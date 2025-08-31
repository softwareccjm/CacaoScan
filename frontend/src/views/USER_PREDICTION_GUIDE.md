# Guía de Uso: Vista de Predicción de Usuario (Feature 4.2)

## Descripción General

La **Vista de Predicción de Usuario** (`UserPrediction.vue`) es una implementación completa que integra los componentes `ImageUpload` y `PredictionResults` con un store de Pinia para el manejo de estado centralizado.

## Arquitectura Implementada

### 1. Store de Pinia (`stores/prediction.js`)

**Estado gestionado:**
```javascript
{
  currentPrediction: Object,    // Predicción actual
  currentImage: File,           // Imagen actual
  isLoading: Boolean,           // Estado de carga
  error: String,                // Errores
  predictions: Array,           // Historial de predicciones
  stats: Object,                // Estadísticas de sesión
  pagination: Object,           // Control de paginación
  filters: Object,              // Filtros para historial
  lastUpload: Object            // Info de última subida
}
```

**Getters principales:**
- `hasPrediction`: Verifica si hay predicción actual
- `currentConfidenceLevel`: Nivel de confianza actual
- `recentPredictions`: Últimas 5 predicciones
- `quickStats`: Estadísticas rápidas (total, promedio, etc.)

**Acciones principales:**
- `makePrediction(formData)`: Realizar nueva predicción
- `updateResults(data)`: Actualizar resultados
- `selectPrediction(id)`: Seleccionar del historial
- `loadHistory()`: Cargar historial paginado
- `clearCurrentPrediction()`: Limpiar predicción actual

### 2. Vista UserPrediction (`views/UserPrediction.vue`)

**Layout estructurado:**
```
┌─────────────────────────────────────────────────────────┐
│                    Header + Stats                       │
├──────────────────────┬──────────────────────────────────┤
│   Left Column        │         Right Column             │
│                      │                                  │
│ • ImageUpload        │ • PredictionResults              │
│ • Error Display      │   (cuando hay predicción)        │
│ • Tips Section       │                                  │
│ • Recent History     │ • Placeholder                    │
│   (móvil)            │   (cuando no hay predicción)     │
│                      │                                  │
│                      │ • Recent History (desktop)      │
│                      │ • Statistics Card                │
└──────────────────────┴──────────────────────────────────┘
```

**Funcionalidades clave:**
- ✅ **Integración completa** con store de Pinia
- ✅ **Layout responsivo** (móvil + desktop)
- ✅ **Gestión de estado** centralizada
- ✅ **Historial de predicciones** con navegación
- ✅ **Estadísticas en tiempo real**
- ✅ **Manejo de errores** unificado
- ✅ **Notificaciones de éxito**

## Flujo de Uso Completo

### 1. Inicialización
```javascript
// Al montar la vista
await predictionStore.initialize()
// - Carga historial reciente
// - Carga estadísticas
// - Actualiza stats del día
```

### 2. Subida de Imagen
```javascript
// Usuario selecciona/arrastra imagen
// ImageUpload valida y crea FormData
const formData = createImageFormData(file, metadata)

// Store realiza predicción
const result = await predictionStore.makePrediction(formData)

// Vista maneja resultado
handlePredictionResult(result)
// - Actualiza store
// - Muestra notificación de éxito
// - Renderiza PredictionResults
```

### 3. Visualización de Resultados
```javascript
// PredictionResults recibe datos del store
:prediction-data="currentPrediction"

// Datos mostrados:
// - Dimensiones físicas (ancho, alto, grosor)
// - Peso predicho
// - Nivel de confianza con indicadores visuales
// - Métricas derivadas (volumen, densidad, etc.)
// - Comparación de métodos (CNN vs regresión)
// - Acciones (descargar, compartir, guardar)
```

### 4. Gestión de Historial
```javascript
// Selección desde historial reciente
selectFromHistory(predictionId)
// - Carga predicción en vista actual
// - Muestra en PredictionResults

// Carga de más historial
loadMoreHistory()
// - Paginación automática
// - Agregado incremental al estado
```

