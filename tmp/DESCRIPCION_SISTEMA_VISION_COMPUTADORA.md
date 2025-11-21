# 📊 Descripción Técnica Completa del Sistema de Visión por Computadora para Medición de Granos de Cacao

**Proyecto:** CacaoScan  
**Fecha de Documentación:** 2025-01-27  
**Versión del Sistema:** Híbrido (CNN + Features de Píxeles)

---

## 1. RESUMEN TÉCNICO COMPLETO DEL SISTEMA ACTUAL

### 1.1. Propósito del Sistema

CacaoScan es un sistema de visión por computadora que utiliza inteligencia artificial para medir automáticamente las dimensiones (alto, ancho, grosor) y el peso de granos de cacao a partir de imágenes digitales. El sistema elimina la necesidad de medición física manual, permitiendo análisis rápido y preciso de lotes de granos.

### 1.2. Lenguaje Principal y Stack Tecnológico

**Lenguaje Principal:** Python 3.12

**Librerías y Frameworks Principales:**

| Categoría | Librería | Versión | Propósito |
|-----------|----------|---------|-----------|
| **Deep Learning** | PyTorch | 2.3.1 | Framework principal para modelos de regresión |
| **Visión por Computadora** | OpenCV | 4.10.0.84 | Procesamiento de imágenes, segmentación, calibración |
| **Visión por Computadora** | Pillow | 10.0.0 | Manipulación de imágenes |
| **Segmentación IA** | rembg | 2.0.57 | Eliminación de fondo con U2Net |
| **Segmentación IA** | ultralytics | 8.3.33 | YOLOv8 para segmentación de granos |
| **Procesamiento Numérico** | NumPy | 1.26.4 | Operaciones matemáticas y arrays |
| **Machine Learning** | scikit-learn | 1.5.0 | Normalización, escaladores, métricas |
| **Data Science** | Pandas | 2.2.2 | Manejo de datasets CSV |
| **Backend Web** | Django | 4.2.7 | Framework web principal |
| **API REST** | Django REST Framework | 3.16.1 | API REST para comunicación frontend-backend |
| **Base de Datos** | PostgreSQL | 15 | Base de datos relacional |
| **Tareas Asíncronas** | Celery | 5.3.4 | Procesamiento en segundo plano |
| **Broker** | Redis | 7.0.0 | Mensajero para Celery |
| **Transformaciones** | Albumentations | 1.4.0 | Data augmentation para entrenamiento |

### 1.3. Arquitectura del Sistema

El sistema sigue una arquitectura de **3 capas**:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue.js 3)                   │
│  - Interfaz de usuario                                  │
│  - Subida de imágenes                                    │
│  - Visualización de resultados                          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API (JSON)
                       │ JWT Authentication
┌──────────────────────▼──────────────────────────────────┐
│              BACKEND (Django + DRF)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Layer (api/views.py)                         │  │
│  │  - Recibe imágenes                                │  │
│  │  - Valida datos                                    │  │
│  │  - Orquesta procesamiento                         │  │
│  └──────────────┬─────────────────────────────────────┘  │
│                 │                                        │
│  ┌──────────────▼────────────────────────────────────┐ │
│  │  Services Layer (api/services/)                     │ │
│  │  - AnalysisService: Lógica de negocio              │ │
│  │  - ImageService: Gestión de imágenes             │ │
│  └──────────────┬─────────────────────────────────────┘ │
│                 │                                        │
│  ┌──────────────▼────────────────────────────────────┐ │
│  │  ML Module (ml/)                                  │ │
│  │  - Segmentación (segmentation/)                   │ │
│  │  - Predicción (prediction/)                       │ │
│  │  - Regresión (regression/)                        │ │
│  │  - Calibración (measurement/)                     │ │
│  └───────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              BASE DE DATOS (PostgreSQL)                  │
│  - CacaoImage: Imágenes subidas                         │
│  - CacaoPrediction: Resultados de análisis              │
│  - TrainingJob: Historial de entrenamientos             │
│  - Finca, Lote: Organización de datos                   │
└──────────────────────────────────────────────────────────┘
```

### 1.4. Flujo de Procesamiento de Imágenes

El sistema procesa imágenes en **6 pasos principales**:

```
1. RECEPCIÓN DE IMAGEN
   └─> Frontend envía imagen (JPG/PNG/BMP) vía POST /api/v1/scan/measure/
       └─> Backend valida formato, tamaño (máx 8MB), dimensiones (mín 50x50px)

