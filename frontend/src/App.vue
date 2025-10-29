<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import GlobalLoader from '@/components/common/GlobalLoader.vue'
import SessionExpiredModal from '@/components/common/SessionExpiredModal.vue'

// Referencia al modal de sesión expirada
const sessionExpiredModalRef = ref(null)

// Exponer el modal globalmente
onMounted(() => {
  window.showSessionExpiredModal = () => {
    if (sessionExpiredModalRef.value) {
      sessionExpiredModalRef.value.show()
    }
  }
})

</script>

<template>
  <div class="app">
    <!-- Router view principal -->
    <RouterView />
    
    <!-- Global loading overlay -->
    <GlobalLoader />
    
    <!-- Session expired modal -->
    <SessionExpiredModal ref="sessionExpiredModalRef" />
  </div>
</template>

<script>

export default {
  name: 'App',
}

</script>
