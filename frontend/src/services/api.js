/**
 * Configuración principal de Axios para CacaoScan
 * Incluye interceptores para JWT, manejo de errores y rate limiting
 */

import axios from 'axios'
import router from '@/router'

// Configuración base de Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Variable para evitar múltiples intentos de refresh
let isRefreshing = false
let refreshSubscribers = []

// Función para subscribir requests mientras se refresca el token
const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb)
}

// Función para ejecutar todos los requests pendientes con nuevo token
const onRefreshed = (token) => {
  refreshSubscribers.map(cb => cb(token))
  refreshSubscribers = []
}

// Función para obtener el store de auth dinámicamente
const getAuthStore = () => {
  // Importación dinámica para evitar dependencias circulares
  const { useAuthStore } = require('@/stores/auth')
  return useAuthStore()
}

// Interceptor de Request
api.interceptors.request.use(
  (config) => {
    // Obtener token de localStorage
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Agregar timestamp para debugging
    config.metadata = { startTime: new Date() }

    // Log de request en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params
      })
    }

    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Interceptor de Response
api.interceptors.response.use(
  (response) => {
    // Calcular tiempo de respuesta
    const endTime = new Date()
    const duration = endTime - response.config.metadata.startTime

    // Log de response en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        duration: `${duration}ms`,
        data: response.data
      })
    }

    // Actualizar actividad del usuario
    try {
      const authStore = getAuthStore()
      if (authStore.isAuthenticated) {
        authStore.updateLastActivity()
      }
    } catch (error) {
      // Ignorar errores del store en caso de que no esté disponible
    }

    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Calcular tiempo de error
    if (originalRequest.metadata) {
      const endTime = new Date()
      const duration = endTime - originalRequest.metadata.startTime
      console.error(`❌ API Error: ${originalRequest.method?.toUpperCase()} ${originalRequest.url}`, {
        status: error.response?.status,
        duration: `${duration}ms`,
        message: error.response?.data?.detail || error.message
      })
    }

    // Manejar errores 401 (No autorizado)
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Verificar si es un endpoint de auth que no requiere refresh
      const authEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/']
      const isAuthEndpoint = authEndpoints.some(endpoint => 
        originalRequest.url.includes(endpoint)
      )

      if (isAuthEndpoint) {
        return Promise.reject(error)
      }

      // Intentar refrescar el token
      if (isRefreshing) {
        // Si ya se está refrescando, esperar el resultado
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        // Hacer request de refresh sin interceptor para evitar loop
        const refreshResponse = await axios.post(
          `${api.defaults.baseURL}/auth/refresh/`,
          { refresh: refreshToken },
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000
          }
        )

        const newAccessToken = refreshResponse.data.access

        // Actualizar token en localStorage
        localStorage.setItem('access_token', newAccessToken)

        // Actualizar header del request original
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

        // Ejecutar requests pendientes
        onRefreshed(newAccessToken)

        // Actualizar store si está disponible
        try {
          const authStore = getAuthStore()
          authStore.accessToken = newAccessToken
        } catch (storeError) {
          console.warn('No se pudo actualizar el store:', storeError)
        }

        isRefreshing = false

        // Reintento del request original
        return api(originalRequest)

      } catch (refreshError) {
        console.error('Error refrescando token:', refreshError)
        
        isRefreshing = false
        refreshSubscribers = []

        // Limpiar tokens y redirigir al login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')

        // Redirigir al login solo si no estamos ya allí
        if (router.currentRoute.value.name !== 'Login') {
          router.push({
            name: 'Login',
            query: { 
              message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
              expired: 'true'
            }
          })
        }

        return Promise.reject(refreshError)
      }
    }

    // Manejar errores 403 (Prohibido)
    if (error.response?.status === 403) {
      const errorMessage = error.response.data?.detail || 'No tienes permisos para realizar esta acción'
      
      // Mostrar notificación de error si hay sistema de notificaciones
      console.warn('🚫 Acceso denegado:', errorMessage)
      
      // Si es falta de verificación, redirigir a página de verificación
      if (errorMessage.includes('verificada')) {
        router.push({
          name: 'EmailVerification',
          query: { message: errorMessage }
        })
      }
    }

    // Manejar errores 429 (Rate Limited)
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      const errorMessage = error.response.data?.detail || 'Demasiadas solicitudes. Intenta más tarde.'
      
      console.warn('🐌 Rate limited:', errorMessage, retryAfter ? `Reintentar en ${retryAfter}s` : '')
      
      // Mostrar notificación específica para rate limiting
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'warning',
          title: 'Límite de solicitudes',
          message: errorMessage,
          duration: 5000
        })
      }
    }

    // Manejar errores 500 (Error del servidor)
    if (error.response?.status >= 500) {
      console.error('🔥 Server Error:', error.response?.data)
      
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'error',
          title: 'Error del servidor',
          message: 'Ocurrió un error interno. Por favor intenta más tarde.',
          duration: 8000
        })
      }
    }

    // Manejar errores de red
    if (!error.response) {
      console.error('🌐 Network Error:', error.message)
      
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'error',
          title: 'Error de conexión',
          message: 'No se pudo conectar al servidor. Verifica tu conexión a internet.',
          duration: 8000
        })
      }
    }

    return Promise.reject(error)
  }
)

// Función helper para crear requests con manejo de archivos
export const createFormDataRequest = (data, progressCallback) => {
  const formData = new FormData()
  
  Object.keys(data).forEach(key => {
    if (data[key] !== null && data[key] !== undefined) {
      formData.append(key, data[key])
    }
  })

  const config = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }

  if (progressCallback) {
    config.onUploadProgress = (progressEvent) => {
      const progress = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
      progressCallback(progress)
    }
  }

  return { formData, config }
}

// Función helper para manejar timeouts específicos
export const createTimeoutRequest = (timeoutMs) => {
  return axios.create({
    ...api.defaults,
    timeout: timeoutMs
  })
}

// Función helper para requests sin interceptores (útil para refresh token)
export const createBaseRequest = () => {
  return axios.create({
    baseURL: api.defaults.baseURL,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
}

// Exportar configuraciones útiles
export const API_CONFIG = {
  BASE_URL: api.defaults.baseURL,
  TIMEOUT: api.defaults.timeout,
  HEADERS: api.defaults.headers
}

export default api
