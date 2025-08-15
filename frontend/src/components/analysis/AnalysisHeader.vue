<template>
  <div class="px-6 py-5 border-b border-gray-200">
    <h2 class="text-2xl font-semibold text-gray-900">Detalles del Análisis #{{ analysisId }}</h2>
    <p class="mt-1 text-sm text-gray-500">{{ subtitle }}</p>
  </div>
</template>

<script>
export default {
  name: 'AnalysisHeader',
  props: {
    analysisId: {
      type: [String, Number],
      required: true
    },
    subtitle: {
      type: String,
      default: 'Resultados del análisis de calidad del lote'
    }
  }
}
</script>
