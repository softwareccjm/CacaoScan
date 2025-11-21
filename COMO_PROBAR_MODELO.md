# 🧪 Cómo Probar el Modelo Entrenado

Este documento explica las diferentes formas de probar el modelo de predicción de cacao después del entrenamiento.

---

## 📋 Opciones Disponibles

### 1️⃣ **Script Simple (Recomendado para pruebas rápidas)**

El script `backend/test_model.py` permite probar el modelo con cualquier imagen del dataset o una imagen personalizada.

#### Uso básico:

```bash
# Probar con imagen ID 497 (la que mencionaste antes)
docker compose exec backend python test_model.py 497

# O probar con cualquier otro ID
docker compose exec backend python test_model.py 123

# O probar con una ruta directa a una imagen
docker compose exec backend python test_model.py media/cacao_images/raw/497.bmp
```

#### Qué muestra el script:
- ✅ Estado de carga del modelo
- 📊 Valores reales del dataset (si la imagen está en el dataset)
- 🤖 Predicciones del modelo (alto, ancho, grosor, peso)
- 📈 Confianzas de las predicciones
- 📊 Comparación entre valores reales y predicciones (con errores)

---

### 2️⃣ **Script de Diagnóstico Avanzado**

El script `backend/test_predictions.py` proporciona información más detallada sobre el proceso de predicción, incluyendo valores normalizados.

#### Uso:

```bash
docker compose exec backend python test_predictions.py
```

**Nota:** Este script está configurado para probar con la imagen ID=1 por defecto. Puedes modificarlo para usar otro ID.

#### Qué muestra:
- Valores normalizados vs desnormalizados
- Información detallada de los escaladores
- Diagnóstico completo del proceso de predicción

---

### 3️⃣ **API REST (Para integración con frontend o pruebas desde fuera)**

Puedes usar el endpoint `/api/predict/` para probar el modelo desde cualquier cliente HTTP.

#### Endpoint:
```
POST /api/predict/
```

#### Headers requeridos:
```
Authorization: Bearer <token_jwt>
Content-Type: multipart/form-data
```

#### Body (form-data):
```
image: <archivo_imagen>
```

#### Ejemplo con cURL:

```bash
# Primero obtener token JWT (ajusta usuario/contraseña)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_usuario","password":"tu_contraseña"}' \
  | jq -r '.access')

# Luego hacer predicción
curl -X POST http://localhost:8000/api/predict/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@ruta/a/tu/imagen.jpg"
```

#### Ejemplo con Python (requests):

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'tu_usuario',
    'password': 'tu_contraseña'
})
token = response.json()['access']

# Predicción
with open('imagen.jpg', 'rb') as f:
    files = {'image': f}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://localhost:8000/api/predict/',
        files=files,
        headers=headers
    )
    
print(response.json())
```

#### Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "alto_mm": 15.23,
    "ancho_mm": 12.45,
    "grosor_mm": 8.67,
    "peso_g": 1.15,
    "confidence_alto": 0.85,
    "confidence_ancho": 0.92,
    "confidence_grosor": 0.78,
    "confidence_peso": 0.88,
    "processing_time_ms": 1234
  }
}
```

---

## 🎯 Ejemplo Práctico: Probar con la Imagen 497

Como mencionaste antes que querías probar con la imagen `497.png`, aquí está el comando exacto:

```bash
docker compose exec backend python test_model.py 497
```

O si la imagen está en una ubicación específica:

```bash
docker compose exec backend python test_model.py media/cacao_images/raw/497.bmp
```

---

## 🔍 Verificar que el Modelo se Cargó Correctamente

Si el script muestra errores al cargar el modelo, verifica que:

1. **El entrenamiento se completó exitosamente:**
   ```bash
   ls -lh backend/ml/artifacts/regressors/
   ```
   Deberías ver:
   - `hybrid.pt` (modelo híbrido)
   - `alto_scaler.pkl`, `ancho_scaler.pkl`, `grosor_scaler.pkl`, `peso_scaler.pkl`

2. **Los artefactos tienen el tamaño correcto:**
   - `hybrid.pt` debería ser ~150-200 MB
   - Los escaladores deberían ser ~1-2 KB cada uno

3. **El modelo está en el formato correcto:**
   El script `test_model.py` verificará automáticamente si los artefactos se pueden cargar.

---

## 📊 Interpretar los Resultados

### Métricas de Calidad:

- **Error absoluto:** Diferencia entre valor real y predicho
- **Error porcentual:** `(error / valor_real) * 100`
- **Confianza:** Probabilidad estimada de que la predicción sea correcta (0-1)

### Valores Esperados (según tu entrenamiento):

Basado en los resultados del entrenamiento que viste:
- **ALTO:** R² = 0.6962 (buena precisión)
- **ANCHO:** R² = 0.9285 (excelente precisión)
- **GROSOR:** R² = -0.3869 (necesita mejora)
- **PESO:** R² = 0.5815 (precisión moderada)

Esto significa que:
- ✅ **ANCHO** tiene la mejor precisión
- ✅ **ALTO** tiene buena precisión
- ⚠️ **PESO** tiene precisión moderada
- ❌ **GROSOR** necesita más trabajo (R² negativo indica que el modelo es peor que predecir la media)

---

## 🚀 Próximos Pasos

1. **Probar múltiples imágenes:**
   ```bash
   for id in 497 498 499 500; do
     echo "Probando imagen $id:"
     docker compose exec backend python test_model.py $id
     echo ""
   done
   ```

2. **Analizar errores sistemáticos:**
   - Si todas las predicciones de grosor están desviadas, puede ser un problema de calibración
   - Si el error es aleatorio, puede necesitar más datos de entrenamiento

3. **Mejorar el modelo:**
   - Re-entrenar con más épocas
   - Ajustar hiperparámetros
   - Agregar más datos de entrenamiento (especialmente para grosor)

---

## ❓ Solución de Problemas

### Error: "No se pudieron cargar los artefactos"
- Verifica que el entrenamiento se completó: `ls backend/ml/artifacts/regressors/`
- Verifica permisos de archivos
- Revisa los logs del entrenamiento

### Error: "Imagen no encontrada"
- Verifica que la imagen existe en `media/cacao_images/raw/`
- Verifica la extensión del archivo (.bmp, .png, .jpg)
- Usa la ruta completa si es necesario

### Predicciones muy incorrectas
- Verifica que el modelo entrenado es el correcto (híbrido con pixel features)
- Verifica que `pixel_calibration.json` existe y está actualizado
- Revisa que la imagen esté bien segmentada

---

¿Necesitas ayuda con algo más? 🚀