## Integración con Componentes Existentes

### ImageUpload.vue
**Eventos manejados:**
```javascript
@prediction-result="handlePredictionResult"
@prediction-error="handlePredictionError"
```

**Flujo interno:**
1. Validación client-side
2. Creación de FormData
3. Llamada a `predictImage()` API
4. Emisión de evento con resultado

### PredictionResults.vue
**Props recibidas:**
```javascript
:prediction-data="currentPrediction"
```

**Eventos emitidos:**
```javascript
@new-analysis="handleNewAnalysis"    // Limpiar para nuevo análisis
@save-analysis="handleSaveAnalysis"  // Guardar análisis actual
```

## Configuración de Router

**Ruta registrada:**
```javascript
{
  path: '/user/prediction',
  name: 'user-prediction',
  component: UserPrediction,
  meta: {
    title: 'Predicción de Usuario | CacaoScan',
    requiresAuth: false // Configurable según necesidades
  }
}
```

**Navegación:**
```javascript
// Programática
this.$router.push('/user/prediction')

// Template
<router-link to="/user/prediction">Predicción</router-link>
```

## Manejo de Estado Reactivo

### Estado Local vs Store
```javascript
// Estado local (solo UI)
const showSuccessMessage = ref(false)
const successMessage = ref('')

// Estado del store (datos de negocio)
const currentPrediction = computed(() => predictionStore.currentPrediction)
const isLoading = computed(() => predictionStore.isLoading)
const error = computed(() => predictionStore.error)
```

### Reactividad Automática
```javascript
// Los cambios en el store se reflejan automáticamente en la UI
watch(currentPrediction, (newPrediction) => {
  if (newPrediction) {
    // Nueva predicción disponible
    console.log('Nueva predicción:', newPrediction)
  }
})
```

## Estadísticas y Métricas

### Stats en Tiempo Real
```javascript
quickStats: {
  total: 15,              // Total de análisis
  avgWeight: '1.234',     // Peso promedio
  avgConfidence: 85,      // Confianza promedio %
  highConfidenceCount: 12 // Análisis de alta confianza
}
```

### Historial Inteligente
- **Caché local**: Últimas 50 predicciones en memoria
- **Paginación**: Carga incremental por páginas
- **Filtros**: Por calidad, lote, origen, fechas
- **Persistencia**: Se mantiene durante la sesión

## Diseño Responsivo

### Breakpoints
- **Móvil** (`< 1280px`): Layout de una columna
- **Desktop** (`≥ 1280px`): Layout de dos columnas

### Adaptaciones Móviles
- Historial reciente se muestra en columna izquierda
- Estadísticas en header se ocultan
- Botones y textos se adaptan al tamaño

### Adaptaciones Desktop
- Historial en columna derecha
- Estadísticas en header visible
- Layout de dos columnas optimizado

## Notificaciones y Feedback

### Mensajes de Éxito
```javascript
showSuccess('¡Análisis completado exitosamente!')
// - Toast temporal (3 segundos)
// - Animación slide-up
// - Auto-dismiss
```

### Manejo de Errores
```javascript
// Errores de predicción
handlePredictionError(error)
// - Mostrar en banner rojo
// - Opción de cerrar manual
// - Log en consola

// Errores de store
predictionStore.setError('Mensaje de error')
// - Estado centralizado
// - Limpieza automática en éxito
```

### Estados de Carga
```javascript
// Indicador global
v-if="isLoading"
// - Spinner en header
// - Overlay en componentes
// - Disabled en botones
```

## Personalización y Extensión

### Configuración de Store
```javascript
// En stores/prediction.js
const ITEMS_PER_PAGE = 10        // Predicciones por página
const MAX_CACHE_SIZE = 50        // Máximo en caché local
const SUCCESS_MESSAGE_DURATION = 3000  // Duración de notificaciones
```

### Temas y Estilos
```css
/* Variables CSS personalizables */
:root {
  --primary-color: #10b981;     /* Verde principal */
  --success-color: #059669;     /* Verde éxito */
  --error-color: #dc2626;       /* Rojo error */
  --warning-color: #d97706;     /* Naranja advertencia */
}
```

