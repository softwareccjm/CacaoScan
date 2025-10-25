#!/usr/bin/env python3
"""
Script de prueba para verificar la persistencia de métricas ML.
"""
import os
import sys
from pathlib import Path
import logging

# Configurar Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

from api.models import ModelMetrics, TrainingJob, User
from ml.regression.train import create_training_job, update_training_job_metrics
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_model_metrics_creation():
    """Prueba la creación de métricas de modelo."""
    logger.info("🧪 Probando creación de métricas de modelo...")
    
    try:
        # Obtener usuario por defecto
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        
        if not user:
            logger.error("❌ No se encontró ningún usuario en la base de datos")
            return False
        
        # Crear métricas de prueba
        model_metrics = ModelMetrics.objects.create(
            model_name="test_regression_model",
            model_type='regression',
            target='alto',
            version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            created_by=user,
            metric_type='validation',
            
            # Métricas principales
            mae=0.1234,
            mse=0.0156,
            rmse=0.1250,
            r2_score=0.8756,
            mape=5.67,
            
            # Métricas adicionales
            additional_metrics={
                'final_train_loss': 0.0123,
                'final_val_loss': 0.0156,
                'epochs_completed': 45,
                'early_stopping_triggered': True,
                'best_val_loss': 0.0145
            },
            
            # Información del dataset
            dataset_size=1000,
            train_size=700,
            validation_size=150,
            test_size=150,
            
            # Configuración del modelo
            epochs=50,
            batch_size=32,
            learning_rate=1e-4,
            
            # Parámetros específicos del modelo
            model_params={
                'model_type': 'resnet18',
                'pretrained': True,
                'dropout_rate': 0.2,
                'weight_decay': 1e-4,
                'early_stopping_patience': 10,
                'best_val_loss': 0.0145,
            },
            
            # Información de rendimiento
            training_time_seconds=1800,  # 30 minutos
            inference_time_ms=15.5,
            
            # Notas
            notes="Modelo de prueba para verificar persistencia de métricas",
            is_best_model=True,
            is_production_model=False
        )
        
        logger.info(f"✅ Métricas creadas exitosamente con ID: {model_metrics.id}")
        
        # Verificar propiedades calculadas
        logger.info(f"📊 Precisión como porcentaje: {model_metrics.accuracy_percentage}%")
        logger.info(f"⏱️ Tiempo de entrenamiento: {model_metrics.training_time_formatted}")
        
        # Verificar resumen de rendimiento
        performance_summary = model_metrics.performance_summary
        logger.info(f"📈 Resumen de rendimiento: {json.dumps(performance_summary, indent=2)}")
        
        # Verificar resumen del dataset
        dataset_summary = model_metrics.dataset_summary
        logger.info(f"📊 Resumen del dataset: {json.dumps(dataset_summary, indent=2)}")
        
        # Verificar resumen del modelo
        model_summary = model_metrics.model_summary
        logger.info(f"🤖 Resumen del modelo: {json.dumps(model_summary, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando métricas: {e}")
        return False


def test_training_job_creation():
    """Prueba la creación de TrainingJob."""
    logger.info("🧪 Probando creación de TrainingJob...")
    
    try:
        # Configuración de prueba
        config = {
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 1e-4,
            'model_type': 'resnet18',
            'pretrained': True,
            'dropout_rate': 0.2,
            'weight_decay': 1e-4,
            'early_stopping_patience': 10
        }
        
        # Crear TrainingJob
        training_job = create_training_job(
            job_type='regression',
            model_name='test_model',
            dataset_size=1000,
            config=config
        )
        
        if not training_job:
            logger.error("❌ No se pudo crear TrainingJob")
            return False
        
        logger.info(f"✅ TrainingJob creado con ID: {training_job.job_id}")
        
        # Simular métricas de entrenamiento
        metrics = {
            'final_train_loss': 0.0123,
            'final_val_loss': 0.0156,
            'final_val_mae': 0.1234,
            'final_val_rmse': 0.1250,
            'final_val_r2': 0.8756,
            'epochs_completed': 45,
            'early_stopping_triggered': True
        }
        
        # Actualizar TrainingJob con métricas
        update_training_job_metrics(
            training_job=training_job,
            metrics=metrics,
            model_path="/path/to/test/model.pt"
        )
        
        # Verificar que se actualizó correctamente
        training_job.refresh_from_db()
        logger.info(f"✅ TrainingJob actualizado - Estado: {training_job.status}")
        logger.info(f"📊 Métricas guardadas: {json.dumps(training_job.metrics, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando TrainingJob: {e}")
        return False


def test_model_metrics_queries():
    """Prueba consultas de métricas de modelo."""
    logger.info("🧪 Probando consultas de métricas...")
    
    try:
        # Obtener todos los modelos de regresión
        regression_models = ModelMetrics.objects.filter(model_type='regression')
        logger.info(f"📊 Total de modelos de regresión: {regression_models.count()}")
        
        # Obtener mejores modelos
        best_models = ModelMetrics.get_best_models()
        logger.info(f"🏆 Mejores modelos encontrados: {best_models.count()}")
        
        # Obtener modelos en producción
        production_models = ModelMetrics.get_production_models()
        logger.info(f"🚀 Modelos en producción: {production_models.count()}")
        
        # Obtener historial de un modelo específico
        model_history = ModelMetrics.get_model_history('test_regression_model')
        logger.info(f"📈 Historial del modelo de prueba: {model_history.count()} versiones")
        
        # Obtener tendencia de rendimiento
        performance_trend = ModelMetrics.get_performance_trend(
            'test_regression_model', 
            'alto', 
            'validation'
        )
        logger.info(f"📊 Tendencia de rendimiento: {len(performance_trend)} puntos")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en consultas: {e}")
        return False


def cleanup_test_data():
    """Limpia los datos de prueba."""
    logger.info("🧹 Limpiando datos de prueba...")
    
    try:
        # Eliminar métricas de prueba
        test_metrics = ModelMetrics.objects.filter(
            model_name__startswith='test_'
        )
        count = test_metrics.count()
        test_metrics.delete()
        logger.info(f"🗑️ Eliminadas {count} métricas de prueba")
        
        # Eliminar TrainingJobs de prueba
        test_jobs = TrainingJob.objects.filter(
            job_id__startswith='regression_test_model_'
        )
        count = test_jobs.count()
        test_jobs.delete()
        logger.info(f"🗑️ Eliminados {count} TrainingJobs de prueba")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error limpiando datos: {e}")
        return False


def main():
    """Función principal de prueba."""
    logger.info("🚀 Iniciando pruebas de persistencia de métricas ML...")
    
    tests = [
        ("Creación de métricas de modelo", test_model_metrics_creation),
        ("Creación de TrainingJob", test_training_job_creation),
        ("Consultas de métricas", test_model_metrics_queries),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASÓ")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 RESUMEN DE PRUEBAS: {passed}/{total} pasaron")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        logger.error(f"⚠️ {total - passed} pruebas fallaron")
    
    # Limpiar datos de prueba
    cleanup_test_data()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
