<template>
  <div class="card">
    <div class="card-header">
      <h5 class="mb-0">
        <i class="fas fa-file-alt me-2"></i>
        Generador de Reportes
      </h5>
    </div>
    <div class="card-body">
      <form @submit.prevent="generateReport">
        <div class="row">
          <!-- Tipo de Reporte -->
          <div class="col-md-6 mb-3">
            <label for="tipoReporte" class="form-label">Tipo de Reporte</label>
            <select 
              id="tipoReporte" 
              v-model="form.tipo_reporte" 
              class="form-select"
              required
            >
              <option value="">Seleccionar tipo...</option>
              <option value="calidad">Reporte de Calidad</option>
              <option value="defectos">Reporte de Defectos</option>
              <option value="rendimiento">Reporte de Rendimiento</option>
              <option value="finca">Reporte de Finca</option>
              <option value="lote">Reporte de Lote</option>
              <option value="usuario">Reporte de Usuario</option>
              <option value="auditoria">Reporte de Auditoría</option>
            </select>
          </div>

          <!-- Formato -->
          <div class="col-md-6 mb-3">
            <label for="formato" class="form-label">Formato</label>
            <select 
              id="formato" 
              v-model="form.formato" 
              class="form-select"
              required
            >
              <option value="">Seleccionar formato...</option>
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="csv">CSV</option>
            </select>
          </div>
        </div>

        <!-- Título -->
        <div class="mb-3">
          <label for="titulo" class="form-label">Título del Reporte</label>
          <input 
            type="text" 
            id="titulo" 
            v-model="form.titulo" 
            class="form-control"
            placeholder="Ingrese el título del reporte"
            required
          >
        </div>

        <!-- Descripción -->
        <div class="mb-3">
          <label for="descripcion" class="form-label">Descripción (Opcional)</label>
          <textarea 
            id="descripcion" 
            v-model="form.descripcion" 
            class="form-control"
            rows="3"
            placeholder="Descripción adicional del reporte"
          ></textarea>
        </div>

        <!-- Filtros -->
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="fechaDesde" class="form-label">Fecha Desde</label>
            <input 
              type="date" 
              id="fechaDesde" 
              v-model="form.filtros.fecha_desde" 
              class="form-control"
            >
          </div>
          <div class="col-md-6 mb-3">
            <label for="fechaHasta" class="form-label">Fecha Hasta</label>
            <input 
              type="date" 
              id="fechaHasta" 
              v-model="form.filtros.fecha_hasta" 
              class="form-control"
            >
          </div>
        </div>

        <!-- Finca (si aplica) -->
        <div class="mb-3" v-if="showFincaFilter">
          <label for="finca" class="form-label">Finca</label>
          <select 
            id="finca" 
            v-model="form.filtros.finca_id" 
            class="form-select"
          >
            <option value="">Todas las fincas</option>
            <option 
              v-for="finca in fincas" 
              :key="finca.id" 
              :value="finca.id"
            >
              {{ finca.nombre }}
            </option>
          </select>
        </div>

        <!-- Lote (si aplica) -->
        <div class="mb-3" v-if="showLoteFilter">
          <label for="lote" class="form-label">Lote</label>
          <select 
            id="lote" 
            v-model="form.filtros.lote_id" 
            class="form-select"
          >
            <option value="">Todos los lotes</option>
            <option 
              v-for="lote in lotes" 
              :key="lote.id" 
              :value="lote.id"
            >
              {{ lote.identificador }} - {{ lote.variedad }}
            </option>
          </select>
        </div>

        <!-- Botones -->
        <div class="d-flex justify-content-end gap-2">
          <button 
            type="button" 
            @click="resetForm" 
            class="btn btn-outline-secondary"
          >
            <i class="fas fa-undo me-2"></i>
            Limpiar
          </button>
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="loading"
          >
            <i class="fas fa-file-alt me-2"></i>
            {{ loading ? 'Generando...' : 'Generar Reporte' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Reactive data
const loading = ref(false)
const fincas = ref([])
const lotes = ref([])

// Form data
const form = reactive({
  tipo_reporte: '',
  formato: '',
  titulo: '',
  descripcion: '',
  filtros: {
    fecha_desde: '',
    fecha_hasta: '',
    finca_id: '',
    lote_id: '',
    usuario_id: ''
  }
})

// Computed
const showFincaFilter = computed(() => {
  return ['finca', 'lote', 'calidad', 'defectos', 'rendimiento'].includes(form.tipo_reporte)
})

const showLoteFilter = computed(() => {
  return ['lote', 'calidad', 'defectos'].includes(form.tipo_reporte)
})

// Methods
const generateReport = async () => {
  try {
    loading.value = true
    
    // Validar fechas
    if (form.filtros.fecha_desde && form.filtros.fecha_hasta) {
      if (new Date(form.filtros.fecha_desde) > new Date(form.filtros.fecha_hasta)) {
        throw new Error('La fecha desde no puede ser mayor a la fecha hasta')
      }
    }
    
    await Swal.fire({
      title: 'Generando Reporte',
      text: 'Se está generando el reporte, esto puede tomar unos minutos...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
    
    const response = await fetch('/api/reportes/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tipo_reporte: form.tipo_reporte,
        formato: form.formato,
        titulo: form.titulo,
        descripcion: form.descripcion,
        filtros_aplicados: form.filtros
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Error generando reporte')
    }
    
    const reporte = await response.json()
    
    await Swal.fire({
      title: 'Reporte Generado',
      text: 'El reporte se ha generado exitosamente',
      icon: 'success',
      confirmButtonText: 'Ver Reportes'
    }).then(() => {
      // Emitir evento para que el componente padre actualice la lista
      window.dispatchEvent(new CustomEvent('reporte-generado', { 
        detail: reporte 
      }))
    })
    
    resetForm()
    
  } catch (error) {
    await Swal.fire({
      title: 'Error',
      text: error.message,
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.tipo_reporte = ''
  form.formato = ''
  form.titulo = ''
  form.descripcion = ''
  form.filtros = {
    fecha_desde: '',
    fecha_hasta: '',
    finca_id: '',
    lote_id: '',
    usuario_id: ''
  }
}

const loadFincas = async () => {
  try {
    const response = await fetch('/api/fincas/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      fincas.value = data.results || []
    }
  } catch (error) {
    console.error('Error cargando fincas:', error)
  }
}

const loadLotes = async () => {
  try {
    const response = await fetch('/api/lotes/', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      lotes.value = data.results || []
    }
  } catch (error) {
    console.error('Error cargando lotes:', error)
  }
}

// Watchers
watch(() => form.tipo_reporte, (newType) => {
  // Generar título automático basado en el tipo
  if (newType && !form.titulo) {
    const titulos = {
      calidad: 'Reporte de Calidad de Granos',
      defectos: 'Reporte de Defectos Detectados',
      rendimiento: 'Reporte de Rendimiento',
      finca: 'Reporte de Finca',
      lote: 'Reporte de Lote',
      usuario: 'Reporte de Usuario',
      auditoria: 'Reporte de Auditoría'
    }
    form.titulo = titulos[newType] || ''
  }
})

watch(() => form.filtros.finca_id, (fincaId) => {
  // Limpiar lote cuando cambia la finca
  if (fincaId) {
    form.filtros.lote_id = ''
  }
})

// Lifecycle
onMounted(() => {
  loadFincas()
  loadLotes()
})
</script>

<style scoped>
.form-label {
  font-weight: 600;
  color: #495057;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.btn {
  transition: all 0.2s ease-in-out;
}

.btn:hover {
  transform: translateY(-1px);
}
</style>