### Extensión de Funcionalidades
```javascript
// Agregar nuevas acciones al store
actions: {
  // Exportar múltiples predicciones
  exportBatch(predictionIds) { ... },
  
  // Comparar predicciones
  comparePredictions(id1, id2) { ... },
  
  // Filtros avanzados
  advancedFilter(criteria) { ... }
}
```

## Testing y Debugging

### Estados de Prueba
```javascript
// Simular predicción de prueba
const mockPrediction = {
  id: 999,
  width: 12.5,
  height: 8.3,
  thickness: 4.2,
  predicted_weight: 1.25,
  confidence_level: 'high',
  confidence_score: 0.85
}

predictionStore.updateResults(mockPrediction)
```

### Debug del Store
```javascript
// En navegador console
// Acceder al store
const store = app.config.globalProperties.$pinia._s.get('prediction')

// Ver estado actual
console.log('Estado del store:', store.$state)

// Triggear acciones
store.makePrediction(formData)
```

### Logging
```javascript
// Logs automáticos en desarrollo
if (import.meta.env.DEV) {
  console.log('Predicción recibida:', result)
  console.log('Estado del store actualizado:', predictionStore.$state)
}
```

## Mejores Prácticas Implementadas

### Separación de Responsabilidades
- **Store**: Lógica de negocio y estado
- **Vista**: Presentación y coordinación
- **Componentes**: Funcionalidades específicas

### Gestión de Errores
- **Graceful degradation**: App funciona sin historial/stats
- **User feedback**: Mensajes claros y accionables
- **Error boundaries**: Errores no rompen la aplicación

### Performance
- **Lazy loading**: Carga incremental de historial
- **Computed properties**: Cálculos reactivos optimizados
- **Memory management**: Límite de caché para evitar memory leaks

### UX/UI
- **Loading states**: Feedback visual durante operaciones
- **Responsive design**: Funciona en todos los dispositivos
- **Accessibility**: ARIA labels y navegación por teclado

## Uso en Producción

### Variables de Entorno
```bash
# .env.production
VITE_API_URL=https://api.cacaoscan.com
VITE_ENABLE_DEBUG=false
VITE_MAX_FILE_SIZE=10485760
```

### Configuración de Autenticación
```javascript
// Habilitar autenticación
meta: {
  requiresAuth: true  // En router/index.js
}

// Guard de navegación
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
  } else {
    next()
  }
})
```

### Monitoreo y Analytics
```javascript
// En stores/prediction.js
actions: {
  makePrediction(formData) {
    // Analytics tracking
    gtag('event', 'prediction_made', {
      file_size: formData.get('image').size,
      processing_time: result.processing_time
    })
  }
}
```

## Próximos Pasos

### Funcionalidades Futuras
- **Batch processing**: Múltiples imágenes simultáneas
- **Comparación**: Comparar predicciones lado a lado
- **Exportación avanzada**: PDF, CSV con gráficos
- **Filtros inteligentes**: Búsqueda por similitud
- **Colaboración**: Compartir predicciones entre usuarios

### Optimizaciones
- **Service Worker**: Cache offline de predicciones
- **Web Workers**: Procesamiento de imágenes en background
- **PWA**: Instalación como app nativa
- **Real-time**: WebSocket para colaboración en tiempo real

---

## Ejemplo de Uso Completo

```vue
<template>
  <!-- La vista se encarga de toda la coordinación -->
  <UserPrediction />
</template>

<script>
// Solo importar y usar la vista
import UserPrediction from '@/views/UserPrediction.vue'

export default {
  components: { UserPrediction }
}
</script>
```

**URL de acceso:** `http://localhost:5173/user/prediction`

**Store disponible globalmente:**
```javascript
// En cualquier componente
import { usePredictionStore } from '@/stores/prediction.js'

const predictionStore = usePredictionStore()
console.log('Predicción actual:', predictionStore.currentPrediction)
```
