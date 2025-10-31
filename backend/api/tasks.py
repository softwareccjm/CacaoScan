"""
Tareas asíncronas de Celery para CacaoScan.
"""
import logging
from pathlib import Path
from celery import shared_task
from django.utils import timezone
from api.models import TrainingJob
from ml.pipeline.train_all import run_training_pipeline
from ml.utils.paths import get_datasets_dir

logger = logging.getLogger("cacaoscan.api.tasks")


@shared_task(bind=True, name='api.tasks.train_model')
def train_model_task(self, job_id: str, config: dict):
    """
    Tarea asíncrona para entrenar un modelo ML.
    
    Args:
        job_id: ID del TrainingJob
        config: Configuración del entrenamiento
    
    Returns:
        dict: Resultado del entrenamiento
    """
    try:
        job = TrainingJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        logger.info(f"Iniciando entrenamiento para job {job_id}")
        job.update_progress(5, "Inicializando pipeline...")
        
        # Asegurar que se use dataset_cacao.clean.csv
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            error_msg = f"Dataset limpio no encontrado: {clean_csv_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Usando dataset: {clean_csv_path}")
        job.update_progress(10, f"Cargando dataset: {clean_csv_path.name}")
        
        # Ejecutar entrenamiento con configuración mejorada para alta confianza
        success = run_training_pipeline(
            epochs=config.get('epochs', 150),  # Aumentado de 30 a 150 para mejor aprendizaje
            batch_size=config.get('batch_size', 16),
            learning_rate=config.get('learning_rate', 0.001),
            multi_head=config.get('multi_head', False),
            model_type=config.get('model_type', 'resnet18'),
            img_size=config.get('img_size', 224),
            early_stopping_patience=config.get('early_stopping_patience', 25),  # Más patience
            save_best_only=config.get('save_best_only', True)
        )
        
        if success:
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.progress_percentage = 100.0
            job.logs += "\n[FINALIZADO] Entrenamiento completado exitosamente"
            job.save()
            
            logger.info(f"Entrenamiento completado para job {job_id}")
            return {
                'status': 'completed',
                'job_id': job_id,
                'message': 'Entrenamiento completado exitosamente'
            }
        else:
            raise Exception("El entrenamiento falló")
            
    except TrainingJob.DoesNotExist:
        logger.error(f"TrainingJob {job_id} no encontrado")
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': 'Job no encontrado'
        }
    except Exception as e:
        logger.error(f"Error en entrenamiento para job {job_id}: {e}")
        
        try:
            job = TrainingJob.objects.get(job_id=job_id)
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.error_message = str(e)
            job.logs += f"\n[ERROR] {str(e)}"
            job.save()
        except TrainingJob.DoesNotExist:
            pass
        
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(e)
        }

