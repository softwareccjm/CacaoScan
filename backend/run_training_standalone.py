#!/usr/bin/env python
"""
Script independiente para ejecutar entrenamiento sin Docker.
Úsalo si Docker Desktop sigue fallando.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

# Ejecutar el comando
from django.core.management import call_command

if __name__ == '__main__':
    print("Ejecutando entrenamiento completo...")
    print("Esto puede tomar varias horas. Por favor, sea paciente...")
    
    try:
        call_command(
            'train_all_models',
            yolo_dataset_size=150,
            yolo_epochs=50,
            yolo_batch_size=8,
            regression_epochs=50,
            regression_batch_size=8,
            regression_learning_rate=0.001
        )
        print("\n✓ Entrenamiento completado exitosamente")
    except KeyboardInterrupt:
        print("\n⚠ Entrenamiento interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

