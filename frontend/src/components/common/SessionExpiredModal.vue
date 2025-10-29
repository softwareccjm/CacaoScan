<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <transition name="slide-up">
        <div
          v-if="visible"
          class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl p-8 max-w-md w-full text-center transform transition-all mx-4"
        >
          <!-- Ícono de advertencia -->
          <div class="flex justify-center mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-14 h-14 text-red-500 animate-pulse"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0z"
              />
            </svg>
          </div>

          <!-- Texto -->
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Sesión expirada
          </h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            Por seguridad, tu sesión ha expirado. Inicia sesión nuevamente para continuar.
          </p>

          <!-- Indicador de tiempo -->
          <div class="mb-6">
            <div class="text-sm text-gray-500 dark:text-gray-400">
              Redirigiendo en {{ countdown }} segundos
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
              <div
                class="bg-green-600 h-2 rounded-full transition-all duration-1000"
                :style="{ width: `${(countdown / 5) * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Botón -->
          <button
            @click="redirectToLogin"
            class="w-full px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-md transition-all duration-200 transform hover:scale-105 active:scale-95"
          >
            Iniciar sesión
          </button>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const visible = ref(false)
const countdown = ref(5)
const router = useRouter()
const authStore = useAuthStore()
let countdownInterval = null

// Función para mostrar el modal (expuesta al componente)
const show = () => {
  visible.value = true
  countdown.value = 5
  
  // Limpiar intervalo anterior si existe
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  
  // Contador regresivo
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      redirectToLogin()
    }
  }, 1000)
}

function redirectToLogin() {
  // Limpiar intervalo
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
  
  visible.value = false
  
  // Dar tiempo para la animación de salida
  setTimeout(() => {
    authStore.logout()
    router.push('/login')
  }, 300)
}

// Limpiar intervalo al desmontar
onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})

// Exponer la función show para uso externo
defineExpose({
  show
})
</script>

<script>
// Script adicional para exportar la función globalmente
export function showSessionExpiredModal(modalInstance) {
  if (modalInstance) {
    modalInstance.show()
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.4s ease-out;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>

