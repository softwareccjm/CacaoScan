<template>
  <!-- Vista de registro con diseño profesional mejorado -->
  <div class="auth-background min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
    <!-- Elementos decorativos de fondo animados -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Círculos decorativos verdes con animación suave -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-green-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-green-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-green-400/5 rounded-full blur-3xl animate-pulse-slow animation-delay-4000"></div>
      
      <!-- Líneas decorativas sutiles -->
      <div class="absolute top-0 left-1/4 w-px h-96 bg-gradient-to-b from-transparent via-green-500/20 to-transparent"></div>
      <div class="absolute bottom-0 right-1/4 w-px h-96 bg-gradient-to-t from-transparent via-green-500/20 to-transparent"></div>
    </div>

    <!-- Contenedor principal con animación de entrada -->
    <div class="auth-form-container w-full max-w-2xl relative z-10 animate-slide-up">
      <!-- Badge superior mejorado -->
      <div class="absolute -top-4 left-1/2 -translate-x-1/2">
        <div class="group relative bg-gradient-to-r from-green-500 to-green-600 text-white px-5 py-2 rounded-full shadow-xl flex items-center gap-2 text-sm font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300">
          <div class="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-300"></div>
          <svg class="w-4 h-4 relative z-10 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          <span class="relative z-10">Únete a CacaoScan</span>
        </div>
      </div>

      <!-- Contenido del formulario -->
      <div class="py-10 px-6 sm:px-10">
        <RegisterForm />
      </div>

      <!-- Footer decorativo mejorado -->
      <div class="border-t border-gray-200 px-6 sm:px-10 py-4 bg-gradient-to-b from-gray-50/50 to-gray-100/30 rounded-b-2xl">
        <div class="text-center space-y-3">
          <p class="text-xs text-gray-500 flex items-center justify-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
            <span class="font-medium">Datos protegidos con encriptación de nivel empresarial</span>
          </p>
          
          <div class="flex items-center justify-center gap-4 text-xs text-gray-400">
            <div class="flex items-center gap-1">
              <svg class="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span>Seguro</span>
            </div>
            <div class="flex items-center gap-1">
              <svg class="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <span>Certificado SENA</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Link de retorno mejorado -->
    <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
      <router-link 
        to="/login"
        class="group bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white hover:text-white px-5 py-2.5 rounded-full flex items-center gap-2 text-sm font-medium transition-all duration-300 border border-white/20 hover:border-white/40"
      >
        <svg class="w-4 h-4 group-hover:-translate-x-1.5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="group-hover:translate-x-0.5 transition-transform duration-300">Volver al inicio</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
/* Animaciones reutilizadas de LoginView */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 6s ease-in-out infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-slide-up {
  animation: slide-up 0.6s ease-out;
}
</style>

<script>
import RegisterForm from '@/components/auth/RegisterForm.vue';

export default {
  name: 'RegisterView',
  components: {
    RegisterForm
  }
}
</script>
