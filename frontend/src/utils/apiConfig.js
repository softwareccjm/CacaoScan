/**
 * Configuración centralizada del API para CacaoScan
 * 
 * Maneja la URL del API en diferentes entornos:
 * - Producción: Runtime injection o build-time variable
 * - Desarrollo: localhost
 * 
 * Prioridad de configuración:
 * 1. Runtime injection (window.__API_BASE_URL__) - mejor para producción
 * 2. Build-time variable (VITE_API_BASE_URL) - para builds estáticos
 * 3. Fallback localhost - solo para desarrollo local
 */

/**
 * Obtiene la URL base del API con prioridad correcta
 * @returns {string} URL base del API
 */
export const getApiBaseUrl = () => {
  // URL absoluta del backend en producción (fallback seguro)
  const PRODUCTION_BACKEND_URL = 'https://cacaoscan-backend.onrender.com/api/v1'
  
  // Prioridad 1: Runtime injection (mejor para producción, permite cambios sin rebuild)
  if (typeof globalThis !== 'undefined' && globalThis.__API_BASE_URL__) {
    let url = globalThis.__API_BASE_URL__
    console.log('🌐 [API Config] Runtime API URL encontrada:', url)
    
    // Validar y corregir si es relativa
    if (url.startsWith('http://') || url.startsWith('https://')) {
      console.log('✅ [API Config] Using runtime API URL:', url)
      return url
    }
    
    console.error('❌ [API Config] Runtime URL es relativa, corrigiendo...')
    // Si es relativa, construir URL absoluta
    if (url.startsWith('/')) {
      // Es una ruta absoluta relativa al dominio actual
      url = `https://${globalThis.location.hostname}${url}`
      console.warn('⚠️ [API Config] Construida URL desde ruta relativa:', url)
      return url
    }
    
    // Usar fallback de producción
    console.warn('⚠️ [API Config] Usando fallback de producción:', PRODUCTION_BACKEND_URL)
    return PRODUCTION_BACKEND_URL
  }
  
  // Prioridad 2: Build-time variable (Vite inyecta esto durante el build)
  if (import.meta.env.VITE_API_BASE_URL) {
    let url = import.meta.env.VITE_API_BASE_URL
    console.log('🔧 [API Config] Build-time API URL encontrada:', url)
    
    // Validar y corregir si es relativa
    if (url.startsWith('http://') || url.startsWith('https://')) {
      console.log('✅ [API Config] Using build-time API URL:', url)
      return url
    }
    
    console.error('❌ [API Config] Build-time URL es relativa, usando fallback')
    return PRODUCTION_BACKEND_URL
  }
  
  // Prioridad 3: Detectar si estamos en producción y usar URL absoluta
  if (typeof globalThis !== 'undefined' && globalThis.location && globalThis.location.hostname.includes('localhost') === false) {
    console.log('🌍 [API Config] Detectado entorno de producción, usando URL absoluta del backend')
    return PRODUCTION_BACKEND_URL
  }
  
  // Prioridad 4: Fallback para desarrollo local
  const devUrl = 'http://localhost:8000/api/v1'
  console.warn('⚠️ [API Config] Using development fallback URL:', devUrl)
  console.warn('⚠️ [API Config] globalThis.__API_BASE_URL__:', typeof globalThis !== 'undefined' ? globalThis.__API_BASE_URL__ : 'N/A')
  console.warn('⚠️ [API Config] VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL || 'N/A')
  const hostname = typeof globalThis !== 'undefined' && globalThis.location ? globalThis.location.hostname : 'N/A'
  console.warn('⚠️ [API Config] globalThis.location.hostname:', hostname)
  return devUrl
}

/**
 * Obtiene la URL base del API sin el path /api/v1
 * Útil para servicios que construyen sus propias rutas
 * @returns {string} URL base del API sin /api/v1
 */
export const getApiBaseUrlWithoutPath = () => {
  const baseUrl = getApiBaseUrl()
  // Remover /api/v1 si está presente
  return baseUrl.replace(/\/api\/v1\/?$/, '')
}

/**
 * Obtiene la URL base del API con /api/v1
 * Asegura que siempre termine con /api/v1
 * @returns {string} URL base del API con /api/v1
 */
export const getApiBaseUrlWithPath = () => {
  const baseUrl = getApiBaseUrl()
  // Si ya termina con /api/v1, retornar tal cual
  if (baseUrl.endsWith('/api/v1') || baseUrl.endsWith('/api/v1/')) {
    return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
  }
  // Si no, agregar /api/v1
  return `${baseUrl.replace(/\/$/, '')}/api/v1`
}

/**
 * Detecta si estamos en modo desarrollo
 * @returns {boolean} true si está en desarrollo
 */
export const isDevelopment = () => {
  return import.meta.env.DEV || 
         import.meta.env.MODE === 'development' ||
         (typeof globalThis !== 'undefined' && globalThis.location && globalThis.location.hostname === 'localhost')
}

/**
 * Detecta si estamos en modo producción
 * @returns {boolean} true si está en producción
 */
export const isProduction = () => {
  return import.meta.env.PROD || 
         import.meta.env.MODE === 'production' ||
         (typeof globalThis !== 'undefined' && globalThis.location && globalThis.location.hostname.includes('localhost') === false)
}

// Exportar configuración actual para debugging
export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  baseUrlWithoutPath: getApiBaseUrlWithoutPath(),
  baseUrlWithPath: getApiBaseUrlWithPath(),
  isDev: isDevelopment(),
  isProd: isProduction(),
  runtimeUrl: typeof globalThis !== 'undefined' ? globalThis.__API_BASE_URL__ : null,
  buildTimeUrl: import.meta.env.VITE_API_BASE_URL || null,
}

// Log de configuración en desarrollo
if (isDevelopment()) {
  console.log('📋 API Configuration:', API_CONFIG)
}

