<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <div class="text-center">
        <!-- 404 visual -->
        <div class="mb-8">
          <h1 class="text-9xl font-bold text-green-600 mb-4">404</h1>
          <div class="relative">
            <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.25a7.962 7.962 0 01-5.196-1.959m10.392 0a7.962 7.962 0 01-4.392.451 7.962 7.962 0 01-4.392-.451M15 8.25a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <!-- Hojas de cacao decorativas -->
            <svg class="absolute -top-2 -left-4 h-8 w-8 text-green-300 transform rotate-12" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.5 12c0-1.657-1.343-3-3-3s-3 1.343-3 3c0 1.657 1.343 3 3 3s3-1.343 3-3zm-3-9c-1.381 0-2.5 1.119-2.5 2.5S13.119 8 14.5 8s2.5-1.119 2.5-2.5S15.881 3.5 14.5 3.5z"/>
            </svg>
            <svg class="absolute -bottom-2 -right-4 h-6 w-6 text-green-200 transform -rotate-12" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.5 12c0-1.657-1.343-3-3-3s-3 1.343-3 3c0 1.657 1.343 3 3 3s3-1.343 3-3zm-3-9c-1.381 0-2.5 1.119-2.5 2.5S13.119 8 14.5 8s2.5-1.119 2.5-2.5S15.881 3.5 14.5 3.5z"/>
            </svg>
          </div>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          Página No Encontrada
        </h2>
        <p class="text-gray-600 mb-8">
          La página que buscas no existe o ha sido movida. 
          <br>
          ¡Pero no te preocupes! Te ayudamos a encontrar lo que necesitas.
        </p>
      </div>
    </div>

    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        
        <!-- Búsqueda rápida -->
        <div class="mb-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">¿Qué estabas buscando?</h3>
          
          <!-- Enlaces rápidos según estado de autenticación -->
          <div class="grid grid-cols-1 gap-3">
            
            <!-- Para usuarios no autenticados -->
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Página Principal</p>
                  <p class="text-sm text-gray-500">Conoce CacaoScan</p>
                </div>
              </router-link>
              
              <router-link
                to="/login"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Iniciar Sesión</p>
                  <p class="text-sm text-gray-500">Accede a tu cuenta</p>
                </div>
              </router-link>
              
              <router-link
                to="/registro"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Crear Cuenta</p>
                  <p class="text-sm text-gray-500">Únete a CacaoScan</p>
                </div>
              </router-link>
            </template>

            <!-- Para usuarios autenticados -->
            <template v-else>
              <router-link
                :to="getRedirectPath()"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h2a2 2 0 012 2v2H8V5z"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Mi Dashboard</p>
                  <p class="text-sm text-gray-500">Panel principal</p>
                </div>
              </router-link>

              <router-link
                v-if="authStore.canUploadImages"
                to="/prediccion"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Analizar Cacao</p>
                  <p class="text-sm text-gray-500">Predicción de granos</p>
                </div>
              </router-link>

              <router-link
                v-if="authStore.canViewAllPredictions"
                to="/reportes"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Reportes</p>
                  <p class="text-sm text-gray-500">Análisis de datos</p>
                </div>
              </router-link>

              <router-link
                to="/perfil"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg class="h-5 w-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <div class="text-left">
                  <p class="font-medium text-gray-900">Mi Perfil</p>
                  <p class="text-sm text-gray-500">Configuración de cuenta</p>
                </div>
              </router-link>
            </template>
          </div>
        </div>

        <!-- Información adicional -->
        <div class="border-t border-gray-200 pt-6">
          <div class="bg-green-50 rounded-lg p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-green-800">¿Necesitas ayuda?</h3>
                <div class="mt-2 text-sm text-green-700">
                  <p>Si estás buscando algo específico, estas páginas pueden ser útiles:</p>
                  <ul class="list-disc list-inside mt-2">
                    <li v-if="!authStore.isAuthenticated">Crea una cuenta para acceder a todas las funcionalidades</li>
                    <li v-else-if="!authStore.isVerified">Verifica tu email para subir imágenes</li>
                    <li>Explora el análisis de granos de cacao</li>
                    <li>Revisa tu historial de predicciones</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón principal -->
        <div class="mt-6">
          <router-link
            to="/"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Volver al Inicio
          </router-link>
        </div>
      </div>

      <!-- Footer con información -->
      <div class="mt-6 text-center text-sm text-gray-500">
        <p>¿Crees que esto es un error?</p>
        <p class="mt-1">
          La URL solicitada: 
          <code class="bg-gray-100 px-2 py-1 rounded text-xs font-mono">{{ currentPath }}</code>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Computed
const currentPath = computed(() => route.fullPath)

// Métodos
const getRedirectPath = () => {
  if (!authStore.user) return '/'

  switch (authStore.userRole) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      return '/'
  }
}
</script>
