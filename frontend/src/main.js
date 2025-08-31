import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Crear la app
const app = createApp(App)

// Configurar Pinia
const pinia = createPinia()
app.use(pinia)

// Configurar router
app.use(router)

// Inicializar store de autenticación
import { useAuthStore } from '@/stores/auth'

// Función para inicializar la aplicación
const initApp = async () => {
  try {
    const authStore = useAuthStore()
    
    // Inicializar desde localStorage si hay tokens
    if (authStore.accessToken && authStore.user) {
      try {
        // Verificar que el token siga siendo válido
        await authStore.getCurrentUser()
        console.log('✅ Usuario autenticado restaurado desde localStorage')
      } catch (error) {
        console.warn('⚠️ Token inválido, limpiando localStorage')
        authStore.clearAll()
      }
    }
  } catch (error) {
    console.error('❌ Error inicializando autenticación:', error)
  }

  // Montar la aplicación
  app.mount('#app')
}

// Configurar notificaciones globales
window.showNotification = (notification) => {
  // Placeholder para sistema de notificaciones
  console.log('🔔 Notification:', notification)
  
  // Aquí se puede integrar con una librería de notificaciones
  // como vue-toastification o similar
}

// Inicializar aplicación
initApp()
