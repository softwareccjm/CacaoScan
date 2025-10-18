# 🧠 Entrenamiento Incremental YOLOv8 - CacaoScan

Sistema de aprendizaje continuo que permite al modelo YOLOv8 mejorar con nuevos datos sin reiniciar el entrenamiento completo.

## 🎯 Características Principales

### ✅ Entrenamiento Incremental
- **Aprendizaje continuo**: El modelo mejora con cada nueva muestra
- **Sin reinicio**: No necesita reentrenar desde cero
- **Tiempo optimizado**: 30-60 segundos por muestra vs horas de entrenamiento completo
- **Preservación de conocimiento**: Mantiene el conocimiento previo del modelo

### ✅ Gestión de Datos
- **Almacenamiento automático**: Imágenes guardadas en `media/cacao_images/new/`
- **Actualización de dataset**: `dataset.csv` se actualiza automáticamente
- **Backup automático**: Respaldo antes de cada actualización
- **Validación robusta**: Verificación de datos antes del entrenamiento

### ✅ Interfaz de Usuario
- **Vista dedicada**: `/entrenamiento-incremental`
- **Formulario intuitivo**: Subida de imagen + datos del grano
- **Progreso en tiempo real**: Indicador de progreso del entrenamiento
- **Historial de entrenamientos**: Seguimiento de mejoras del modelo

## 🚀 Uso del Sistema

### 1. Frontend Vue.js

#### Acceder a la Vista
```bash
# Navegar a la vista de entrenamiento incremental
http://localhost:3000/entrenamiento-incremental
```

#### Subir Nueva Muestra
1. **Seleccionar imagen**: Arrastrar y soltar o hacer clic para seleccionar
2. **Ingresar datos del grano**:
   - ID de la muestra (número único)
   - Dimensiones reales (alto, ancho, grosor en mm)
   - Peso real (en gramos)
3. **Información adicional** (opcional):
   - Número de lote
   - Origen del grano
   - Notas
4. **Entrenar modelo**: Hacer clic en "Entrenar Modelo"

#### Ver Resultados
- **Progreso**: Barra de progreso durante el entrenamiento
- **Estadísticas**: Mejoras en precisión y reducción de pérdida
- **Historial**: Lista de entrenamientos recientes

### 2. API REST

#### Endpoint Principal
```bash
POST /api/ml/train/incremental-weight/
Content-Type: multipart/form-data

# Parámetros requeridos:
- image: archivo de imagen
- data: JSON con datos del grano

# Parámetros opcionales:
- batch_number: número de lote
- origin: origen del grano
- notes: notas adicionales
```

#### Ejemplo de Uso
```javascript
// Crear FormData
const formData = new FormData()
formData.append('image', imageFile)
formData.append('data', JSON.stringify({
    id: 511,
    alto: 22.5,
    ancho: 14.8,
    grosor: 7.2,
    peso: 1.95
}))

// Realizar solicitud
const response = await fetch('/api/ml/train/incremental-weight/', {
    method: 'POST',
    body: formData,
    headers: {
        'Authorization': `Bearer ${token}`
    }
})

const result = await response.json()
```

#### Respuesta del API
```json
{
    "success": true,
    "message": "Modelo actualizado exitosamente",
    "training_stats": {
        "new_samples": 1,
        "total_samples": 511,
        "training_time": 45.2,
        "accuracy_improvement": 0.02,
        "loss_reduction": 0.05,
        "epochs_completed": 5,
        "method": "incremental"
    },
    "dataset_info": {
        "current_size": 511,
        "last_updated": "2024-01-15T10:30:00Z",
        "next_id": 512
    },
    "image_info": {
        "id": 511,
        "filename": "511.bmp",
        "path": "/path/to/image",
        "database_id": 123
    }
}
```

## 🔧 Configuración Técnica

### Backend (Django)

#### Estructura de Archivos
```
backend/
├── apps/ml/
│   ├── views.py              # IncrementalTrainingView
│   ├── urls.py               # Rutas del módulo ML
│   └── apps.py               # Configuración de la app
├── ml/
│   ├── prepare_yolo_data.py  # Preparación de datos incrementales
│   ├── train_yolo.py         # Entrenamiento incremental
│   └── demo_incremental_training.py  # Script de demostración
└── config/
    ├── urls.py               # URLs principales
    └── settings.py           # Configuración Django
```

#### Configuración de URLs
```python
# config/urls.py
urlpatterns = [
    path('api/ml/', include('apps.ml.urls', namespace='ml')),
]

# apps/ml/urls.py
urlpatterns = [
    path('train/incremental-weight/', IncrementalTrainingView.as_view()),
]
```

#### Configuración de Apps
```python
# config/settings.py
INSTALLED_APPS = [
    'apps.ml.apps.MLConfig',
]
```

### Frontend (Vue.js)

