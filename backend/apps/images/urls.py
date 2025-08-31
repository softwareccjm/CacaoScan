"""
Configuración de URLs para la app de imágenes de cacao.

Define las rutas para los endpoints de predicción e historial de imágenes.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CacaoImagePredictionView, CacaoImageViewSet

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r'', CacaoImageViewSet, basename='cacaoimage')

# Nombre de la aplicación para namespacing
app_name = 'images'

urlpatterns = [
    # Endpoint específico para predicción
    path('predict/', CacaoImagePredictionView.as_view(), name='predict'),
    
    # Endpoints del ViewSet (CRUD completo)
    # GET /api/images/ - Lista todas las imágenes
    # POST /api/images/ - Crea nueva imagen (sin predicción)
    # GET /api/images/{id}/ - Obtiene imagen específica
    # PUT/PATCH /api/images/{id}/ - Actualiza imagen
    # DELETE /api/images/{id}/ - Elimina imagen
    # GET /api/images/stats/ - Estadísticas de predicciones
    path('', include(router.urls)),
]

"""
Estructura de URLs resultante:

POST /api/images/predict/
    - Sube imagen y realiza predicción completa
    - Guarda en BD y devuelve resultados ML
    - Formato respuesta: {"id": 1, "width": ..., "height": ..., etc.}

GET /api/images/
    - Lista todas las predicciones realizadas
    - Soporta filtros: ?processed=true&quality=good&batch=001
    - Paginación automática
    - Formato respuesta: {"count": N, "results": [...]}

GET /api/images/{id}/
    - Obtiene detalles completos de una predicción específica
    - Incluye métricas derivadas y metadatos
    - Formato respuesta: CacaoImageSerializer completo

GET /api/images/stats/
    - Estadísticas globales de predicciones
    - Total, hoy, tiempo promedio, distribución calidad
    - Formato respuesta: {"total_predictions": N, "avg_processing_time": X, ...}

PUT/PATCH /api/images/{id}/
    - Actualiza metadatos de imagen (batch_number, origin, notes)
    - Los campos de predicción son read-only
    - Para rehacer predicción usar POST /api/images/{id}/reprocess/

DELETE /api/images/{id}/
    - Elimina imagen y registro de BD
    - Acción irreversible

Filtros soportados en GET /api/images/:
- processed=true/false - Solo imágenes procesadas/no procesadas
- quality=excellent/good/fair/poor - Filtrar por calidad predicha
- batch=XXX - Filtrar por número de lote
- date_from=YYYY-MM-DD - Desde fecha
- date_to=YYYY-MM-DD - Hasta fecha

Ejemplo de uso:
GET /api/images/?processed=true&quality=excellent&date_from=2024-01-01
"""
