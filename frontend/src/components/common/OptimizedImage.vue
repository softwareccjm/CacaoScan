<template>
  <div class="optimized-image" :class="containerClass">
    <div v-if="loading" class="image-placeholder">
      <div class="skeleton-image" :style="placeholderStyle">
        <i class="fas fa-image"></i>
      </div>
    </div>
    
    <div v-else-if="error" class="image-error">
      <div class="error-content" :style="placeholderStyle">
        <i class="fas fa-exclamation-triangle"></i>
        <p>Error al cargar la imagen</p>
        <button @click="retry" class="btn btn-sm btn-outline-primary">
          <i class="fas fa-redo"></i>
          Reintentar
        </button>
      </div>
    </div>
    
    <img
      v-else
      :src="optimizedSrc"
      :alt="alt"
      :class="imageClass"
      :style="imageStyle"
      @load="onLoad"
      @error="onError"
      @click="handleClick"
      loading="lazy"
      decoding="async"
    />
    
    <!-- Overlay para acciones -->
    <div v-if="showOverlay && !loading && !error" class="image-overlay">
      <div class="overlay-content">
        <button 
          v-if="showDownload"
          @click="downloadImage"
          class="overlay-btn"
          title="Descargar imagen"
        >
          <i class="fas fa-download"></i>
        </button>
        
        <button 
          v-if="showView"
          @click="viewImage"
          class="overlay-btn"
          title="Ver imagen completa"
        >
          <i class="fas fa-expand"></i>
        </button>
        
        <button 
          v-if="showDelete"
          @click="deleteImage"
          class="overlay-btn danger"
          title="Eliminar imagen"
        >
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>
    
    <!-- Modal para vista completa -->
    <div v-if="showModal" class="image-modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
        <img :src="originalSrc" :alt="alt" class="modal-image" />
        <div class="modal-info">
          <h3>{{ alt }}</h3>
          <p v-if="imageInfo">{{ imageInfo }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'

export default {
  name: 'OptimizedImage',
  props: {
    src: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      default: ''
    },
    width: {
      type: [Number, String],
      default: null
    },
    height: {
      type: [Number, String],
      default: null
    },
    quality: {
      type: Number,
      default: 80
    },
    format: {
      type: String,
      default: 'webp',
      validator: (value) => ['webp', 'jpeg', 'png', 'avif'].includes(value)
    },
    placeholder: {
      type: String,
      default: 'blur'
    },
    showOverlay: {
      type: Boolean,
      default: false
    },
    showDownload: {
      type: Boolean,
      default: true
    },
    showView: {
      type: Boolean,
      default: true
    },
    showDelete: {
      type: Boolean,
      default: false
    },
    containerClass: {
      type: String,
      default: ''
    },
    imageClass: {
      type: String,
      default: ''
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['load', 'error', 'click', 'download', 'view', 'delete'],
  setup(props, { emit }) {
    const loading = ref(true)
    const error = ref(false)
    const showModal = ref(false)
    const imageInfo = ref('')

    // Computed properties
    const optimizedSrc = computed(() => {
      if (!props.src) return ''
      
      // Si es una URL externa, devolver tal como está
      if (props.src.startsWith('http')) {
        return props.src
      }
      
      // Generar URL optimizada
      const baseUrl = props.src.split('?')[0]
      const params = new URLSearchParams()
      
      if (props.width) params.append('w', props.width)
      if (props.height) params.append('h', props.height)
      if (props.quality) params.append('q', props.quality)
      if (props.format) params.append('f', props.format)
      
      const queryString = params.toString()
      return queryString ? `${baseUrl}?${queryString}` : baseUrl
    })

    const originalSrc = computed(() => props.src)

    const placeholderStyle = computed(() => {
      const style = {}
      if (props.width) style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
      if (props.height) style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
      return style
    })

    const imageStyle = computed(() => {
      const style = {}
      if (props.width) style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
      if (props.height) style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
      return style
    })

    // Methods
    const onLoad = (event) => {
      loading.value = false
      error.value = false
      
      // Obtener información de la imagen
      const img = event.target
      imageInfo.value = `${img.naturalWidth} × ${img.naturalHeight}`
      
      emit('load', {
        width: img.naturalWidth,
        height: img.naturalHeight,
        src: img.src
      })
    }

    const onError = (event) => {
      loading.value = false
      error.value = true
      emit('error', event)
    }

    const retry = () => {
      loading.value = true
      error.value = false
      // Forzar recarga de la imagen
      const img = document.querySelector(`img[src="${optimizedSrc.value}"]`)
      if (img) {
        img.src = img.src
      }
    }

    const handleClick = () => {
      if (props.clickable) {
        emit('click', {
          src: props.src,
          alt: props.alt
        })
      }
    }

    const downloadImage = () => {
      const link = document.createElement('a')
      link.href = props.src
      link.download = props.alt || 'imagen'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      emit('download', {
        src: props.src,
        alt: props.alt
      })
    }

    const viewImage = () => {
      showModal.value = true
      emit('view', {
        src: props.src,
        alt: props.alt
      })
    }

    const deleteImage = () => {
      emit('delete', {
        src: props.src,
        alt: props.alt
      })
    }

    const closeModal = () => {
      showModal.value = false
    }

    // Watchers
    watch(() => props.src, () => {
      loading.value = true
      error.value = false
    })

    // Lifecycle
    onMounted(() => {
      // Preload image for better performance
      if (props.src) {
        const img = new Image()
        img.onload = () => {
          // Image is preloaded
        }
        img.src = props.src
      }
    })

    return {
      loading,
      error,
      showModal,
      imageInfo,
      optimizedSrc,
      originalSrc,
      placeholderStyle,
      imageStyle,
      onLoad,
      onError,
      retry,
      handleClick,
      downloadImage,
      viewImage,
      deleteImage,
      closeModal
    }
  }
}
</script>

<style scoped>
.optimized-image {
  position: relative;
  display: inline-block;
  overflow: hidden;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.skeleton-image {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  color: #adb5bd;
}

.skeleton-image i {
  font-size: 2rem;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.error-content {
  text-align: center;
  color: #721c24;
  padding: 20px;
}

.error-content i {
  font-size: 2rem;
  margin-bottom: 10px;
}

.error-content p {
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.optimized-image img {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  transition: transform 0.2s ease;
}

.optimized-image img:hover {
  transform: scale(1.02);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.optimized-image:hover .image-overlay {
  opacity: 1;
}

.overlay-content {
  display: flex;
  gap: 10px;
}

.overlay-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #495057;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.overlay-btn:hover {
  background: white;
  transform: scale(1.1);
}

.overlay-btn.danger {
  color: #dc3545;
}

.overlay-btn.danger:hover {
  background: #dc3545;
  color: white;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2001;
}

.modal-image {
  display: block;
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.modal-info {
  padding: 20px;
  text-align: center;
}

.modal-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.modal-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
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

@media (max-width: 768px) {
  .overlay-content {
    gap: 5px;
  }
  
  .overlay-btn {
    width: 35px;
    height: 35px;
  }
  
  .modal-content {
    max-width: 95%;
    max-height: 95%;
  }
}
</style>
