# 🚀 CACOASCAN YOLOV8 - SISTEMA DE PREDICCIÓN DE PESO

Sistema completo de detección y predicción de peso de granos de cacao usando YOLOv8.

## 📋 CARACTERÍSTICAS PRINCIPALES

### 🎯 Detección Automática
- **Detección de granos**: Identifica automáticamente granos de cacao en imágenes
- **Recorte inteligente**: Aísla el objeto como hace el iPhone
- **Bounding box preciso**: Calcula coordenadas exactas del grano

### 📏 Estimación de Dimensiones
- **Medidas físicas**: Calcula alto, ancho y grosor en milímetros
- **Calibración automática**: Convierte píxeles a medidas reales
- **Precisión mejorada**: Usa datos de calibración para mayor exactitud

### ⚖️ Predicción de Peso
- **Fórmula empírica**: `peso = densidad × volumen × factor_forma`
- **Volumen elipsoidal**: `V = (4/3) × π × a × b × c`
- **Rango realista**: Predicciones entre 0.5g y 3.0g

### 🔄 Integración Completa
- **Sin duplicación**: Reutiliza vistas y endpoints existentes
- **Comparación múltiple**: CNN + Regresión + YOLOv8
- **API unificada**: Endpoint `/api/images/predict-yolo/`

## 🏗️ ARQUITECTURA DEL SISTEMA

```
backend/ml/
├── yolo_model.py              # Clase principal CacaoYOLOModel
├── prepare_yolo_data.py       # Preparación de datos para entrenamiento
├── train_yolo.py             # Script de entrenamiento
├── demo_yolo_system.py       # Demo completo del sistema
├── models/weight_predictor_yolo/
│   ├── weight_yolo.pt        # Modelo entrenado
│   ├── calibration.json      # Datos de calibración
│   └── integrated_weight_model.json
└── config.py                 # Configuración actualizada
```

## 🚀 INSTALACIÓN Y CONFIGURACIÓN

### 1. Dependencias
```bash
pip install ultralytics torch torchvision opencv-python
```

### 2. Preparar Datos
```bash
python prepare_yolo_data.py \
    --dataset-csv backend/ml/media/dataset/dataset.csv \
    --images-dir backend/ml/media/imgs \
    --output-dir yolo_dataset \
    --split-ratios 0.7 0.2 0.1
```

### 3. Entrenar Modelo
```bash
python train_yolo.py \
    --dataset-config yolo_dataset/dataset.yaml \
    --output-dir training_output \
    --model-size n \
    --epochs 100 \
    --batch 16
```

### 4. Probar Sistema
```bash
python demo_yolo_system.py
```

## 📊 FORMATO DE DATOS

### Entrada (Imagen)
- **Formatos**: JPG, PNG, BMP, TIFF
- **Tamaño**: Máximo 10MB
- **Resolución**: Cualquier tamaño (se redimensiona a 640x640)

### Salida (Predicción)
```json
{
    "peso_estimado": 1.94,
    "altura_mm": 22.25,
    "ancho_mm": 14.63,
    "grosor_mm": 7.88,
    "nivel_confianza": 0.85,
    "detection_info": {
        "bbox_pixels": [100, 150, 200, 250],
        "width_pixels": 100,
        "height_pixels": 100,
        "detection_method": "yolo_v8"
    },
    "processing_time": 0.234,
    "success": true
}
```

## 🔧 USO DEL SISTEMA

### 1. Uso Básico
```python
from ml.yolo_model import CacaoYOLOModel

# Crear modelo
model = CacaoYOLOModel()

# Cargar modelo entrenado
model.load_model('training_output/weight_yolo.pt')

# Realizar predicción
result = model.predict_weight_from_image('imagen.jpg')
print(f"Peso: {result['peso_estimado']}g")
```

### 2. Uso con Servicio de Predicción
```python
from ml.prediction_service import CacaoPredictionService

# Crear servicio con YOLOv8
service = CacaoPredictionService(enable_yolo=True)

# Análisis completo
result = service.predict_complete_analysis(
    'imagen.jpg',
    include_yolo=True
)

print(f"Peso YOLOv8: {result['yolo_prediction']['peso_estimado']}g")
```

