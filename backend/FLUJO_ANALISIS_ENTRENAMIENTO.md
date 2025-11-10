# Flujo de Análisis y Entrenamiento - CacaoScan

Este documento describe el flujo exacto que debe seguir el sistema según la documentación.

## FLUJO COMPLETO DE UN ANÁLISIS

### 1. Usuario inicia sesión
- Frontend envía credenciales → Backend verifica → Genera token JWT → Frontend guarda token

### 2. Usuario sube imágenes
- Frontend prepara FormData → Envía petición POST → Backend recibe imágenes

### 3. Para cada imagen:
**a) Backend usa YOLO para encontrar el grano**
- Archivo: `backend/ml/segmentation/infer_yolo_seg.py`
- Método: `YOLOSegmentationInference.get_best_prediction()`
- Genera máscara que identifica dónde está el grano

**b) Genera imagen con fondo transparente**
- Archivo: `backend/ml/segmentation/cropper.py`
- Método: `CacaoCropper.process_image()`
- Crea imagen PNG con fondo transparente del grano aislado

**c) Pasa imagen a los 4 modelos de predicción**
- Archivo: `backend/ml/prediction/predict.py`
- Método: `CacaoPredictor.predict()`
- Usa 4 modelos ResNet18 separados (uno por medida)

**d) Cada modelo predice su medida correspondiente**
- Alto (mm)
- Ancho (mm)
- Grosor (mm)
- Peso (g)

**e) Se calcula nivel de confianza**
- Se ejecuta el modelo varias veces con variaciones
- Se analiza la consistencia de los resultados

**f) Se guarda todo en base de datos**
- Archivo: `backend/api/services/analysis_service.py`
- Método: `AnalysisService._save_prediction()`
- Guarda: imagen original, imagen procesada, predicciones, confianzas, metadatos

### 4. Backend agrupa resultados
- Calcula estadísticas del lote (promedios, totales, etc.)
- Responde al frontend

### 5. Frontend muestra resultados
- Usuario ve: medidas, confianzas, imágenes procesadas, estadísticas

**Tiempo estimado:** 5-10 segundos por imagen

---

## FLUJO COMPLETO DE UN ENTRENAMIENTO

### 1. Usuario inicia entrenamiento
- Frontend envía configuración → Backend crea job → Encola tarea en Celery → Responde con job_id

### 2. Worker de Celery toma la tarea
- Actualiza estado a "en progreso"
- Archivo: `backend/api/tasks.py`
- Método: `train_model_task()` o `auto_train_model_task()`

### 3. Pipeline de entrenamiento
**a) Carga y valida dataset**
- Archivo: `backend/ml/data/dataset_loader.py`
- Método: `CacaoDatasetLoader.load_dataset()`
- Valida: CSV existe, columnas correctas, imágenes existen

**b) Genera/valida crops de todas las imágenes**
- Archivo: `backend/ml/pipeline/train_all.py`
- Método: `CacaoTrainingPipeline.load_data()`
- Genera crops automáticamente desde raw si no existen
- Valida calidad de crops existentes

**c) Normaliza los datos**
- Archivo: `backend/ml/regression/scalers.py`
- Método: `create_scalers_from_data()`
- Crea escaladores StandardScaler para cada target

**d) Divide en train/validation/test**
- Archivo: `backend/ml/pipeline/train_all.py`
- Método: `CacaoTrainingPipeline.create_stratified_split()`
- Split: 70% train, 10% validation, 20% test
- Estratificado por cuantiles de peso

**e) Entrena 4 modelos (uno por medida)**
- Archivo: `backend/ml/regression/train.py`
- Método: `train_single_model()` para cada target
- Modelo: ResNet18 pre-entrenado
- Épocas: hasta 150 (con early stopping)
- Batch size: 16-32
- Learning rate: 0.001 con scheduler

**f) Evalúa modelos con conjunto de prueba**
- Archivo: `backend/ml/pipeline/train_all.py`
- Método: `CacaoTrainingPipeline.evaluate_models()`
- Calcula: MAE, RMSE, R² para cada target

**g) Guarda modelos y escaladores**
- Archivo: `backend/ml/pipeline/train_all.py`
- Método: `CacaoTrainingPipeline.save_scalers()`
- Guarda: `{target}.pt` (modelos) y `{target}_scaler.pkl` (escaladores)
- Ubicación: `ml/artifacts/regressors/`

### 4. Durante el entrenamiento
- Frontend consulta estado cada 5 segundos
- Muestra progreso al usuario
- Archivo: `backend/training/models.py` - `TrainingJob`

### 5. Al finalizar
- Sistema actualiza estado a "completado"
- Guarda métricas de evaluación
- Frontend muestra resultados finales

**Tiempo estimado:** 2-3 horas en CPU

---

## Orden de Ejecución del Pipeline de Entrenamiento

1. **Cargar datos** (`load_data()`)
   - Carga CSV
   - Valida imágenes raw
   - Genera crops si faltan

2. **Preparar escaladores** (`create_scalers_from_data()`)
   - Ajusta escaladores con todos los datos

3. **Normalizar targets** (`scalers.transform()`)
   - Normaliza antes de dividir

4. **Crear splits** (`create_stratified_split()`)
   - Divide con targets normalizados

5. **Crear data loaders** (`create_data_loaders()`)
   - Prepara batches para entrenamiento

6. **Entrenar modelos** (`train_models()`)
   - Entrena 4 modelos individuales o 1 multi-head

7. **Guardar escaladores** (`save_scalers()`)
   - Guarda escaladores para predicción

8. **Verificar artefactos** (`_verify_artifacts_saved()`)
   - Valida que todo se guardó correctamente

9. **Evaluar modelos** (`evaluate_models()`)
   - Evalúa con conjunto de prueba

10. **Generar reportes** (`generate_reports()`)
    - Crea reportes de evaluación

---

## Puntos Clave

### Análisis:
- ✅ Lee desde raw
- ✅ Usa YOLO para segmentación
- ✅ Genera imagen transparente
- ✅ Usa 4 modelos ResNet18
- ✅ Calcula confianza
- ✅ Guarda en BD

### Entrenamiento:
- ✅ Lee desde raw
- ✅ Genera crops automáticamente
- ✅ Normaliza datos
- ✅ Divide estratificado
- ✅ Entrena 4 modelos
- ✅ Evalúa con test set
- ✅ Guarda modelos y escaladores