2. GUARDADO Y SEGMENTACIÓN
   └─> Guarda imagen original en media/cacao_images/
       └─> Segmenta grano usando cascada de métodos:
           ├─> Prioridad 1: U-Net (remove_background_ai)
           ├─> Prioridad 2: rembg (U2Net)
           └─> Prioridad 3: OpenCV (GrabCut + morfología)
       └─> Genera PNG con fondo transparente
       └─> Guarda en media/cacao_images/processed/YYYY/MM/DD/

3. EXTRACCIÓN DE FEATURES DE PÍXELES
   └─> Mide dimensiones del grano segmentado:
       ├─> pixel_width: Ancho en píxeles (solo área visible, alpha > 128)
       ├─> pixel_height: Alto en píxeles
       ├─> pixel_area: Área en píxeles
       ├─> scale_factor: Factor de conversión mm/píxel (de calibración)
       └─> aspect_ratio: Relación ancho/alto
   └─> Convierte a tensor [1, 5] para modelo híbrido

4. PREPROCESAMIENTO PARA CNN
   └─> Convierte PNG RGBA a RGB
       └─> Aplica transformaciones:
           ├─> Resize a 224x224
           ├─> ToTensor
           └─> Normalización ImageNet (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
       └─> Convierte a tensor [1, 3, 224, 224]

5. PREDICCIÓN CON MODELO HÍBRIDO
   └─> Modelo: HybridCacaoRegression
       ├─> Entrada 1: Tensor de imagen [1, 3, 224, 224]
       ├─> Entrada 2: Tensor de features de píxeles [1, 5]
       └─> Salida: 4 valores normalizados (alto, ancho, grosor, peso)
   └─> Desnormaliza usando escaladores (StandardScaler o RobustScaler)
   └─> Aplica límites físicos (clipping):
       ├─> alto: [5.0, 60.0] mm
       ├─> ancho: [3.0, 30.0] mm
       ├─> grosor: [1.0, 20.0] mm
       └─> peso: [0.2, 10.0] g

6. GUARDADO Y RESPUESTA
   └─> Guarda predicción en CacaoPrediction (PostgreSQL)
       ├─> alto_mm, ancho_mm, grosor_mm, peso_g
       ├─> confidences (actualmente fijas en 0.90)
       ├─> processing_time_ms
       └─> crop_url (ruta al PNG segmentado)
   └─> Responde JSON al frontend con resultados
```

---

## 2. MÓDULOS EXISTENTES Y SUS FUNCIONES

### 2.1. Módulo de Segmentación (`backend/ml/segmentation/`)

**Archivos principales:**
- `processor.py`: Procesador principal de segmentación
- `cropper.py`: Cropper con YOLO (legacy, no usado en flujo actual)
- `infer_yolo_seg.py`: Inferencia YOLO (legacy)
- `train_yolo.py`: Entrenamiento de YOLO (legacy)

**Función principal:** `segment_and_crop_cacao_bean(image_path: str, method: str = "ai") -> str`

**Métodos de segmentación (cascada):**

1. **U-Net (Prioridad 1)** - `remove_background_ai()`
   - Ubicación: `ml/data/transforms.py`
   - Modelo de deep learning para eliminación de fondo
   - Más preciso pero puede fallar en imágenes complejas

2. **rembg/U2Net (Prioridad 2)** - `_remove_background_rembg()`
   - Librería: `rembg`
   - Modelo U2Net preentrenado
   - Buen balance entre precisión y velocidad

3. **OpenCV (Prioridad 3)** - `_remove_background_opencv()`
   - Métodos: Otsu thresholding + GrabCut + morfología
   - Funciones auxiliares:
     - `_deshadow_alpha()`: Elimina sombras adyacentes
     - `_clean_components()`: Conserva componente mayor, elimina ruido
     - `_guided_refine()`: Refina bordes con guided filter
   - Fallback robusto, siempre disponible

**Salida:** Ruta absoluta a archivo PNG con fondo transparente (RGBA)

### 2.2. Módulo de Predicción (`backend/ml/prediction/`)

**Archivos principales:**
- `predict.py`: Predictor principal (modo híbrido)
- `calibrated_predict.py`: Predicción con calibración avanzada (opcional)

**Clase principal:** `CacaoPredictor`

**Métodos clave:**

- `__init__(confidence_threshold: float = 0.5)`: Inicializa predictor
- `load_artifacts() -> bool`: Carga modelos y escaladores
- `predict(image: Image.Image) -> Dict[str, Any]`: Predicción principal
- `_segment_and_crop()`: Segmenta imagen
- `_extract_crop_characteristics()`: Extrae features de píxeles
- `_preprocess_image()`: Preprocesa para CNN
- `_predict_hybrid()`: Ejecuta modelo híbrido
- `_calculate_pixel_to_mm_scale_factor()`: Calcula factor de escala desde calibración

**Instancia global:** `get_predictor()` retorna singleton

**Artefactos requeridos:**
- `hybrid.pt`: Modelo híbrido entrenado
- `alto_scaler.pkl`, `ancho_scaler.pkl`, `grosor_scaler.pkl`, `peso_scaler.pkl`: Escaladores
- `pixel_calibration.json`: Calibración de píxeles (opcional pero recomendado)

### 2.3. Módulo de Regresión (`backend/ml/regression/`)

**Archivos principales:**
- `models.py`: Definición de arquitecturas de modelos
- `train.py`: Entrenamiento básico
- `train_improved.py`: Entrenamiento mejorado
- `hybrid_trainer.py`: Entrenador para modelo híbrido
- `hybrid_model.py`: Arquitectura del modelo híbrido
- `scalers.py`: Gestión de escaladores
- `metrics.py`: Métricas de evaluación
- `evaluate.py`: Evaluación de modelos

**Arquitecturas disponibles:**

1. **ResNet18Regression**
   - Backbone: ResNet18 preentrenado en ImageNet
   - Head: 3 capas fully connected (256 → 128 → num_outputs)
   - BatchNorm y Dropout para regularización
   - Inicialización Xavier uniform

2. **ConvNeXtTinyRegression**
   - Backbone: ConvNeXt Tiny (timm)
   - Pesos: ImageNet-12k preentrenados
   - Similar head a ResNet18

3. **HybridCacaoRegression** (ACTUAL)
   - Fusiona CNN (ResNet18 o ConvNeXt) + Features de píxeles
   - Entrada dual:
     - Imagen: [batch, 3, 224, 224]
     - Pixel features: [batch, 5] (width, height, area, scale_factor, aspect_ratio)
   - Fusiona en capa intermedia
   - Salida: 4 valores (alto, ancho, grosor, peso)

**Escaladores:**
- `StandardScaler` o `RobustScaler` (configurable)
- Uno por target (alto, ancho, grosor, peso)
- Guardados en `regressors_artifacts/{target}_scaler.pkl`

### 2.4. Módulo de Datos (`backend/ml/data/`)

**Archivos principales:**
- `cacao_dataset.py`: Dataset principal para entrenamiento
- `dataset_loader.py`: Cargador de datasets CSV
- `hybrid_dataset.py`: Dataset para modelo híbrido
- `pixel_feature_extractor.py`: Extractor de features de píxeles
- `pixel_features_loader.py`: Cargador de features de píxeles
- `transforms.py`: Transformaciones de imágenes (incluye U-Net)
- `improved_dataloader.py`: DataLoader mejorado

**Clase principal:** `CacaoDataset`

**Funcionalidades:**
- Carga CSV con columnas: `ID, ALTO, ANCHO, GROSOR, PESO, filename, image_path`
- Valida existencia de imágenes
- Carga crops segmentados (PNG con fondo transparente)
- Extrae features de píxeles desde `pixel_calibration.json`
- Aplica transformaciones (augmentation) durante entrenamiento
- Normaliza targets usando escaladores

### 2.5. Módulo de Calibración (`backend/ml/measurement/`)

**Archivo principal:** `calibration.py`

**Funcionalidades:**
- Calibración de píxeles a milímetros
- Detección automática de objetos de referencia (monedas, reglas)
- Calibración manual con puntos de referencia
- Validación de precisión
- Persistencia en `pixel_calibration.json`

**Objetos de referencia soportados:**
- Monedas colombianas: 1000 COP (23mm), 500 COP (21mm), 200 COP (17mm), 100 COP (15mm)
- Reglas: 1cm, 2cm, 5cm

**Estructura de `pixel_calibration.json`:**
```json
{
  "calibration_records": [
    {
      "id": 510,
      "pixel_measurements": {
        "width_pixels": 650,
        "height_pixels": 900,
        "grain_area_pixels": 450000,
        "aspect_ratio": 0.72
      },
      "scale_factors": {
        "width_mm_per_pixel": 0.035,
        "height_mm_per_pixel": 0.035,
        "average_mm_per_pixel": 0.035
      },
      "real_dimensions": {
        "alto_mm": 22.8,
        "ancho_mm": 16.3,
        "grosor_mm": 10.2,
        "peso_g": 1.72
      }
    }
  ],
  "statistics": {
    "scale_factors": {
      "mean": 0.035,
      "std": 0.002,
      "min": 0.030,
      "max": 0.040
    }
  }
}
```

### 2.6. Módulo de Pipeline de Entrenamiento (`backend/ml/pipeline/`)

**Archivos principales:**
- `train_all.py`: Pipeline completo de entrenamiento
- `hybrid_training.py`: Entrenamiento híbrido (legacy)
- `hybrid_v2_training.py`: Entrenamiento híbrido v2 mejorado

**Clase principal:** `CacaoTrainingPipeline`

**Flujo de entrenamiento:**

1. **Carga de datos**
   - Lee CSV del dataset
   - Valida imágenes
   - Genera crops si no existen
   - Carga calibración de píxeles

2. **Preprocesamiento**
   - Normaliza targets con escaladores
   - Divide dataset: 70% train, 10% validation, 20% test
   - Aplica augmentation (rotaciones, cambios de brillo, etc.)

3. **Entrenamiento**
   - Entrena modelo híbrido
   - Usa loss function: Smooth L1, MSE o Huber (configurable)
   - Optimizador: Adam con learning rate scheduler
   - Early stopping si no mejora
   - Guarda checkpoints

4. **Evaluación**
   - Evalúa en conjunto de test
   - Calcula métricas: MAE, RMSE, R², MAPE
   - Genera reporte JSON

5. **Guardado**
   - Guarda modelo: `hybrid.pt`
   - Guarda escaladores: `{target}_scaler.pkl`
   - Guarda reporte: `evaluation_report_{timestamp}.json`

### 2.7. Módulo de Comandos de Gestión (`backend/training/management/commands/`)

**Comandos principales:**

1. **`train_cacao_models.py`**
   - Comando: `python manage.py train_cacao_models`
   - Entrena modelos de regresión
   - Argumentos:
     - `--hybrid`: Usar modelo híbrido (recomendado)
     - `--use-pixel-features`: Incluir features de píxeles
     - `--epochs`: Número de épocas (default: 50)
     - `--batch-size`: Tamaño de batch (default: 32)
     - `--learning-rate`: Learning rate (default: 1e-5)
     - `--segmentation-backend`: Método de segmentación (auto/opencv/ai)

2. **`calibrate_dataset_pixels.py`**
   - Comando: `python manage.py calibrate_dataset_pixels`
   - Genera `pixel_calibration.json` desde dataset
   - Procesa todas las imágenes del dataset
   - Mide píxeles y calcula factores de escala

3. **`make_cacao_crops.py`**
   - Comando: `python manage.py make_cacao_crops`
   - Genera crops segmentados para todas las imágenes
   - Guarda PNGs con fondo transparente

4. **`convert_cacao_images.py`**
   - Comando: `python manage.py convert_cacao_images`
   - Convierte BMP a JPG (si es necesario)

### 2.8. Módulo de API (`backend/api/`)

**Archivos principales:**
- `views.py`: Vistas principales (ScanMeasureView)
- `services/analysis_service.py`: Servicio de análisis
- `ml_views.py`: Vistas relacionadas con ML
- `calibration_views.py`: Vistas de calibración
- `models.py`: Modelos de base de datos (importa desde apps modulares)

**Endpoints principales:**

- `POST /api/v1/scan/measure/`: Medir grano de cacao
  - Recibe: multipart/form-data con campo `image`
  - Responde: JSON con predicciones (alto, ancho, grosor, peso, confidences, crop_url)

- `GET /api/v1/predictions/`: Listar predicciones
- `GET /api/v1/predictions/{id}/`: Detalles de predicción
- `POST /api/v1/training/start/`: Iniciar entrenamiento
- `GET /api/v1/training/status/{job_id}/`: Estado de entrenamiento

### 2.9. Módulo de Utilidades (`backend/ml/utils/`)

**Archivos:**
- `paths.py`: Rutas de directorios (artifacts, datasets, media)
- `logs.py`: Configuración de logging
- `io.py`: Utilidades de I/O (guardar/cargar JSON, asegurar directorios)
- `metrics.py`: Métricas de evaluación
- `losses.py`: Funciones de pérdida personalizadas
- `scalers.py`: Utilidades de escaladores
- `early_stopping.py`: Early stopping callback

---

## 3. DIAGRAMA DEL FLUJO INTERNO (TEXTO)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DE ANÁLISIS                            │
└─────────────────────────────────────────────────────────────────────────┘

[FRONTEND] Usuario sube imagen
    │
    │ POST /api/v1/scan/measure/
    │ Content-Type: multipart/form-data
    │ Body: { image: File }
    ▼
[BACKEND] ScanMeasureView.post()
    │
    ├─> Validar imagen (tipo, tamaño, dimensiones)
    │
    ├─> Guardar imagen original
    │   └─> CacaoImage.save() → media/cacao_images/
    │
    ├─> Segmentar grano
    │   └─> segment_and_crop_cacao_bean(image_path, method="ai")
    │       │
    │       ├─> [INTENTO 1] remove_background_ai() (U-Net)
    │       │   └─> Si falla →
    │       │
    │       ├─> [INTENTO 2] _remove_background_rembg() (U2Net)
    │       │   └─> Si falla →
    │       │
    │       └─> [INTENTO 3] _remove_background_opencv()
    │           ├─> Otsu thresholding
    │           ├─> GrabCut
    │           ├─> _clean_components()
    │           ├─> _deshadow_alpha()
    │           └─> _guided_refine()
    │
    │   └─> Guardar PNG RGBA → media/cacao_images/processed/YYYY/MM/DD/
    │
    └─> Obtener predictor
        └─> get_predictor() → CacaoPredictor (singleton)
            │
            ├─> Si modelos no cargados:
            │   └─> load_artifacts()
            │       ├─> Cargar hybrid.pt
            │       ├─> Cargar escaladores (alto, ancho, grosor, peso)
            │       └─> Cargar pixel_calibration.json (opcional)
            │
            └─> predictor.predict(image)
                │
                ├─> PASO 1: Segmentar
                │   └─> _segment_and_crop()
                │       └─> Retorna: (crop_image: PIL.Image, crop_url: str, confidence: float)
                │
                ├─> PASO 2: Extraer features de píxeles
                │   └─> _extract_crop_characteristics(crop_image)
                │       ├─> Medir width_pixels, height_pixels, pixel_area
                │       ├─> Calcular aspect_ratio
                │       ├─> _calculate_pixel_to_mm_scale_factor()
                │       │   └─> Buscar en pixel_calibration.json registro similar
                │       │       └─> Retornar average_mm_per_pixel
                │       └─> Retornar: { pixel_width, pixel_height, pixel_area, scale_factor, aspect_ratio }
                │
                ├─> PASO 3: Preprocesar imagen
                │   └─> _preprocess_image(crop_image)
                │       ├─> Convertir a RGB
                │       ├─> Resize a 224x224
                │       ├─> ToTensor
                │       └─> Normalizar (ImageNet stats)
                │
                ├─> PASO 4: Predicción híbrida
                │   └─> _predict_hybrid(image_tensor, pixel_features_tensor)
                │       ├─> regression_model.eval()
                │       ├─> Forward pass: model(image_tensor, pixel_features_tensor)
                │       ├─> Salida: 4 valores normalizados
                │       └─> Desnormalizar con escaladores
                │
                ├─> PASO 5: Aplicar límites físicos
                │   └─> np.clip(predictions, min_val, max_val)
                │
                └─> PASO 6: Preparar resultado
                    └─> Retornar: {
                        'alto_mm': float,
                        'ancho_mm': float,
                        'grosor_mm': float,
                        'peso_g': float,
                        'confidences': { 'alto': 0.90, ... },
                        'crop_url': str,
                        'debug': { ... }
                    }
    │
    └─> Guardar predicción
        └─> CacaoPrediction.save()
            ├─> Guardar en PostgreSQL
            └─> Marcar imagen como procesada
    │
    └─> Responder JSON al frontend
        └─> HTTP 200 OK
            {
                'alto_mm': 22.8,
                'ancho_mm': 16.3,
                'grosor_mm': 10.2,
                'peso_g': 1.72,
                'confidences': { ... },
                'crop_url': '/media/cacao_images/processed/...',
                'image_id': 123,
                'prediction_id': 456
            }
```

---

## 4. QUÉ FUNCIONA ACTUALMENTE

### 4.1. Segmentación de Granos ✅

- **Funcionalidad:** Eliminación de fondo y segmentación de granos
- **Métodos:** Cascada U-Net → rembg → OpenCV
- **Precisión:** Alta en imágenes con buen contraste
- **Formato de salida:** PNG RGBA con fondo transparente
- **Ubicación:** `backend/ml/segmentation/processor.py`

### 4.2. Predicción de Dimensiones y Peso ✅

- **Funcionalidad:** Predicción de alto, ancho, grosor y peso
- **Modelo:** HybridCacaoRegression (CNN + Features de píxeles)
- **Precisión:** Depende del entrenamiento, típicamente MAE < 2mm para dimensiones
- **Tiempo de procesamiento:** 5-10 segundos por imagen (CPU)
- **Ubicación:** `backend/ml/prediction/predict.py`

### 4.3. Calibración de Píxeles ✅

- **Funcionalidad:** Conversión de píxeles a milímetros
- **Método:** Basado en dataset calibrado (`pixel_calibration.json`)
- **Precisión:** Mejora cuando hay registro similar en calibración
- **Ubicación:** `backend/ml/prediction/predict.py` (método `_calculate_pixel_to_mm_scale_factor`)

### 4.4. Entrenamiento de Modelos ✅

- **Funcionalidad:** Entrenamiento de modelos híbridos
- **Comando:** `python manage.py train_cacao_models --hybrid --use-pixel-features`
- **Características:**
  - Data augmentation
  - Early stopping
  - Guardado de checkpoints
  - Evaluación automática
- **Ubicación:** `backend/training/management/commands/train_cacao_models.py`

### 4.5. API REST ✅

- **Funcionalidad:** Endpoints para análisis y gestión
- **Autenticación:** JWT
- **Endpoints principales:**
  - `POST /api/v1/scan/measure/`: Medir grano
  - `GET /api/v1/predictions/`: Listar predicciones
  - `POST /api/v1/training/start/`: Iniciar entrenamiento
- **Ubicación:** `backend/api/views.py`

### 4.6. Almacenamiento en Base de Datos ✅

- **Funcionalidad:** Persistencia de imágenes y predicciones
- **Modelos:**
  - `CacaoImage`: Imágenes subidas
  - `CacaoPrediction`: Resultados de análisis
  - `TrainingJob`: Historial de entrenamientos
- **Ubicación:** `backend/images_app/models.py`

---

## 5. QUÉ NO FUNCIONA O ESTÁ PENDIENTE

### 5.1. Cálculo de Confianza Real ❌

- **Problema:** Las confidences están hardcodeadas en 0.90
- **Ubicación:** `backend/ml/prediction/predict.py` línea 442
- **Solución necesaria:** Implementar cálculo basado en:
  - Varianza de predicciones (múltiples forward passes con dropout)
  - Distancia a datos de entrenamiento
  - Calidad de segmentación

### 5.2. Procesamiento Paralelo ❌

- **Problema:** Procesamiento secuencial de imágenes
- **Impacto:** Lotes grandes tardan mucho tiempo
- **Solución necesaria:** Implementar procesamiento en batch o paralelo

### 5.3. Soporte GPU Limitado ⚠️

- **Problema:** Sistema optimizado para CPU, no aprovecha GPU completamente
- **Impacto:** Procesamiento más lento de lo necesario
- **Solución necesaria:** Optimizar carga de modelos en GPU, usar mixed precision

### 5.4. Calibración Automática con Objetos de Referencia ❌

- **Problema:** Módulo de calibración existe pero no está integrado en flujo principal
- **Ubicación:** `backend/ml/measurement/calibration.py`
- **Solución necesaria:** Integrar detección automática de monedas/reglas en imágenes

### 5.5. Validación de Calidad de Segmentación ⚠️

- **Problema:** No se valida si la segmentación es correcta antes de predecir
- **Impacto:** Predicciones incorrectas en imágenes mal segmentadas
- **Solución necesaria:** Implementar métricas de calidad (área mínima, relación aspecto, etc.)

### 5.6. Manejo de Errores en Cascada de Segmentación ⚠️

- **Problema:** Si todos los métodos fallan, se lanza excepción genérica
- **Solución necesaria:** Mejorar mensajes de error y logging

### 5.7. Actualización de Modelos en Tiempo Real ❌

- **Problema:** Modelos deben recargarse manualmente después de entrenamiento
- **Solución necesaria:** Implementar hot-reload de modelos

---

## 6. CÓMO SE USA ACTUALMENTE

### 6.1. Uso por Consola (Comandos Django)

**Entrenar modelos:**
```bash
cd backend
python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32
```

**Calibrar dataset:**
```bash
python manage.py calibrate_dataset_pixels --segmentation-backend auto
```

**Generar crops:**
```bash
python manage.py make_cacao_crops --segmentation-backend auto
```

### 6.2. Uso por API REST

**Medir grano:**
```bash
curl -X POST http://localhost:8000/api/v1/scan/measure/ \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "image=@grano.jpg"
```

**Respuesta:**
```json
{
  "alto_mm": 22.8,
  "ancho_mm": 16.3,
  "grosor_mm": 10.2,
  "peso_g": 1.72,
  "confidences": {
    "alto": 0.90,
    "ancho": 0.90,
    "grosor": 0.90,
    "peso": 0.90
  },
  "crop_url": "/media/cacao_images/processed/2025/01/27/cacao_abc123.png",
  "image_id": 123,
  "prediction_id": 456
}
```

### 6.3. Uso por Frontend Web

1. Usuario inicia sesión
2. Navega a página de análisis
3. Selecciona imagen(es) de granos
4. Hace clic en "Analizar"
5. Sistema procesa y muestra resultados:
   - Dimensiones (alto, ancho, grosor)
   - Peso
   - Imagen segmentada
   - Nivel de confianza

---

## 7. LIMITACIONES ACTUALES

### 7.1. Precisión

- **Dependencia del entrenamiento:** La precisión depende directamente de la calidad y cantidad de datos de entrenamiento
- **Rango de valores:** Modelo entrenado para rangos específicos (alto: 5-60mm, ancho: 3-30mm, etc.)
- **Fuera de rango:** Granos fuera de estos rangos pueden tener predicciones incorrectas

### 7.2. Rendimiento

- **CPU only:** Optimizado para CPU, no aprovecha GPU completamente
- **Secuencial:** Procesa una imagen a la vez
- **Tiempo:** 5-10 segundos por imagen en CPU

### 7.3. Calibración

- **Dependencia de dataset:** Requiere `pixel_calibration.json` generado desde dataset
- **Sin objetos de referencia:** No detecta automáticamente monedas/reglas en imágenes nuevas
- **Factor por defecto:** Si no hay calibración, usa factor fijo (0.035 mm/píxel)

### 7.4. Segmentación

- **Condiciones de iluminación:** Puede fallar con iluminación muy baja o muy alta
- **Fondos complejos:** Fondos muy similares al grano pueden causar segmentación incorrecta
- **Granos deformados:** Granos muy deformados pueden segmentarse incorrectamente

### 7.5. Confianza

- **Valores fijos:** Confidences hardcodeadas en 0.90, no reflejan incertidumbre real
- **Sin validación:** No valida calidad de segmentación antes de predecir

### 7.6. Escalabilidad

- **Sin procesamiento paralelo:** No puede procesar múltiples imágenes simultáneamente
- **Sin cola de tareas:** Análisis bloquea request hasta completarse
- **Sin caché:** No cachea resultados de segmentación

---

## 8. MEJORAS NECESARIAS PARA COMPLETAR EL SISTEMA

### 8.1. Mejoras de Precisión

1. **Implementar cálculo real de confianza**
   - Múltiples forward passes con dropout activado
   - Análisis de varianza
   - Distancia a datos de entrenamiento (outlier detection)

2. **Validación de calidad de segmentación**
   - Verificar área mínima del grano
   - Verificar relación de aspecto razonable
   - Detectar segmentaciones fallidas antes de predecir

3. **Mejorar calibración de píxeles**
   - Integrar detección automática de objetos de referencia
   - Calibración por imagen individual
   - Validación de precisión de calibración

### 8.2. Mejoras de Rendimiento

1. **Procesamiento paralelo**
   - Procesar múltiples imágenes en batch
   - Usar multiprocessing para segmentación
   - Cola de tareas con Celery para análisis batch

2. **Optimización GPU**
   - Cargar modelos en GPU desde inicio
   - Usar mixed precision training
   - Batch inference

3. **Caché de resultados**
   - Cachear segmentaciones (hash de imagen)
   - Cachear predicciones para imágenes idénticas

### 8.3. Mejoras de Robustez

1. **Manejo de errores mejorado**
   - Mensajes de error más descriptivos
   - Fallbacks automáticos
   - Logging detallado

2. **Validación de entrada**
   - Validar calidad de imagen (resolución, contraste)
   - Detectar imágenes corruptas
   - Validar formato antes de procesar

3. **Recuperación de errores**
   - Reintentos automáticos en fallos de segmentación
   - Guardar estado intermedio para recuperación

### 8.4. Mejoras de Funcionalidad

1. **Análisis batch**
   - Endpoint para múltiples imágenes
   - Procesamiento asíncrono con Celery
   - Notificaciones cuando termine

2. **Historial y comparación**
   - Comparar predicciones con mediciones reales
   - Gráficos de evolución de precisión
   - Exportar datos para análisis

3. **Calibración interactiva**
   - Interfaz para calibración manual
   - Validación visual de calibración
   - Guardar múltiples calibraciones

### 8.5. Mejoras de Monitoreo

1. **Métricas en tiempo real**
   - Dashboard de precisión
   - Tiempos de procesamiento
   - Tasa de errores

2. **Alertas**
   - Alertar cuando precisión baja
   - Alertar cuando modelos necesitan reentrenamiento
   - Alertar sobre errores frecuentes

### 8.6. Mejoras de Documentación

1. **Documentación técnica**
   - Documentar arquitectura completa
   - Documentar flujos de datos
   - Documentar APIs

2. **Guías de usuario**
   - Cómo tomar buenas fotos
   - Cómo interpretar resultados
   - Cómo calibrar sistema

---

## 9. ESTRUCTURA DE ARCHIVOS RELEVANTES

```
backend/
├── ml/
│   ├── segmentation/
│   │   ├── processor.py          # Segmentación principal (cascada)
│   │   ├── cropper.py            # YOLO cropper (legacy)
│   │   └── infer_yolo_seg.py    # Inferencia YOLO (legacy)
│   │
│   ├── prediction/
│   │   ├── predict.py            # Predictor principal (HÍBRIDO)
│   │   └── calibrated_predict.py # Predicción calibrada (opcional)
│   │
│   ├── regression/
│   │   ├── models.py             # Arquitecturas (ResNet18, ConvNeXt, Hybrid)
│   │   ├── hybrid_model.py       # Modelo híbrido
│   │   ├── hybrid_trainer.py     # Entrenador híbrido
│   │   ├── train_improved.py     # Entrenamiento mejorado
│   │   ├── scalers.py            # Gestión de escaladores
│   │   └── metrics.py            # Métricas de evaluación
│   │
│   ├── data/
│   │   ├── cacao_dataset.py      # Dataset principal
│   │   ├── dataset_loader.py     # Cargador de CSV
│   │   ├── hybrid_dataset.py     # Dataset híbrido
│   │   ├── pixel_feature_extractor.py # Extractor de features
│   │   └── transforms.py         # Transformaciones (incluye U-Net)
│   │
│   ├── measurement/
│   │   └── calibration.py       # Calibración con objetos de referencia
│   │
│   ├── pipeline/
│   │   ├── train_all.py          # Pipeline completo de entrenamiento
│   │   └── hybrid_v2_training.py # Entrenamiento híbrido v2
│   │
│   └── utils/
│       ├── paths.py               # Rutas de directorios
│       ├── logs.py                # Logging
│       ├── io.py                  # I/O utilities
│       └── metrics.py             # Métricas
│
├── api/
│   ├── views.py                   # Vistas principales (ScanMeasureView)
│   ├── services/
│   │   └── analysis_service.py   # Servicio de análisis
│   └── ml_views.py               # Vistas ML
│
├── training/
│   └── management/
│       └── commands/
│           ├── train_cacao_models.py      # Comando entrenamiento
│           ├── calibrate_dataset_pixels.py # Comando calibración
│           └── make_cacao_crops.py       # Comando generar crops
│
└── images_app/
    └── models.py                  # CacaoImage, CacaoPrediction
```

---

## 10. CONFIGURACIÓN Y VARIABLES DE ENTORNO

**Archivos de configuración:**
- `backend/requirements.txt`: Dependencias Python
- `backend/cacaoscan/settings.py`: Configuración Django
- `.env`: Variables de entorno (DB, secret keys, etc.)

**Variables importantes:**
- `MEDIA_ROOT`: Directorio de archivos multimedia
- `DATASETS_DIR`: Directorio de datasets CSV
- `ARTIFACTS_DIR`: Directorio de modelos entrenados

**Rutas por defecto:**
- Imágenes originales: `media/cacao_images/`
- Crops segmentados: `media/cacao_images/processed/YYYY/MM/DD/`
- Modelos: `media/ml_artifacts/regressors/`
- Datasets: `media/datasets/`

---

## 11. CONCLUSIÓN

El sistema CacaoScan es un sistema completo de visión por computadora para medición de granos de cacao que combina:

- **Segmentación avanzada** con cascada de métodos (U-Net, rembg, OpenCV)
- **Predicción híbrida** que fusiona CNN (ResNet18/ConvNeXt) con features de píxeles
- **Calibración de píxeles** basada en dataset calibrado
- **API REST** completa para integración
- **Entrenamiento automatizado** con pipeline completo

**Estado actual:** Sistema funcional con capacidades básicas completas, pero con oportunidades de mejora en precisión, rendimiento y robustez.

**Próximos pasos recomendados:**
1. Implementar cálculo real de confianza
2. Agregar procesamiento paralelo
3. Integrar calibración automática con objetos de referencia
4. Mejorar validación de calidad de segmentación
5. Optimizar para GPU

---

**Documento generado:** 2025-01-27  
**Versión del sistema documentada:** Híbrido (CNN + Pixel Features)  
**Última actualización del código:** 2025-01-27

