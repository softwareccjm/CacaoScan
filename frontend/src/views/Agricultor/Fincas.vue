<template>
  <div class="farmer-dashboard-container">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="farmerName"
      :user-role="'agricultor'"
      :current-route="''"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="logout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <main class="dashboard-main" :class="isSidebarCollapsed ? 'ml-20' : 'ml-64'">
      <div class="dashboard-section">
        <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900">Gestión de Fincas</h1>
            <p class="text-gray-600 mt-1">Administra y monitorea tus fincas y lotes de cacao</p>
          </div>
        </div>

        <!-- Fincas Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-xl border border-gray-200 shadow-md overflow-hidden hover:shadow-lg transition-all duration-300">
            <div class="p-6">
              <div class="flex items-center">
                <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mr-4">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider">Total Fincas</p>
                  <p class="text-2xl font-bold text-gray-900">{{ fincasStats.totalFincas }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 shadow-md overflow-hidden hover:shadow-lg transition-all duration-300">
            <div class="p-6">
              <div class="flex items-center">
                <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mr-4">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider">Lotes Activos</p>
                  <p class="text-2xl font-bold text-gray-900">{{ fincasStats.totalLotes }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 shadow-md overflow-hidden hover:shadow-lg transition-all duration-300">
            <div class="p-6">
              <div class="flex items-center">
                <div class="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center mr-4">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-600 uppercase tracking-wider">Área Total</p>
                  <p class="text-2xl font-bold text-gray-900">{{ fincasStats.areaTotal }} ha</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-6">Acciones Rápidas</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button 
              @click="handleNuevaFinca"
              class="bg-green-600 hover:bg-green-700 text-white rounded-lg p-6 text-left transition-all duration-200 shadow-md hover:shadow-lg"
            >
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center mr-3">
                  <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                </div>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Registrar Nueva Finca</h3>
              <p class="text-white/80 text-sm">Agrega una nueva finca a tu portafolio</p>
            </button>

            <button 
              @click="handleMonitorearLotes"
              class="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-6 text-left transition-all duration-200 shadow-md hover:shadow-lg"
            >
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center mr-3">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Monitorear Lotes</h3>
              <p class="text-white/80 text-sm">Visualiza el estado y rendimiento de tus lotes</p>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Sidebar from '@/components/layout/Common/Sidebar.vue';

export default {
  name: 'Fincas',
  components: {
    Sidebar
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    const activeSection = ref('fincas');
    
    const farmerName = computed(() => authStore.userFullName || 'Usuario');
    
    const fincasStats = ref({
      totalFincas: 0,
      totalLotes: 0,
      areaTotal: 0
    });

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        isSidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    const handleMenuClick = (item) => {
      if (item.route && item.route !== null) {
        // Don't navigate if we're already on that route
        const currentPath = router.currentRoute.value.path;
        if (currentPath !== item.route) {
          router.push(item.route);
        }
      } else {
        // For items without routes (internal dashboard sections), navigate to dashboard with query param
        const currentName = router.currentRoute.value.name;
        if (currentName !== 'AgricultorDashboard') {
          router.push({ 
            name: 'AgricultorDashboard',
            query: { section: item.id }
          });
        }
      }
    };

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    const logout = async () => {
      try {
        await authStore.logout();
      } catch (error) {
        console.error('Error al cerrar sesión:', error);
        authStore.clearAll();
      }
    };

    const handleNuevaFinca = () => {
      alert('Funcionalidad de registrar nueva finca próximamente');
    };

    const handleMonitorearLotes = () => {
      alert('Funcionalidad de monitorear lotes próximamente');
    };

    return {
      isSidebarCollapsed,
      activeSection,
      farmerName,
      fincasStats,
      checkScreenSize,
      handleMenuClick,
      toggleSidebarCollapse,
      logout,
      handleNuevaFinca,
      handleMonitorearLotes
    };
  },
  mounted() {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
};
</script>

<style scoped>
.farmer-dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #F9FAFB;
}

.dashboard-section {
  padding: 2rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>

