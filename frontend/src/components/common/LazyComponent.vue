<template>
  <div class="lazy-component" ref="container">
    <div v-if="loading" class="loading-placeholder">
      <div class="skeleton-loader">
        <div class="skeleton-header"></div>
        <div class="skeleton-content">
          <div class="skeleton-line" v-for="i in 3" :key="i"></div>
        </div>
      </div>
    </div>
    
    <div v-else-if="error" class="error-placeholder">
      <i class="fas fa-exclamation-triangle"></i>
      <p>Error al cargar el componente</p>
      <button @click="retry" class="btn btn-sm btn-outline-primary">
        <i class="fas fa-redo"></i>
        Reintentar
      </button>
    </div>
    
    <div v-else class="loaded-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'LazyComponent',
  props: {
    threshold: {
      type: Number,
      default: 0.1
    },
    rootMargin: {
      type: String,
      default: '50px'
    },
    retryDelay: {
      type: Number,
      default: 1000
    },
    maxRetries: {
      type: Number,
      default: 3
    }
  },
  emits: ['load', 'error', 'retry'],
  setup(props, { emit }) {
    const container = ref(null)
    const loading = ref(true)
    const error = ref(false)
    const retryCount = ref(0)
    const observer = ref(null)
    const isLoaded = ref(false)

    const loadComponent = async () => {
      if (isLoaded.value) return
      
      try {
        loading.value = true
        error.value = false
        
        // Simular carga asíncrona del componente
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Emitir evento de carga
        emit('load')
        
        loading.value = false
        isLoaded.value = true
        
        // Desconectar observer después de cargar
        if (observer.value) {
          observer.value.disconnect()
        }
        
      } catch (err) {
        console.error('Error loading lazy component:', err)
        error.value = true
        loading.value = false
        emit('error', err)
      }
    }

    const retry = async () => {
      if (retryCount.value >= props.maxRetries) {
        console.error('Max retries reached for lazy component')
        return
      }
      
      retryCount.value++
      emit('retry', retryCount.value)
      
      // Esperar antes de reintentar
      await new Promise(resolve => setTimeout(resolve, props.retryDelay))
      
      await loadComponent()
    }

    const setupIntersectionObserver = () => {
      if (!container.value) return

      observer.value = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting && !isLoaded.value) {
              loadComponent()
            }
          })
        },
        {
          threshold: props.threshold,
          rootMargin: props.rootMargin
        }
      )

      observer.value.observe(container.value)
    }

    onMounted(() => {
      nextTick(() => {
        setupIntersectionObserver()
      })
    })

    onUnmounted(() => {
      if (observer.value) {
        observer.value.disconnect()
      }
    })

    return {
      container,
      loading,
      error,
      retry
    }
  }
}
</script>

<style scoped>
.lazy-component {
  min-height: 200px;
}

.loading-placeholder {
  padding: 20px;
}

.skeleton-loader {
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton-header {
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  margin-bottom: 15px;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton-line:nth-child(1) { width: 100%; }
.skeleton-line:nth-child(2) { width: 80%; }
.skeleton-line:nth-child(3) { width: 60%; }

@keyframes pulse {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.error-placeholder {
  padding: 40px;
  text-align: center;
  color: #dc3545;
}

.error-placeholder i {
  font-size: 2rem;
  margin-bottom: 10px;
}

.error-placeholder p {
  margin-bottom: 15px;
  color: #6c757d;
}

.loaded-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.7rem;
}

.btn-outline-primary {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline-primary:hover {
  background-color: #3498db;
  color: white;
}
</style>
