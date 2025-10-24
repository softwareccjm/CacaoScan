"""
Servicio de análisis para CacaoScan.
Maneja el procesamiento de imágenes de granos de cacao y predicciones.
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.base import ContentFile
from PIL import Image
import io

from .base import BaseService, ServiceError, ValidationServiceError, PermissionServiceError, NotFoundServiceError, FileService

logger = logging.getLogger("cacaoscan.services.analysis")


class AnalysisService(BaseService):
    """
    Servicio para manejo de análisis de granos de cacao.
    """
    
    def __init__(self):
        super().__init__()
        self.file_service = FileService()
    
    def process_image_analysis(self, user: User, image_file, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa una imagen de grano de cacao y realiza análisis completo.
        
        Args:
            user: Usuario que realiza el análisis
            image_file: Archivo de imagen a procesar
            metadata: Metadatos adicionales (opcional)
            
        Returns:
            Diccionario con resultados del análisis
            
        Raises:
            ValidationServiceError: Si la imagen no es válida
            ServiceError: Si hay error en el procesamiento
        """
        try:
            start_time = time.time()
            
            # Validar archivo de imagen
            validation_result = self.file_service.validate_image_file(image_file)
            self.log_info(f"Imagen validada: {validation_result['size_mb']:.2f}MB", user_id=user.id)
            
            # Guardar imagen en el sistema
            cacao_image, image_saved = self._save_uploaded_image(user, image_file, metadata)
            
            # Cargar imagen para procesamiento
            image_data = image_file.read()
            image_file.seek(0)  # Resetear posición
            image = Image.open(io.BytesIO(image_data))
            
            # Realizar predicción
            prediction_result = self._perform_prediction(image)
            prediction_time_ms = int((time.time() - start_time) * 1000)
            
            # Guardar predicción en BD
            cacao_prediction, prediction_saved = self._save_prediction(
                cacao_image, prediction_result, prediction_time_ms
            )
            
            # Enviar notificación por email
            self._send_analysis_notification(user, prediction_result, cacao_prediction)
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="analysis_completed",
                resource_type="cacao_prediction",
                resource_id=cacao_prediction.id if cacao_prediction else None,
                details={
                    'image_id': cacao_image.id if cacao_image else None,
                    'processing_time_ms': prediction_time_ms,
                    'confidence': prediction_result.get('average_confidence', 0)
                }
            )
            
            # Preparar respuesta
            response_data = {
                'alto_mm': prediction_result.get('alto_mm', 0),
                'ancho_mm': prediction_result.get('ancho_mm', 0),
                'grosor_mm': prediction_result.get('grosor_mm', 0),
                'peso_g': prediction_result.get('peso_g', 0),
                'confidences': prediction_result.get('confidences', {}),
                'crop_url': prediction_result.get('crop_url', ''),
                'debug': prediction_result.get('debug', {}),
                'image_id': cacao_image.id if cacao_image else None,
                'prediction_id': cacao_prediction.id if cacao_prediction else None,
                'saved_to_database': image_saved and prediction_saved,
                'processing_time_ms': prediction_time_ms
            }
            
            self.log_info(f"Análisis completado en {prediction_time_ms}ms", 
                         user_id=user.id, 
                         prediction_id=cacao_prediction.id if cacao_prediction else None)
            
            return response_data
            
        except ValidationServiceError:
            raise
        except Exception as e:
            self.log_error(f"Error en análisis de imagen: {e}")
            raise ServiceError("Error interno en análisis", "analysis_error")
    
    def _save_uploaded_image(self, user: User, image_file, metadata: Dict[str, Any] = None) -> Tuple[Any, bool]:
        """
        Guarda la imagen subida en el sistema de archivos y BD.
        
        Args:
            user: Usuario propietario
            image_file: Archivo de imagen
            metadata: Metadatos adicionales
            
        Returns:
            Tupla con (cacao_image_obj, success)
        """
        try:
            from ..models import CacaoImage
            
            # Generar nombre único para el archivo
            unique_filename = self.file_service.generate_unique_filename(
                image_file.name, 
                f"user_{user.id}"
            )
            
            # Crear objeto CacaoImage
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=unique_filename,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False,
                metadata=metadata or {}
            )
            
            # Guardar en BD
            cacao_image.save()
            
            self.log_info(f"Imagen guardada con ID {cacao_image.id}", user_id=user.id)
            return cacao_image, True
            
        except Exception as e:
            self.log_error(f"Error guardando imagen: {e}")
            return None, False
    
    def _perform_prediction(self, image: Image.Image) -> Dict[str, Any]:
        """
        Realiza la predicción de dimensiones y peso del grano.
        
        Args:
            image: Imagen PIL a procesar
            
        Returns:
            Diccionario con resultados de la predicción
            
        Raises:
            ServiceError: Si hay error en la predicción
        """
        try:
            from ml.prediction.predict import get_predictor, load_artifacts
            
            # Obtener predictor
            predictor = get_predictor()
            
            if not predictor.models_loaded:
                # Intentar cargar modelos automáticamente
                self.log_info("Modelos no cargados. Intentando carga automática...")
                success = load_artifacts()
                
                if not success:
                    raise ServiceError("Modelos no disponibles", "models_not_available")
                
                # Reintentar obtener predictor
                predictor = get_predictor()
                
                if not predictor.models_loaded:
                    raise ServiceError("Error cargando modelos", "model_loading_error")
            
            # Realizar predicción
            prediction_start = time.time()
            result = predictor.predict(image)
            prediction_time_ms = int((time.time() - prediction_start) * 1000)
            
            # Agregar información de tiempo de procesamiento
            result['processing_time_ms'] = prediction_time_ms
            
            self.log_info(f"Predicción completada en {prediction_time_ms}ms")
            
            return result
            
        except Exception as e:
            self.log_error(f"Error en predicción: {e}")
            raise ServiceError(f"Error en predicción: {str(e)}", "prediction_error")
    
    def _save_prediction(self, cacao_image, prediction_result: Dict[str, Any], 
                        processing_time_ms: int) -> Tuple[Any, bool]:
        """
        Guarda los resultados de la predicción en BD.
        
        Args:
            cacao_image: Objeto de imagen asociada
            prediction_result: Resultados de la predicción
            processing_time_ms: Tiempo de procesamiento
            
        Returns:
            Tupla con (cacao_prediction_obj, success)
        """
        try:
            from ..models import CacaoPrediction
            
            # Calcular confianza promedio
            confidences = prediction_result.get('confidences', {})
            avg_confidence = sum(confidences.values()) / len(confidences) if confidences else 0
            
            # Crear objeto CacaoPrediction
            cacao_prediction = CacaoPrediction(
                image=cacao_image,
                user=cacao_image.user,
                alto_mm=prediction_result.get('alto_mm', 0),
                ancho_mm=prediction_result.get('ancho_mm', 0),
                grosor_mm=prediction_result.get('grosor_mm', 0),
                peso_g=prediction_result.get('peso_g', 0),
                confidence_alto=confidences.get('alto', 0),
                confidence_ancho=confidences.get('ancho', 0),
                confidence_grosor=confidences.get('grosor', 0),
                confidence_peso=confidences.get('peso', 0),
                average_confidence=avg_confidence,
                processing_time_ms=processing_time_ms,
                model_version=prediction_result.get('debug', {}).get('model_version', 'v1.0'),
                crop_url=prediction_result.get('crop_url', ''),
                metadata=prediction_result.get('debug', {})
            )
            
            # Guardar en BD
            cacao_prediction.save()
            
            # Marcar imagen como procesada
            cacao_image.processed = True
            cacao_image.save()
            
            self.log_info(f"Predicción guardada con ID {cacao_prediction.id}")
            return cacao_prediction, True
            
        except Exception as e:
            self.log_error(f"Error guardando predicción: {e}")
            return None, False
    
    def _send_analysis_notification(self, user: User, prediction_result: Dict[str, Any], 
                                  cacao_prediction) -> None:
        """
        Envía notificación por email del análisis completado.
        
        Args:
            user: Usuario destinatario
            prediction_result: Resultados de la predicción
            cacao_prediction: Objeto de predicción guardado
        """
        try:
            # Determinar nivel de confianza
            avg_confidence = prediction_result.get('average_confidence', 0)
            if avg_confidence >= 0.8:
                confidence_level = 'high'
            elif avg_confidence >= 0.6:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'
            
            email_context = {
                'analysis_id': cacao_prediction.id if cacao_prediction else 'N/A',
                'confidence': round(avg_confidence * 100, 1),
                'confidence_level': confidence_level,
                'alto_mm': prediction_result.get('alto_mm', 0),
                'ancho_mm': prediction_result.get('ancho_mm', 0),
                'grosor_mm': prediction_result.get('grosor_mm', 0),
                'peso_g': prediction_result.get('peso_g', 0),
                'confidence_alto': round(prediction_result.get('confidences', {}).get('alto', 0) * 100, 1),
                'confidence_ancho': round(prediction_result.get('confidences', {}).get('ancho', 0) * 100, 1),
                'confidence_grosor': round(prediction_result.get('confidences', {}).get('grosor', 0) * 100, 1),
                'confidence_peso': round(prediction_result.get('confidences', {}).get('peso', 0) * 100, 1),
                'processing_time_ms': prediction_result.get('processing_time_ms', 0),
                'model_version': prediction_result.get('debug', {}).get('model_version', 'v1.0'),
                'analysis_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                'crop_url': prediction_result.get('crop_url', ''),
                'defects_detected': []  # TODO: Implementar detección de defectos
            }
            
            email_result = self.send_email_notification(
                user=user,
                notification_type='analysis_complete',
                context=email_context
            )
            
            if email_result['success']:
                self.log_info(f"Email de análisis enviado a {user.email}", user_id=user.id)
            else:
                self.log_warning(f"Error enviando email: {email_result.get('error')}", user_id=user.id)
                
        except Exception as e:
            self.log_error(f"Error enviando notificación de análisis: {e}")
    
    def get_analysis_history(self, user: User, page: int = 1, page_size: int = 20, 
                            filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtiene el historial de análisis de un usuario.
        
        Args:
            user: Usuario del cual obtener historial
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            Diccionario con historial paginado
        """
        try:
            from ..models import CacaoPrediction
            from .base import PaginationService
            
            # Construir queryset base
            queryset = CacaoPrediction.objects.filter(user=user).select_related('image').order_by('-created_at')
            
            # Aplicar filtros
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
                if 'min_confidence' in filters:
                    queryset = queryset.filter(average_confidence__gte=filters['min_confidence'])
                if 'max_confidence' in filters:
                    queryset = queryset.filter(average_confidence__lte=filters['max_confidence'])
            
            # Paginar resultados
            paginated_data = PaginationService.paginate_queryset(queryset, page, page_size)
            
            # Serializar resultados
            results = []
            for prediction in paginated_data['results']:
                results.append({
                    'id': prediction.id,
                    'image_id': prediction.image.id,
                    'alto_mm': prediction.alto_mm,
                    'ancho_mm': prediction.ancho_mm,
                    'grosor_mm': prediction.grosor_mm,
                    'peso_g': prediction.peso_g,
                    'average_confidence': prediction.average_confidence,
                    'processing_time_ms': prediction.processing_time_ms,
                    'model_version': prediction.model_version,
                    'crop_url': prediction.crop_url,
                    'created_at': prediction.created_at.isoformat()
                })
            
            return {
                'results': results,
                'pagination': paginated_data['pagination']
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo historial de análisis: {e}")
            raise ServiceError("Error interno obteniendo historial", "history_error")
    
    def get_analysis_statistics(self, user: User, date_from: str = None, 
                               date_to: str = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de análisis de un usuario.
        
        Args:
            user: Usuario del cual obtener estadísticas
            date_from: Fecha de inicio (opcional)
            date_to: Fecha de fin (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            from ..models import CacaoPrediction
            from django.db.models import Avg, Min, Max, Count, StdDev
            
            # Construir queryset base
            queryset = CacaoPrediction.objects.filter(user=user)
            
            # Aplicar filtros de fecha
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            
            # Calcular estadísticas
            stats = queryset.aggregate(
                total_analyses=Count('id'),
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_confidence=Avg('average_confidence'),
                min_confidence=Min('average_confidence'),
                max_confidence=Max('average_confidence'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            # Calcular distribución por confianza
            high_confidence = queryset.filter(average_confidence__gte=0.8).count()
            medium_confidence = queryset.filter(average_confidence__gte=0.6, average_confidence__lt=0.8).count()
            low_confidence = queryset.filter(average_confidence__lt=0.6).count()
            
            return {
                'total_analyses': stats['total_analyses'] or 0,
                'average_dimensions': {
                    'alto_mm': round(float(stats['avg_alto'] or 0), 2),
                    'ancho_mm': round(float(stats['avg_ancho'] or 0), 2),
                    'grosor_mm': round(float(stats['avg_grosor'] or 0), 2),
                    'peso_g': round(float(stats['avg_peso'] or 0), 2)
                },
                'confidence_stats': {
                    'average': round(float(stats['avg_confidence'] or 0), 3),
                    'minimum': round(float(stats['min_confidence'] or 0), 3),
                    'maximum': round(float(stats['max_confidence'] or 0), 3),
                    'distribution': {
                        'high': high_confidence,
                        'medium': medium_confidence,
                        'low': low_confidence
                    }
                },
                'performance_stats': {
                    'average_processing_time_ms': round(float(stats['avg_processing_time'] or 0), 0)
                }
            }
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {e}")
            raise ServiceError("Error interno obteniendo estadísticas", "stats_error")
    
    def delete_analysis(self, user: User, analysis_id: int) -> bool:
        """
        Elimina un análisis específico.
        
        Args:
            user: Usuario que solicita la eliminación
            analysis_id: ID del análisis a eliminar
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundServiceError: Si el análisis no existe
            PermissionServiceError: Si el usuario no tiene permisos
        """
        try:
            from ..models import CacaoPrediction
            
            # Obtener análisis
            try:
                analysis = CacaoPrediction.objects.get(id=analysis_id)
            except CacaoPrediction.DoesNotExist:
                raise NotFoundServiceError(f"Análisis con ID {analysis_id} no encontrado", "analysis_not_found")
            
            # Verificar permisos
            if analysis.user != user and not user.is_superuser:
                raise PermissionServiceError("No tienes permisos para eliminar este análisis", "no_permission")
            
            with transaction.atomic():
                # Eliminar análisis
                analysis.delete()
                
                # Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action="analysis_deleted",
                    resource_type="cacao_prediction",
                    resource_id=analysis_id
                )
                
                self.log_info(f"Análisis eliminado: {analysis_id}", user_id=user.id)
                
                return True
                
        except (NotFoundServiceError, PermissionServiceError):
            raise
        except Exception as e:
            self.log_error(f"Error eliminando análisis: {e}")
            raise ServiceError("Error interno eliminando análisis", "delete_error")
