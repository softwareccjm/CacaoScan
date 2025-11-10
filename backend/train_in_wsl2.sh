#!/bin/bash
# Script para ejecutar entrenamiento en WSL2
set -e

echo "🚀 Configurando entorno para entrenamiento en WSL2..."

# Configurar PATH
export PATH=$PATH:/root/.local/bin

# Navegar al directorio del proyecto
cd /mnt/c/Users/Camacho/Documents/cacaoscan/backend

# Verificar Python
echo "Python: $(python3 --version)"

# Configurar Django
export DJANGO_SETTINGS_MODULE=cacaoscan.settings

# Ejecutar entrenamiento
echo "📊 Iniciando entrenamiento completo..."
python3 manage.py train_all_models \
  --yolo-dataset-size 150 \
  --yolo-epochs 50 \
  --yolo-batch-size 8 \
  --regression-epochs 50 \
  --regression-batch-size 8 \
  --regression-learning-rate 0.001

echo "✅ Entrenamiento completado!"