### 3. Uso via API
```bash
curl -X POST http://localhost:8000/api/images/predict-yolo/ \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "image=@granos.jpg" \
    -F "batch_number=LOTE001" \
    -F "return_detection_image=true"
```

## 🎛️ CONFIGURACIÓN AVANZADA

### Calibración del Modelo
```python
# Calibrar con imágenes de referencia
model.calibrate_model(
    reference_images=['ref1.jpg', 'ref2.jpg'],
    reference_sizes_mm=[20.0, 18.5]
)
```

### Configuración de Entrenamiento
```python
# Configuración personalizada
custom_config = {
    'epochs': 150,
    'batch_size': 32,
    'learning_rate': 0.005,
    'patience': 30,
    'device': 'cuda'
}
```

### Parámetros de Detección
```python
# Ajustar umbrales
model = CacaoYOLOModel(
    confidence_threshold=0.6,
    iou_threshold=0.5
)
```

## 📈 MÉTRICAS Y EVALUACIÓN

### Métricas de Detección
- **mAP50**: Precisión promedio con IoU > 0.5
- **mAP50-95**: Precisión promedio con IoU 0.5-0.95
- **Precision**: Verdaderos positivos / (Verdaderos positivos + Falsos positivos)
- **Recall**: Verdaderos positivos / (Verdaderos positivos + Falsos negativos)

### Métricas de Peso
- **MAE**: Error absoluto medio
- **RMSE**: Raíz del error cuadrático medio
- **R²**: Coeficiente de determinación
- **MAPE**: Error porcentual absoluto medio

## 🔍 DEBUGGING Y TROUBLESHOOTING

### Problemas Comunes

#### 1. Modelo no carga
```python
# Verificar disponibilidad de YOLO
from ultralytics import YOLO
print("YOLO disponible:", YOLO is not None)

# Verificar ruta del modelo
import os
model_path = "training_output/weight_yolo.pt"
print("Modelo existe:", os.path.exists(model_path))
```

#### 2. Predicciones incorrectas
```python
# Verificar calibración
model.get_model_info()['calibration_data']

# Recalibrar si es necesario
model.calibrate_model(reference_images, reference_sizes)
```

#### 3. Rendimiento lento
```python
# Usar GPU si está disponible
model = CacaoYOLOModel(device='cuda')

# Precargar modelo
model.warmup()
```

### Logs y Monitoreo
```python
import logging
logging.basicConfig(level=logging.INFO)

# Los logs mostrarán:
# - Tiempo de carga del modelo
# - Tiempo de inferencia
# - Errores de predicción
# - Estadísticas de uso
```

## 🚀 DESPLIEGUE EN PRODUCCIÓN

### 1. Optimización del Modelo
```bash
# Exportar a ONNX para mejor rendimiento
python train_yolo.py --export onnx
```

### 2. Configuración de Servidor
```python
# En settings.py
YOLO_MODEL_PATH = '/path/to/weight_yolo.pt'
YOLO_CONFIDENCE_THRESHOLD = 0.5
YOLO_DEVICE = 'cuda'  # o 'cpu'
```

### 3. Monitoreo
```python
# Estadísticas de uso
info = model.get_model_info()
print(f"Predicciones realizadas: {info['prediction_count']}")
print(f"Tiempo promedio: {info['avg_inference_time']:.3f}s")
```

## 📚 REFERENCIAS Y RECURSOS

### Documentación YOLOv8
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [YOLOv8 GitHub](https://github.com/ultralytics/ultralytics)

### Papers Relevantes
- [YOLOv8: Real-Time Object Detection](https://arxiv.org/abs/2305.09972)
- [Object Detection in Computer Vision](https://arxiv.org/abs/2005.13243)

### Datasets de Cacao
- Dataset interno: `backend/ml/media/dataset/dataset.csv`
- 510 imágenes numeradas: `1.bmp` a `510.bmp`

## 🤝 CONTRIBUCIÓN

### Cómo Contribuir
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código
- Seguir PEP 8 para Python
- Documentar todas las funciones
- Incluir tests unitarios
- Mantener compatibilidad con sistema existente

## 📄 LICENCIA

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 📞 SOPORTE

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Contactar al equipo de desarrollo
- Revisar documentación existente

---

**¡Sistema YOLOv8 listo para predecir pesos de granos de cacao con precisión!** 🍫⚖️
