<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
    <div class="bg-gradient-to-r from-green-50 to-green-50 px-4 py-3 border-b border-gray-200">
      <div class="flex items-center">
        <div class="bg-green-100 p-1.5 rounded-lg mr-2">
          <svg class="text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div>
          <h2 class="text-base font-bold text-gray-900">Acciones Rápidas</h2>
          <p class="text-xs text-gray-600">Gestionar y analizar</p>
        </div>
      </div>
    </div>
    <div class="p-4 space-y-3">
      <button @click="$emit('nuevo-analisis')" class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-200 group">
        <div class="bg-green-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">Nuevo Análisis</h3>
          <p class="text-xs text-gray-600">Analizar granos de cacao</p>
        </div>
        <div class="text-green-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
      
      <button @click="$emit('gestionar-fincas')" class="w-full flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 border border-gray-200 group">
        <div class="bg-blue-500 p-2 rounded-lg flex-shrink-0">
          <svg class="text-white w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
        </div>
        <div class="flex-1 text-left">
          <h3 class="text-base font-bold text-gray-900">Gestionar Fincas</h3>
          <p class="text-xs text-gray-600">Administrar fincas y lotes</p>
        </div>
        <div class="text-blue-600 group-hover:translate-x-1 transition-transform duration-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickActions',
  emits: ['nuevo-analisis', 'gestionar-fincas']
}
</script>