#### Estructura de Archivos
```
frontend/src/
├── views/
│   └── SubirDatosEntrenamiento.vue  # Vista principal
├── services/
│   └── incrementalTrainingApi.js    # API service
└── router/
    └── index.js                     # Rutas
```

#### Configuración de Rutas
```javascript
// router/index.js
{
    path: '/entrenamiento-incremental',
    name: 'SubirDatosEntrenamiento',
    component: SubirDatosEntrenamiento,
    beforeEnter: ROUTE_GUARDS.canUpload,
    meta: {
        title: 'Entrenamiento Incremental | CacaoScan',
        requiresVerification: true
    }
}
```

## 📊 Proceso de Entrenamiento

### 1. Validación de Datos
- **Imagen**: Formato, tamaño, contenido válido
- **Datos del grano**: Campos requeridos, rangos válidos
- **ID único**: Verificación de que no exista en el dataset

### 2. Almacenamiento
- **Imagen**: Guardada en `media/cacao_images/new/{id}.bmp`
- **Base de datos**: Registro en `CacaoImage` y `CacaoImageAnalysis`
- **Dataset**: Actualización de `dataset.csv` con backup automático

### 3. Preparación de Datos
- **Anotaciones YOLO**: Generación automática de bounding boxes
- **Configuración**: Archivo YAML para entrenamiento incremental
- **Validación**: Verificación de datos preparados

### 4. Entrenamiento Incremental
- **Carga del modelo**: Modelo previamente entrenado
- **Parámetros optimizados**: Learning rate bajo, pocas épocas
- **Entrenamiento**: Ajuste fino con nuevos datos
- **Validación**: Métricas de mejora del modelo

### 5. Actualización del Modelo
- **Guardado**: Modelo actualizado reemplaza el anterior
- **Métricas**: Cálculo de mejoras en precisión y pérdida
- **Respuesta**: Estadísticas del entrenamiento al usuario

## 🧪 Pruebas y Demostración

### Script de Demostración
```bash
# Ejecutar demostración completa
python backend/ml/demo_incremental_training.py
```

### Pruebas Manuales
1. **Preparar datos de prueba**:
   - Imágenes de granos de cacao
   - Datos reales de dimensiones y peso

2. **Ejecutar entrenamiento**:
   - Subir imagen y datos
   - Monitorear progreso
   - Verificar resultados

3. **Validar mejoras**:
   - Comparar métricas antes/después
   - Probar predicciones con modelo actualizado
   - Verificar persistencia de datos

## 🔒 Seguridad y Validación

### Validaciones Implementadas
- **Autenticación**: Token JWT requerido
- **Permisos**: Solo usuarios verificados pueden entrenar
- **Rate limiting**: Límite de solicitudes por usuario
- **Validación de datos**: Rangos y formatos válidos
- **Sanitización**: Limpieza de archivos subidos

### Manejo de Errores
- **Errores de validación**: Mensajes claros al usuario
- **Errores de entrenamiento**: Rollback automático
- **Errores de red**: Reintentos y timeouts
- **Logging**: Registro detallado para debugging

## 📈 Monitoreo y Métricas

### Métricas Disponibles
- **Tiempo de entrenamiento**: Duración por muestra
- **Mejora en precisión**: Incremento en mAP
- **Reducción de pérdida**: Disminución en loss
- **Tamaño del dataset**: Número total de muestras
- **Frecuencia de actualizaciones**: Entrenamientos por día

### Dashboard de Estadísticas
- **Muestras totales**: Contador de muestras en dataset
- **Actualizaciones**: Número de entrenamientos incrementales
- **Precisión actual**: Precisión del modelo actual
- **Historial**: Lista de entrenamientos recientes

## 🚀 Próximos Pasos

### Mejoras Planificadas
1. **Entrenamiento en lote**: Múltiples muestras simultáneas
2. **Validación cruzada**: Verificación automática de calidad
3. **Notificaciones**: Alertas de entrenamiento completado
4. **Métricas avanzadas**: Análisis de tendencias del modelo
5. **Optimización**: Entrenamiento más rápido y eficiente

### Integración con Producción
1. **CI/CD**: Automatización de despliegues
2. **Monitoreo**: Métricas en tiempo real
3. **Escalabilidad**: Soporte para múltiples usuarios
4. **Backup**: Estrategias de respaldo robustas
5. **Documentación**: Guías de usuario y administrador

## 📚 Recursos Adicionales

### Documentación Relacionada
- [YOLOv8 Integration Guide](../YOLOV8_README.md)
- [Smart Weight Prediction](../prediction/README.md)
- [API Documentation](../../api/docs/)

### Enlaces Útiles
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js Documentation](https://vuejs.org/)

---

**¡El modelo YOLOv8 ahora puede aprender continuamente de nuevos datos!** 🍫⚖️🧠
