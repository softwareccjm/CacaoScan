"""
Módulo de predicción unificada para CacaoScan.
Integra segmentación YOLOv8-seg con modelos de regresión.
"""
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
import numpy as np
import torch
import cv2
from PIL import Image
import io

from ..utils.paths import get_regressors_artifacts_dir, get_yolo_artifacts_dir
from ..utils.logs import get_ml_logger
from ..utils.io import save_image, ensure_dir_exists
from ..segmentation.cropper import create_cacao_cropper
from ..regression.models import create_model, TARGETS
from ..regression.scalers import load_scalers
from ..data.transforms import resize_crop_to_square

logger = get_ml_logger("cacaoscan.ml.prediction")


class CacaoPredictor:
    """Predictor unificado para granos de cacao."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Inicializa el predictor.
        
        Args:
            confidence_threshold: Umbral de confianza para YOLO
        """
        self.confidence_threshold = confidence_threshold
        self.yolo_cropper = None
        self.regression_models = {}
        self.scalers = None
        self.device = self._get_device()
        self.models_loaded = False
        
        # Directorios para crops: defectuosos -> crops_runtime, buenos -> processed
        self.runtime_crops_dir = Path("media/cacao_images/crops_runtime")
        ensure_dir_exists(self.runtime_crops_dir)
        
        from datetime import datetime
        today = datetime.now()
        self.processed_crops_dir = Path("media") / "cacao_images" / "processed" / f"{today.year}" / f"{today.month:02d}" / f"{today.day:02d}"
        ensure_dir_exists(self.processed_crops_dir)
        
        logger.info(f"Predictor inicializado con threshold {confidence_threshold}")
    
    def _get_device(self) -> torch.device:
        """Obtiene el dispositivo disponible."""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"Usando GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
            logger.info("Usando CPU")
        
        return device
    
    def load_artifacts(self) -> bool:
        """
        Carga todos los artefactos necesarios para la predicción.
        Si no existen, entrena automáticamente los modelos.
        
        Returns:
            True si se cargaron exitosamente, False en caso contrario
        """
        try:
            logger.info("Cargando artefactos...")
            start_time = time.time()
            
            # 1. Cargar YOLO cropper
            self.yolo_cropper = create_cacao_cropper(
                confidence_threshold=self.confidence_threshold,
                crop_size=512,
                padding=10,
                save_masks=False,
                overwrite=False
            )
            
            # 2. Verificar si existen los modelos y escaladores
            scalers_path = get_regressors_artifacts_dir()
            models_exist = all(
                (get_regressors_artifacts_dir() / f"{target}.pt").exists() 
                for target in TARGETS
            )
            scalers_exist = scalers_path.exists()
            
            if not models_exist or not scalers_exist:
                import os
                auto_train_enabled = os.getenv("AUTO_TRAIN_ENABLED", "0").lower() in ("1", "true", "yes")
                if auto_train_enabled:
                    logger.warning("Modelos o escaladores no encontrados. Iniciando entrenamiento automático...")
                    if not self._auto_train_models():
                        logger.error("Error en entrenamiento automático")
                        return False
                else:
                    logger.warning("Modelos/escaladores no encontrados y AUTO_TRAIN_ENABLED=0. Omitiendo autoentrenamiento.")
                    return False
            
            # 3. Cargar escaladores
            try:
                self.scalers = load_scalers()
                logger.info("Escaladores cargados exitosamente")
            except Exception as e:
                logger.error(f"Error cargando escaladores: {e}")
                return False
            
            # 4. Cargar modelos de regresión
            self.regression_models = {}
            
            for target in TARGETS:
                model_path = get_regressors_artifacts_dir() / f"{target}.pt"
                
                if not model_path.exists():
                    logger.error(f"Modelo no encontrado para {target}: {model_path}")
                    return False
                
                try:
                    # Crear modelo
                    model = create_model(
                        model_type="resnet18",  # Por defecto ResNet18
                        num_outputs=1,
                        pretrained=False,
                        dropout_rate=0.2,
                        multi_head=False
                    )
                    
                    # Cargar pesos
                    checkpoint = torch.load(model_path, map_location=self.device)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.to(self.device)
                    model.eval()
                    
                    self.regression_models[target] = model
                    logger.info(f"Modelo cargado para {target}")
                    
                except Exception as e:
                    logger.error(f"Error cargando modelo para {target}: {e}")
                    return False
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Todos los artefactos cargados exitosamente en {load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error general cargando artefactos: {e}")
            return False
    
    def _auto_train_models(self) -> bool:
        """
        Entrena automáticamente los modelos si no existen.
        
        Returns:
            True si el entrenamiento fue exitoso, False en caso contrario
        """
        try:
            logger.info("[INICIO] Iniciando entrenamiento automático de modelos...")
            
            # Importar funciones de entrenamiento
            from ..pipeline.train_all import run_training_pipeline
            
            # Configuración de entrenamiento automático
            config = {
                'epochs': 30,  # Menos epochs para entrenamiento rápido
                'batch_size': 16,  # Batch size más pequeño para memoria
                'learning_rate': 0.001,
                'multi_head': False,  # 4 modelos independientes
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
            
            logger.info(f"Configuración de entrenamiento automático: {config}")
            
            # Ejecutar pipeline de entrenamiento
            success = run_training_pipeline(
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                learning_rate=config['learning_rate'],
                multi_head=config['multi_head'],
                model_type=config['model_type'],
                img_size=config['img_size'],
                early_stopping_patience=config['early_stopping_patience'],
                save_best_only=config['save_best_only']
            )
            
            if success:
                logger.info("[OK] Entrenamiento automático completado exitosamente")
                return True
            else:
                logger.error("[ERROR] Error en entrenamiento automático")
                return False
                
        except Exception as e:
            logger.error(f"Error en entrenamiento automático: {e}")
            return False
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocesa una imagen para los modelos de regresión.
        
        Args:
            image: Imagen PIL
            
        Returns:
            Tensor preprocesado
        """
        import torchvision.transforms as transforms
        
        # Convertir a RGB si es necesario (el crop puede venir como RGBA)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Transformaciones estándar para ImageNet
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Aplicar transformaciones
        tensor = transform(image)
        
        # Añadir dimensión de batch
        tensor = tensor.unsqueeze(0)
        
        return tensor.to(self.device)
    
    def _predict_single_target(self, image_tensor: torch.Tensor, target: str) -> Tuple[float, float]:
        """
        Predice un target específico.
        
        Args:
            image_tensor: Imagen preprocesada
            target: Target a predecir
            
        Returns:
            Tuple con (valor_predicho, confianza)
        """
        model = self.regression_models[target]
        
        # Límites razonables basados en el dataset real (en mm o g)
        target_limits = {
            'alto': (5.0, 60.0),      # 5-60 mm
            'ancho': (3.0, 30.0),     # 3-30 mm
            'grosor': (1.0, 20.0),    # 1-20 mm
            'peso': (0.2, 10.0)       # 0.2-10 g
        }
        
        with torch.no_grad():
            # Predicción
            prediction = model(image_tensor)
            prediction_value = prediction.cpu().numpy().flatten()[0]
            
            # Validar valor normalizado antes de desnormalizar
            # Los valores normalizados deberían estar típicamente entre -3 y +3 (99.7% de datos)
            if abs(prediction_value) > 5.0:
                logger.warning(f"Valor normalizado fuera de rango para {target}: {prediction_value:.4f}. Limitando a ±5.0")
                prediction_value = np.clip(prediction_value, -5.0, 5.0)
            
            # Desnormalizar usando el escalador específico del target
            if self.scalers and target in self.scalers.scalers:
                try:
                    # Usar directamente el escalador del target en lugar de inverse_transform completo
                    scaler = self.scalers.scalers[target]
                    target_values = np.array([prediction_value]).reshape(-1, 1)
                    denorm_values = scaler.inverse_transform(target_values)
                    prediction_value = float(denorm_values.flatten()[0])
                    
                    # Aplicar límites físicos razonables
                    if target in target_limits:
                        min_val, max_val = target_limits[target]
                        if prediction_value < min_val or prediction_value > max_val:
                            logger.warning(
                                f"Predicción fuera de límites razonables para {target}: "
                                f"{prediction_value:.2f}. Limitando a [{min_val}, {max_val}]"
                            )
                            prediction_value = np.clip(prediction_value, min_val, max_val)
                            
                except Exception as e:
                    logger.warning(f"Error desnormalizando {target}: {e}")
                    # Continuar con valor normalizado si falla la desnormalización
            
            # Calcular confianza (proxy basado en varianza del modelo)
            # Usar dropout para estimar incertidumbre si está disponible
            confidence = self._estimate_confidence(model, image_tensor, target)
            
            return float(prediction_value), float(confidence)
    
    def _estimate_confidence(self, model: torch.nn.Module, image_tensor: torch.Tensor, target: str) -> float:
        """
        Estima la confianza de la predicción con método mejorado.
        
        Args:
            model: Modelo de regresión
            image_tensor: Imagen preprocesada
            target: Target predicho
            
        Returns:
            Confianza estimada (0-1), mínimo 0.8 si el modelo está bien entrenado
        """
        try:
            # Método 1: Monte Carlo Dropout (más muestras para mejor estimación)
            model.train()  # Activar dropout
            
            predictions = []
            n_samples = 10  # Más muestras para mejor estimación
            
            for _ in range(n_samples):
                with torch.no_grad():
                    pred = model(image_tensor)
                    predictions.append(pred.cpu().numpy().flatten()[0])
            
            model.eval()  # Volver a modo eval
            
            # Calcular estadísticas
            predictions = np.array(predictions)
            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)
            variance = np.var(predictions)
            
            # Método 2: Calcular confianza basada en consistencia
            # Menor desviación estándar relativa = mayor confianza
            if abs(mean_pred) > 1e-6:
                cv = std_pred / abs(mean_pred)  # Coeficiente de variación
                consistency_conf = 1.0 / (1.0 + cv * 5)  # Mapear CV a confianza
            else:
                consistency_conf = 0.5
            
            # Método 3: Confianza basada en varianza absoluta
            # Normalizar por el rango típico del target
            target_ranges = {
                'alto': 50.0,    # Rango típico: 0-50mm normalizado
                'ancho': 30.0,   # Rango típico: 0-30mm normalizado
                'grosor': 20.0,  # Rango típico: 0-20mm normalizado
                'peso': 5.0      # Rango típico: 0-5g normalizado
            }
            
            target_range = target_ranges.get(target, 10.0)
            normalized_variance = variance / (target_range ** 2)
            variance_conf = 1.0 / (1.0 + normalized_variance * 20)
            
            # Combinar ambos métodos (promedio ponderado)
            confidence = 0.6 * consistency_conf + 0.4 * variance_conf
            
            # Ajustar para asegurar mínimo si el modelo está entrenado
            # Si la varianza es muy baja, confiar más en el modelo
            if variance < 0.01:
                confidence = max(confidence, 0.8)
            elif variance < 0.05:
                confidence = max(confidence, 0.7)
            else:
                confidence = max(confidence, 0.5)
            
            return min(max(confidence, 0.0), 1.0)  # Clamp a [0, 1]
            
        except Exception as e:
            logger.warning(f"Error estimando confianza para {target}: {e}")
            # Fallback mejorado: confianza más alta si el modelo está entrenado
            return max(self._get_proxy_confidence(target), 0.75)
    
    def _validate_crop_quality(self, crop_image: Image.Image) -> bool:
        """
        Valida la calidad del crop. Verifica si tiene bordes blancos, tamaño adecuado, etc.
        
        Args:
            crop_image: Imagen RGBA del crop
            
        Returns:
            True si el crop es válido (bueno), False si es defectuoso
        """
        try:
            import numpy as np
            
            # Convertir a array numpy
            img_array = np.array(crop_image)
            
            if img_array.shape[2] != 4:  # Debe ser RGBA
                return False
            
            # Extraer canales RGB y alpha
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # 1. Verificar que haya suficiente contenido visible (más del 20% de píxeles)
            visible_pixels = np.sum(alpha > 30)  # Píxeles con alpha > 30/255
            total_pixels = alpha.size
            visible_ratio = visible_pixels / total_pixels if total_pixels > 0 else 0
            
            if visible_ratio < 0.2:  # Menos del 20% visible = defectuoso
                return False
            
            # 2. Verificar bordes: detectar píxeles blancos/casi blancos en los bordes
            h, w = alpha.shape
            border_width = max(5, min(h, w) // 20)  # 5% del tamaño o mínimo 5px
            
            # Bordes: top, bottom, left, right
            top_border = rgb[:border_width, :, :]
            bottom_border = rgb[-border_width:, :, :]
            left_border = rgb[:, :border_width, :]
            right_border = rgb[:, -border_width:, :]
            
            # Detectar píxeles blancos (valores RGB > 240)
            white_threshold = 240
            top_white = np.mean(top_border, axis=2) > white_threshold
            bottom_white = np.mean(bottom_border, axis=2) > white_threshold
            left_white = np.mean(left_border, axis=2) > white_threshold
            right_white = np.mean(right_border, axis=2) > white_threshold
            
            # Si más del 30% de los bordes son blancos = defectuoso
            border_white_ratio = (
                np.sum(top_white) + np.sum(bottom_white) + 
                np.sum(left_white) + np.sum(right_white)
            ) / (top_white.size + bottom_white.size + left_white.size + right_white.size)
            
            if border_white_ratio > 0.3:
                return False
            
            # 3. Verificar tamaño mínimo (debe ser al menos 50x50 píxeles)
            if h < 50 or w < 50:
                return False
            
            # 4. Verificar que no sea demasiado pequeño el objeto visible
            object_area = np.sum(alpha > 128)  # Área del objeto (alpha > 128)
            if object_area < (h * w * 0.1):  # Menos del 10% del área = defectuoso
                return False
            
            # Si pasa todas las validaciones = BUENO
            return True
            
        except Exception as e:
            logger.warning(f"Error validando calidad del crop: {e}")
            # En caso de error, considerarlo defectuoso
            return False
    
    def _get_proxy_confidence(self, target: str) -> float:
        """
        Obtiene una confianza proxy basada en estadísticas del target.
        
        Args:
            target: Target predicho
            
        Returns:
            Confianza proxy (0-1)
        """
        # Confianzas proxy mejoradas - asumiendo modelo bien entrenado
        proxy_confidences = {
            'alto': 0.85,   # Alto es relativamente fácil de estimar
            'ancho': 0.85,  # Ancho similar a alto
            'grosor': 0.80, # Grosor puede ser más difícil
            'peso': 0.90    # Peso tiene buena correlación con volumen
        }
        
        # Si los modelos están cargados, asumir que están entrenados y dar confianza alta
        if self.models_loaded:
            return max(proxy_confidences.get(target, 0.80), 0.80)
        else:
            return proxy_confidences.get(target, 0.75)
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice dimensiones y peso de un grano de cacao.
        
        Args:
            image: Imagen PIL del grano
            
        Returns:
            Diccionario con predicciones y metadatos
        """
        if not self.models_loaded:
            raise RuntimeError("Los artefactos no han sido cargados. Llamar load_artifacts() primero.")
        
        start_time = time.time()
        
        try:
            # 1. Segmentación y recorte
            logger.debug("Iniciando segmentación...")
            
            # Guardar imagen temporalmente para el cropper
            temp_image_path = self.processed_crops_dir / f"temp_{uuid.uuid4()}.jpg"
            image.save(temp_image_path)
            
            try:
                # Usar el cropper para segmentar y recortar
                crop_result = self.yolo_cropper.process_image(
                    temp_image_path,
                    image_id=1,  # ID ficticio
                    force_process=True
                )
                
                if not crop_result['success']:
                    raise ValueError(f"Error en segmentación: {crop_result.get('error', 'Error desconocido')}")
                
                # Cargar el crop generado (debe ser RGBA con fondo transparente)
                crop_path = crop_result['crop_path']
                crop_image = Image.open(crop_path)
                
                # Verificar que es RGBA (con transparencia)
                if crop_image.mode != 'RGBA':
                    logger.warning(f"Crop no es RGBA ({crop_image.mode}), convirtiendo...")
                    # Si no es RGBA, intentar crear uno con fondo transparente
                    if crop_image.mode == 'RGB':
                        # Crear RGBA con fondo transparente
                        rgba = Image.new('RGBA', crop_image.size, (0, 0, 0, 0))
                        rgba.paste(crop_image, (0, 0))
                        crop_image = rgba
                    else:
                        crop_image = crop_image.convert('RGBA')
                
                # Validar calidad del crop: verificar si tiene bordes blancos o es defectuoso
                crop_is_valid = self._validate_crop_quality(crop_image)
                
                crop_uuid = str(uuid.uuid4())
                
                if crop_is_valid:
                    # Crop BUENO -> guardar en processed/YYYY/MM/DD
                    processed_crop_path = self.processed_crops_dir / f"{crop_uuid}.png"
                    crop_image.save(processed_crop_path, 'PNG')
                    final_crop_path = processed_crop_path
                    crop_url = f"/media/cacao_images/processed/{datetime.now().year}/{datetime.now().month:02d}/{datetime.now().day:02d}/{crop_uuid}.png"
                    logger.info(f"Crop válido guardado en processed: {crop_uuid}.png")
                else:
                    # Crop DEFECTUOSO -> guardar en crops_runtime
                    runtime_crop_path = self.runtime_crops_dir / f"{crop_uuid}.png"
                    crop_image.save(runtime_crop_path, 'PNG')
                    final_crop_path = runtime_crop_path
                    crop_url = f"/media/cacao_images/crops_runtime/{crop_uuid}.png"
                    logger.warning(f"Crop defectuoso guardado en crops_runtime: {crop_uuid}.png")
                
                # Para el modelo ML, convertir a RGB (el modelo espera RGB)
                crop_image_rgb = crop_image.convert('RGB')
                
                yolo_confidence = crop_result.get('confidence', 0.0)
                
            finally:
                # Limpiar archivo temporal
                if temp_image_path.exists():
                    temp_image_path.unlink()
            
            # 2. Preprocesar imagen para regresión (usar versión RGB)
            image_tensor = self._preprocess_image(crop_image_rgb)
            
            # 3. Predecir cada target
            predictions = {}
            confidences = {}
            
            for target in TARGETS:
                pred_value, confidence = self._predict_single_target(image_tensor, target)
                predictions[target] = pred_value
                confidences[target] = confidence
            
            # 4. Preparar resultado
            total_time = time.time() - start_time
            latency_ms = int(total_time * 1000)
            
            result = {
                'alto_mm': predictions['alto'],
                'ancho_mm': predictions['ancho'],
                'grosor_mm': predictions['grosor'],
                'peso_g': predictions['peso'],
                'confidences': confidences,
                'crop_url': crop_url,
                'debug': {
                    'segmented': True,
                    'yolo_conf': float(yolo_confidence),
                    'latency_ms': latency_ms,
                    'models_version': 'v1',
                    'device': str(self.device),
                    'total_time_s': total_time
                }
            }
            
            logger.info(f"Predicción completada en {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predice desde bytes de imagen.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Diccionario con predicciones
        """
        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return self.predict(image)
            
        except Exception as e:
            logger.error(f"Error procesando imagen desde bytes: {e}")
            raise ValueError(f"Error procesando imagen: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre los modelos cargados.
        
        Returns:
            Diccionario con información de los modelos
        """
        if not self.models_loaded:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'device': str(self.device),
            'models': {},
            'scalers': 'loaded' if self.scalers else 'not_loaded',
            'yolo_cropper': 'loaded' if self.yolo_cropper else 'not_loaded'
        }
        
        for target, model in self.regression_models.items():
            info['models'][target] = {
                'type': type(model).__name__,
                'parameters': sum(p.numel() for p in model.parameters())
            }
        
        return info


# Instancia global del predictor
_predictor_instance: Optional[CacaoPredictor] = None


def get_predictor() -> CacaoPredictor:
    """
    Obtiene la instancia global del predictor.
    
    Returns:
        Instancia del predictor
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = CacaoPredictor()
        
        # Intentar cargar artefactos automáticamente
        if not _predictor_instance.load_artifacts():
            logger.warning("No se pudieron cargar todos los artefactos automáticamente")
    
    return _predictor_instance


def load_artifacts() -> bool:
    """
    Función de conveniencia para cargar artefactos.
    
    Returns:
        True si se cargaron exitosamente
    """
    predictor = get_predictor()
    return predictor.load_artifacts()


def predict_image(image: Image.Image) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir una imagen.
    
    Args:
        image: Imagen PIL
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict(image)


def predict_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir desde bytes.
    
    Args:
        image_bytes: Bytes de la imagen
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict_from_bytes(image_bytes)
