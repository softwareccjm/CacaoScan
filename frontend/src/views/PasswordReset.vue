<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-6.586l4.686-4.686a2 2 0 012.828 0L16 8a2 2 0 012 2z" />
        </svg>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Restablecer Contraseña
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Ingresa tu email para recibir instrucciones
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        
        <!-- Formulario de solicitud -->
        <div v-if="!emailSent">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Dirección de Email
              </label>
              <div class="mt-1">
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  autocomplete="email"
                  required
                  :disabled="isLoading"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                  :class="{ 'border-red-500': errors.email }"
                  placeholder="usuario@ejemplo.com"
                />
              </div>
              <p v-if="errors.email" class="mt-2 text-sm text-red-600">{{ errors.email }}</p>
            </div>

            <!-- Información adicional -->
            <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-blue-800">¿Cómo funciona?</h3>
                  <div class="mt-2 text-sm text-blue-700">
                    <ul class="list-disc list-inside space-y-1">
                      <li>Ingresa tu dirección de email registrada</li>
                      <li>Recibirás un enlace seguro en tu bandeja de entrada</li>
                      <li>Haz clic en el enlace para crear una nueva contraseña</li>
                      <li>El enlace expira en 1 hora por seguridad</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botón de envío -->
            <div>
              <button
                type="submit"
                :disabled="isLoading"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg
                  v-if="isLoading"
                  class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isLoading ? 'Enviando...' : 'Enviar Instrucciones' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Confirmación de envío -->
        <div v-else class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
          
          <h3 class="text-lg font-medium text-gray-900 mb-2">¡Instrucciones Enviadas!</h3>
          
          <p class="text-gray-600 mb-6">
            Si existe una cuenta con el email <strong>{{ form.email }}</strong>, 
            recibirás un enlace para restablecer tu contraseña en los próximos minutos.
          </p>

          <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800">Revisa tu bandeja de entrada</h3>
                <div class="mt-2 text-sm text-yellow-700">
                  <ul class="list-disc list-inside space-y-1">
                    <li>Busca un email de CacaoScan</li>
                    <li>Revisa también la carpeta de spam</li>
                    <li>El enlace expira en 1 hora</li>
                    <li>Si no llega el email, puedes intentar nuevamente</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="space-y-3">
            <button
              @click="sendAnother"
              :disabled="isLoading || recentlySent"
              class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {{ getResendButtonText() }}
            </button>
            
            <router-link
              to="/login"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Volver al Login
            </router-link>
          </div>

          <p v-if="recentlySent" class="mt-3 text-sm text-gray-500">
            Podrás enviar otro email en {{ countdown }} segundos
          </p>
        </div>

        <!-- Mensaje de error -->
        <div v-if="errorMessage" class="mt-4 rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ errorMessage }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enlaces adicionales -->
      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-gray-50 text-gray-500">¿Recordaste tu contraseña?</span>
          </div>
        </div>

        <div class="mt-6 text-center">
          <router-link
            to="/login"
            class="font-medium text-green-600 hover:text-green-500"
          >
            Iniciar Sesión
          </router-link>
          <span class="text-gray-300 mx-2">·</span>
          <router-link
            to="/registro"
            class="font-medium text-green-600 hover:text-green-500"
          >
            Crear Cuenta
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Estado del formulario
const form = ref({
  email: ''
})

const errors = ref({})
const emailSent = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const recentlySent = ref(false)
const countdown = ref(60)
const countdownInterval = ref(null)

// Computed
const getResendButtonText = () => {
  if (isLoading.value) return 'Enviando...'
  if (recentlySent.value) return `Esperar ${countdown.value}s`
  return 'Enviar Nuevamente'
}

// Validación
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.email.trim()) {
    errors.value.email = 'El email es requerido'
  } else if (!isValidEmail(form.value.email)) {
    errors.value.email = 'Ingresa un email válido'
  }
  
  return Object.keys(errors.value).length === 0
}

const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// Funciones
const startCountdown = () => {
  recentlySent.value = true
  countdown.value = 60
  
  countdownInterval.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      recentlySent.value = false
      clearInterval(countdownInterval.value)
    }
  }, 1000)
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.requestPasswordReset(form.value.email.trim())
    
    if (result.success) {
      emailSent.value = true
      startCountdown()
    } else {
      errorMessage.value = result.error || 'Error al enviar instrucciones'
    }
  } catch (error) {
    console.error('Error en password reset:', error)
    errorMessage.value = 'Error inesperado. Intenta nuevamente.'
  } finally {
    isLoading.value = false
  }
}

const sendAnother = async () => {
  if (isLoading.value || recentlySent.value) return
  
  await handleSubmit()
}

// Lifecycle
onMounted(() => {
  // Pre-llenar email si viene en query params
  if (route.query.email) {
    form.value.email = route.query.email
  }
  
  // Mostrar mensaje si viene en query params
  if (route.query.message) {
    errorMessage.value = route.query.message
  }
})

onUnmounted(() => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
