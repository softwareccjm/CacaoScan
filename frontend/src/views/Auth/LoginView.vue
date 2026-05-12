<template>
  <!-- Vista de login con diseño profesional mejorado -->
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
    <div class="auth-form-container w-full max-w-md relative z-10 animate-slide-up">
      <!-- Badge superior mejorado con efecto hover -->
      <div class="absolute -top-4 left-1/2 -translate-x-1/2">
        <div class="group relative bg-gradient-to-r from-green-500 to-green-600 text-white px-5 py-2 rounded-full shadow-xl flex items-center gap-2 text-sm font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300">
          <!-- Efecto de brillo en hover -->
          <div class="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-300"></div>
          <svg class="w-4 h-4 relative z-10 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          <span class="relative z-10">Proyecto formativo SENA</span>
        </div>
      </div>

      <!-- Contenido del formulario -->
      <div class="py-10 px-6 sm:px-10">
        <LoginForm />
      </div>

    </div>

    <!-- Link de retorno mejorado con efecto hover -->
    <div class="absolute bottom-2 left-1/2 -translate-x-1/2 z-10">
      <a href="/" class="group bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white hover:text-white px-5 py-2.5 rounded-full flex items-center gap-2 text-sm font-medium transition-all duration-300 border border-white/20 hover:border-white/40">
        <svg class="w-4 h-4 group-hover:-translate-x-1.5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="group-hover:translate-x-0.5 transition-transform duration-300">Volver al inicio</span>
      </a>
    </div>
  </div>
</template>

<style scoped>
/* Animación de pulso lento para círculos decorativos */
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

/* Animación de entrada del contenedor */
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

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue'
</script>