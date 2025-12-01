<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <h1 class="text-3xl font-bold text-gray-900">Reportes</h1>
              <p class="text-gray-600 mt-1">Genera y visualiza reportes detallados de tus análisis</p>
            </div>
          </div>
        
          <!-- Reports Content -->
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <p class="text-gray-600">Funcionalidad de reportes próximamente disponible</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref } from 'vue'

// 2. Composables
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'

// 3. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// State
const activeSection = ref('reports')
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
