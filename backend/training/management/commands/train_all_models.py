"""
Comando Django para entrenar todos los modelos: YOLO + Regresión.
ACTUALIZADO:
- Se eliminó la lógica de Celery para una ejecución directa y síncrona.
- Se agregaron los argumentos del "Flujo Mejorado" para el entrenamiento
  del modelo de regresión híbrido.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import time
import sys
from pathlib import Path

# Asegurar que el path del proyecto esté configurado para ml
project_root = Path(__file__).resolve().parents[4] # Sube 4 niveles (commands/management/training/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = None


class Command(BaseCommand):
    help = 'Entrena todos los modelos (YOLO + Regresión) de forma directa y síncrona.'
    
    def add_arguments(self, parser):
        # --- Argumentos YOLO ---
        parser.add_argument(
            '--yolo-dataset-size',
            type=int,
            default=150,
            help='Número de imágenes para dataset YOLO (default: 150)'
        )
        parser.add_argument(
            '--yolo-epochs',
            type=int,
            default=100,
            help='Número de épocas para YOLO (default: 100)'
        )
        parser.add_argument(
            '--yolo-batch-size',
            type=int,
            default=16,
            help='Tamaño de batch para YOLO (default: 16)'
        )
        parser.add_argument(
            '--yolo-model-name',
            type=str,
            default='yolov8s-seg',
            choices=['yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg', 'yolov8l-seg', 'yolov8x-seg'],
            help='Modelo base YOLO (default: yolov8s-seg)'
        )
        
        # --- Argumentos Regresión (Flujo Mejorado) ---
        parser.add_argument(
            '--regression-epochs',
            type=int,
            default=150,
            help='Número de épocas para regresión (default: 150)'
        )
        parser.add_argument(
            '--regression-batch-size',
            type=int,
            default=16,
            help='Tamaño de batch para regresión (default: 16)'
        )
        parser.add_argument(
            '--regression-learning-rate',
            type=float,
            default=0.001,
            help='Learning rate para regresión (default: 0.001)'
        )
        parser.add_argument(
            '--regression-model-type',
            type=str,
            default='hybrid', # Default al nuevo modelo híbrido
            choices=['resnet18', 'convnext_tiny', 'hybrid'],
            help='Tipo de modelo de regresión (default: hybrid)'
        )
        parser.add_argument(
            '--regression-hybrid',
            action='store_true',
            default=True, # Default a True
            help='(Recomendado) Usar modelo híbrido (equivale a --regression-model-type hybrid)'
        )
        parser.add_argument(
            '--regression-use-pixel-features',
            action='store_true',
            default=True, # Default a True
            help='(Recomendado) Usar features de píxeles si pixel_calibration.json existe'
        )

    
    def handle(self, *args, **options):
        """Maneja la ejecución del comando."""
        global logger
        from ml.utils.logs import get_ml_logger
        logger = get_ml_logger("cacaoscan.ml.commands")
        
        start_time = time.time()
        
        # Determinar si es híbrido
        is_hybrid = options['regression_hybrid'] or options['regression_model_type'] == 'hybrid'

        # Preparar configuraciones
        yolo_config = {
            'dataset_size': options['yolo_dataset_size'],
            'epochs': options['yolo_epochs'],
            'batch_size': options['yolo_batch_size'],
            'model_name': options['yolo_model_name']
        }
        
        regression_config = {
            'epochs': options['regression_epochs'],
            'batch_size': options['regression_batch_size'],
            'learning_rate': options['regression_learning_rate'],
            'model_type': 'hybrid' if is_hybrid else options['regression_model_type'],
            'multi_head': is_hybrid, # Modelo híbrido es multi-head
            'hybrid': is_hybrid,
            'use_pixel_features': options['regression_use_pixel_features'] and is_hybrid,
            'img_size': 224,
            'early_stopping_patience': 25,
            'save_best_only': True
        }
        
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando entrenamiento completo: YOLO + Modelos de Regresión"
            )
        )
        self.stdout.write(f"Configuración YOLO: {json.dumps(yolo_config, indent=2)}")
        self.stdout.write(f"Configuración Regresión: {json.dumps(regression_config, indent=2)}")
        
        # --- LÓGICA DE CELERY ELIMINADA ---
        # Se ejecuta directamente (síncrono)
        
        self.stdout.write("Ejecutando entrenamiento directamente (síncrono)...")
        self.stdout.write("Esto puede tomar varias horas. Por favor, sea paciente...")
        
        try:
            # Importar funciones directamente
            from ml.segmentation.train_yolo import train_cacao_yolo_model
            from ml.pipeline.train_all import run_training_pipeline
            
            results = {
                'yolo': None,
                'regression': None,
                'status': 'running'
            }
            
            # Paso 1: Entrenar YOLO
            self.stdout.write("\n" + "="*60)
            self.stdout.write("PASO 1/2: ENTRENANDO MODELO YOLO")
            self.stdout.write("="*60)
            try:
                self.stdout.write(f"Configuración YOLO: {json.dumps(yolo_config, indent=2)}")
                self.stdout.write("Iniciando entrenamiento YOLO...")
                self.stdout.write("(Esto puede tomar 30-60 minutos)")
                
                yolo_result = train_cacao_yolo_model(
                    dataset_size=yolo_config.get('dataset_size', 150),
                    epochs=yolo_config.get('epochs', 100),
                    batch_size=yolo_config.get('batch_size', 16),
                    model_name=yolo_config.get('model_name', 'yolov8s-seg')
                )
                
                if yolo_result and yolo_result.get('success', False):
                    results['yolo'] = {
                        'status': 'completed',
                        'message': 'Entrenamiento YOLO completado exitosamente',
                        'best_model_path': yolo_result.get('best_model_path')
                    }
                    self.stdout.write(
                        self.style.SUCCESS("✓ Entrenamiento YOLO completado")
                    )
                    self.stdout.write(f"Modelo guardado en: {yolo_result.get('best_model_path')}")
                else:
                    results['yolo'] = {
                        'status': 'failed',
                        'message': 'El entrenamiento YOLO falló',
                        'error': yolo_result.get('error', 'Error desconocido')
                    }
                    self.stdout.write(
                        self.style.ERROR(f"✗ Entrenamiento YOLO falló: {yolo_result.get('error')}")
                    )
            except Exception as e:
                import traceback
                logger.error(f"Error en entrenamiento YOLO: {e}", exc_info=True)
                error_traceback = traceback.format_exc()
                
                results['yolo'] = {
                    'status': 'failed',
                    'error': str(e),
                    'traceback': error_traceback
                }
                
                self.stdout.write(self.style.ERROR(f"\n✗ ERROR EN ENTRENAMIENTO YOLO: {str(e)}"))
                self.stdout.write(error_traceback)
            
            # Paso 2: Entrenar modelos de regresión
            self.stdout.write("\n" + "="*60)
            self.stdout.write("PASO 2/2: ENTRENANDO MODELOS DE REGRESIÓN")
            self.stdout.write("="*60)
            try:
                self.stdout.write(f"Configuración Regresión: {json.dumps(regression_config, indent=2)}")
                self.stdout.write("Iniciando entrenamiento de regresión...")
                self.stdout.write("(Esto puede tomar 1-3 horas)")
                
                # Llamar a run_training_pipeline con la configuración mejorada
                regression_success = run_training_pipeline(
                    epochs=regression_config.get('epochs', 150),
                    batch_size=regression_config.get('batch_size', 16),
                    learning_rate=regression_config.get('learning_rate', 0.001),
                    multi_head=regression_config.get('multi_head', False),
                    model_type=regression_config.get('model_type', 'resnet18'),
                    img_size=regression_config.get('img_size', 224),
                    early_stopping_patience=regression_config.get('early_stopping_patience', 25),
                    save_best_only=regression_config.get('save_best_only', True),
                    # Pasar los nuevos flags del Flujo Mejorado
                    hybrid=regression_config.get('hybrid', False),
                    use_pixel_features=regression_config.get('use_pixel_features', False)
                )
                
                if regression_success:
                    results['regression'] = {
                        'status': 'completed',
                        'message': 'Entrenamiento de regresión completado exitosamente'
                    }
                    self.stdout.write(
                        self.style.SUCCESS("✓ Entrenamiento de regresión completado")
                    )
                else:
                    results['regression'] = {
                        'status': 'failed',
                        'message': 'El entrenamiento de regresión falló'
                    }
                    self.stdout.write(
                        self.style.ERROR("✗ Entrenamiento de regresión falló")
                    )
            except Exception as e:
                import traceback
                logger.error(f"Error en entrenamiento de regresión: {e}", exc_info=True)
                error_traceback = traceback.format_exc()
                
                results['regression'] = {
                    'status': 'failed',
                    'error': str(e),
                    'traceback': error_traceback
                }
                
                self.stdout.write(self.style.ERROR(f"\n✗ ERROR EN ENTRENAMIENTO DE REGRESIÓN: {str(e)}"))
                self.stdout.write(error_traceback)
            
            # Determinar estado final
            yolo_ok = results['yolo'] and results['yolo'].get('status') == 'completed'
            regression_ok = results['regression'] and results['regression'].get('status') == 'completed'
            
            if yolo_ok and regression_ok:
                results['status'] = 'completed'
                results['message'] = 'Entrenamiento completo exitoso'
            elif yolo_ok or regression_ok:
                results['status'] = 'partial'
                results['message'] = 'Entrenamiento completado parcialmente'
            else:
                results['status'] = 'failed'
                results['message'] = 'Entrenamiento completo falló'
            
            # Mostrar resultados
            self._display_results(results, start_time)
            
        except Exception as e:
            import traceback
            logger.error(f"Error en entrenamiento completo: {e}", exc_info=True)
            error_traceback = traceback.format_exc()
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.ERROR("ERROR FATAL EN ENTRENAMIENTO"))
            self.stdout.write("="*60)
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            self.stdout.write(error_traceback)
            self.stdout.write("="*60)
            
            raise CommandError(f"Error en entrenamiento: {e}\n\nTraceback completo:\n{error_traceback}")
    
    def _display_results(self, results: dict, start_time: float) -> None:
        """Muestra los resultados del entrenamiento."""
        end_time = time.time()
        total_time = end_time - start_time
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("RESULTADOS DEL ENTRENAMIENTO COMPLETO")
        self.stdout.write("="*60)
        
        # Resultados YOLO
        self.stdout.write("\n--- Entrenamiento YOLO ---")
        if results.get('yolo'):
            yolo_result = results['yolo']
            status = yolo_result.get('status', 'unknown')
            if status == 'completed':
                self.stdout.write(self.style.SUCCESS(f"✓ YOLO: {yolo_result.get('message', 'Completado')}"))
                if yolo_result.get('best_model_path'):
                    self.stdout.write(f"  Modelo guardado en: {yolo_result['best_model_path']}")
            else:
                self.stdout.write(self.style.ERROR(f"✗ YOLO: {yolo_result.get('message', 'Falló')}"))
                if yolo_result.get('error'):
                    self.stdout.write(self.style.ERROR(f"  Error: {yolo_result['error']}"))
        else:
            self.stdout.write(self.style.WARNING("⊘ YOLO: No se ejecutó"))
        
        # Resultados Regresión
        self.stdout.write("\n--- Entrenamiento Regresión ---")
        if results.get('regression'):
            regression_result = results['regression']
            status = regression_result.get('status', 'unknown')
            if status == 'completed':
                self.stdout.write(self.style.SUCCESS(f"✓ Regresión: {regression_result.get('message', 'Completado')}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Regresión: {regression_result.get('message', 'Falló')}"))
                if regression_result.get('error'):
                    self.stdout.write(self.style.ERROR(f"  Error: {regression_result['error']}"))
        else:
            self.stdout.write(self.style.WARNING("⊘ Regresión: No se ejecutó"))
        
        # Estado final
        self.stdout.write("\n--- Estado Final ---")
        final_status = results.get('status', 'unknown')
        if final_status == 'completed':
            self.stdout.write(self.style.SUCCESS(f"✓ {results.get('message', 'Entrenamiento completo exitoso')}"))
        elif final_status == 'partial':
            self.stdout.write(self.style.WARNING(f"⚠ {results.get('message', 'Entrenamiento completado parcialmente')}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ {results.get('message', 'Entrenamiento falló')}"))
            if results.get('error'):
                self.stdout.write(f"  Error: {results['error']}")
        
        self.stdout.write(f"\nTiempo total: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
        self.stdout.write("="*60)