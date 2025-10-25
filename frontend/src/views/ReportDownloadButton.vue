<template>
  <button 
    @click="downloadReport" 
    class="btn btn-sm btn-outline-primary"
    :disabled="loading || !reporte.archivo_url"
    :title="reporte.archivo_url ? 'Descargar reporte' : 'Reporte no disponible'"
  >
    <i class="fas fa-download me-1" v-if="!loading"></i>
    <div class="spinner-border spinner-border-sm me-1" v-if="loading"></div>
    {{ loading ? 'Descargando...' : 'Descargar' }}
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const props = defineProps({
  reporte: {
    type: Object,
    required: true
  }
})

const authStore = useAuthStore()
const loading = ref(false)

const downloadReport = async () => {
  if (!props.reporte.archivo_url) {
    await Swal.fire({
      title: 'Error',
      text: 'El archivo del reporte no está disponible',
      icon: 'error'
    })
    return
  }

  try {
    loading.value = true
    
    const response = await fetch(`/api/reportes/${props.reporte.id}/download/`, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Error descargando el reporte')
    }
    
    // Obtener el nombre del archivo del header Content-Disposition
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `reporte_${props.reporte.id}.${props.reporte.formato}`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    // Crear blob y descargar
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    await Swal.fire({
      title: 'Descarga Completada',
      text: 'El reporte se ha descargado exitosamente',
      icon: 'success',
      timer: 2000,
      showConfirmButton: false
    })
    
  } catch (error) {
    await Swal.fire({
      title: 'Error',
      text: 'No se pudo descargar el reporte',
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.btn {
  transition: all 0.2s ease-in-out;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.spinner-border-sm {
  width: 0.875rem;
  height: 0.875rem;
}
</style>
