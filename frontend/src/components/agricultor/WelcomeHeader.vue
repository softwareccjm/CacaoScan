<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8">
    <div class="flex items-center justify-between">
      <div class="flex items-center">
        <div class="bg-green-100 p-3 rounded-xl mr-4">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
          </svg>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">¡Bienvenido a CacaoScan, {{ farmerName }}!</h1>
          <p class="text-gray-600 mt-1">Su herramienta para asegurar la calidad de cada grano</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WelcomeHeader',
  props: {
    farmerName: {
      type: String,
      required: true
    }
  }
}
</script>

