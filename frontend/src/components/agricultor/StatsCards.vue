<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <!-- Card Lotes Totales -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Lotes Totales</h3>
          <p class="text-2xl font-bold text-gray-900">{{ totalBatches }}</p>
        </div>
      </div>
    </div>
    
    <!-- Card Calidad Promedio -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Calidad Promedio</h3>
          <p class="text-2xl font-bold text-gray-900">{{ avgQuality }}%</p>
        </div>
      </div>
    </div>
    
    <!-- Card Tasa de Defectos -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 p-6">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">Tasa de Defectos</h3>
          <p class="text-2xl font-bold text-gray-900">{{ defectRate }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsCards',
  props: {
    totalBatches: {
      type: Number,
      default: 0
    },
    avgQuality: {
      type: Number,
      default: 0
    },
    defectRate: {
      type: Number,
      default: 0
    }
  }
}
</script>

