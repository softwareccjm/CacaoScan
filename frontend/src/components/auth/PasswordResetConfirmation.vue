<template>
  <!-- Confirmación de envío con diseño mejorado -->
  <div class="text-center">
    <!-- Ícono de confirmación animado -->
    <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-gradient-to-br from-green-500 to-green-600 mb-6 mx-auto shadow-lg animate-bounce-light">
      <svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    </div>
    
    <h3 class="text-2xl font-bold text-gray-900 mb-3">¡Instrucciones Enviadas!</h3>
    
    <p class="text-gray-600 mb-8 leading-relaxed">
      Si existe una cuenta con el email <span class="font-semibold text-green-600">{{ email }}</span>, 
      recibirás un enlace para restablecer tu contraseña en los próximos minutos.
    </p>

    <!-- Alerta de información con mejor diseño -->
    <div class="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl p-6 mb-8 shadow-sm">
      <div class="flex items-start gap-4">
        <div class="flex-shrink-0">
          <div class="w-10 h-10 bg-yellow-100 rounded-xl flex items-center justify-center">
            <svg class="h-5 w-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-yellow-900 mb-3">Revisa tu bandeja de entrada</h3>
          <ul class="space-y-2 text-sm text-yellow-800">
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Busca un email de CacaoScan</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Revisa también la carpeta de spam</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>El enlace expira en 1 hora</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Si no llega el email, puedes intentar nuevamente</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Botones de acción mejorados -->
    <div class="space-y-3">
      <button
        @click="$emit('resend')"
        :disabled="isLoading || recentlySent"
        class="w-full flex justify-center items-center gap-2 py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm text-base font-semibold text-gray-700 bg-white hover:bg-gray-50 hover:border-green-300 focus:outline-none focus:ring-4 focus:ring-green-500/30 transition-all duration-200 hover:shadow-md active:scale-[0.97] disabled:opacity-50 group"
      >
        <svg v-if="!isLoading && !recentlySent" class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{{ buttonText }}</span>
      </button>
      
      <router-link
        to="/login"
        class="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
      >
        <svg class="w-5 h-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
        <span>Volver al Login</span>
      </router-link>
    </div>

    <!-- Contador de tiempo -->
    <Transition
      enter-active-class="transform ease-out duration-200"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <p v-if="recentlySent" class="mt-4 text-sm text-gray-500 flex items-center justify-center gap-2">
        <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Podrás enviar otro email en <span class="font-bold text-green-600">{{ countdown }}</span> segundos
      </p>
    </Transition>
  </div>
</template>

<script setup>
defineProps({
  email: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  recentlySent: {
    type: Boolean,
    default: false
  },
  countdown: {
    type: Number,
    default: 0
  },
  buttonText: {
    type: String,
    default: 'Enviar Nuevamente'
  }
})

defineEmits(['resend'])
</script>

<style scoped>
@keyframes bounce-light {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-light {
  animation: bounce-light 2s ease-in-out infinite;
}
</style>

