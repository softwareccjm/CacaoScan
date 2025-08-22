<template>
  <div class="bg-gray-50 min-h-screen">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <AdminSidebar 
        :user-initials="userInitials"
        :user-name="userName"
        :user-role="userRole"
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
      
      <!-- Contenido principal -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden" :class="{ 'main-expanded': sidebarCollapsed }">
        <!-- Header de la página -->
        <PageHeader 
          title="Agricultores"
          subtitle="Gestión de agricultores y fincas"
        />
        
        <!-- Contenido principal -->
        <main class="flex-1 p-4 md:p-6 lg:p-8 pb-0 overflow-y-auto">
          <!-- Filtros y controles -->
          <div class="mb-4 md:mb-6">
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <div class="flex flex-col sm:flex-row gap-4 flex-1">
                <FilterSelect 
                  id="region"
                  label="Región"
                  v-model="filters.region"
                  :options="regionOptions"
                />
                
                <FilterSelect 
                  id="status"
                  label="Estado"
                  v-model="filters.status"
                  :options="statusOptions"
                />
              </div>
              
              <div class="flex gap-2">
                <ActionButton 
                  label="Aplicar Filtros"
                  short-label="Filtrar"
                  variant="secondary"
                  icon="FunnelIcon"
                  @click="applyFilters"
                />
                <ActionButton 
                  label="Nuevo Agricultor"
                  short-label="+ Nuevo"
                  variant="primary"
                  @click="handleNewFarmer"
                />
              </div>
            </div>
          </div>

          <!-- Barra de búsqueda -->
          <div class="mb-4 md:mb-6">
            <SearchBar 
              v-model="searchQuery"
              placeholder="Buscar agricultor..."
            />
          </div>

          <!-- Tabla de agricultores -->
          <div class="flex-1 min-h-0">
            <DataTable 
              :columns="tableColumns"
              :data="filteredFarmers"
            >
              <!-- Celda personalizada para Agricultor -->
              <template #cell-farmer="{ row }">
                <div class="flex items-center">
                  <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-medium text-sm md:text-base">
                    {{ row.initials }}
                  </div>
                  <div class="ml-2 md:ml-4">
                    <div class="text-xs md:text-sm font-medium text-gray-900">{{ row.name }}</div>
                    <div class="text-xs md:text-sm text-gray-500">{{ row.email }}</div>
                  </div>
                </div>
              </template>

              <!-- Celda personalizada para Finca -->
              <template #cell-farm="{ row }">
                <div class="text-xs md:text-sm text-gray-900">{{ row.farm }}</div>
                <div class="text-xs md:text-sm text-gray-500">{{ row.hectares }}</div>
              </template>

              <!-- Celda personalizada para Estado -->
              <template #cell-status="{ row }">
                <span :class="getStatusClasses(row.status)" class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ row.status }}
                </span>
              </template>

              <!-- Celda personalizada para Acciones -->
              <template #cell-actions="{ row }">
                <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
                  <a href="#" class="text-green-600 hover:text-green-900 transition-colors duration-200">Ver</a>
                  <a href="#" class="text-blue-600 hover:text-blue-900 transition-colors duration-200">Editar</a>
                  <a href="#" class="text-red-600 hover:text-red-900 transition-colors duration-200">Eliminar</a>
                </div>
              </template>

              <!-- Paginación -->
              <template #pagination>
                <Pagination 
                  :current-page="currentPage"
                  :total-pages="totalPages"
                  :total-items="totalItems"
                  :items-per-page="itemsPerPage"
                  @page-change="handlePageChange"
                />
              </template>
            </DataTable>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import AdminSidebar from '@/components/common/AdminSidebar.vue';
import PageHeader from '@/components/agricultores/PageHeader.vue';
import SearchBar from '@/components/agricultores/SearchBar.vue';
import ActionButton from '@/components/agricultores/ActionButton.vue';
import FilterSelect from '@/components/agricultores/FilterSelect.vue';
import DataTable from '@/components/agricultores/DataTable.vue';
import Pagination from '@/components/agricultores/Pagination.vue';

export default {
  name: 'AgricultoresView',
  components: {
    AdminSidebar,
    PageHeader,
    SearchBar,
    ActionButton,
    FilterSelect,
    DataTable,
    Pagination
  },
  setup() {
    // Estado reactivo
    const searchQuery = ref('');
    const currentPage = ref(1);
    const loading = ref(false);
    const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Datos de usuario
    const userInitials = ref('AD');
    const userName = ref('Admin');
    const userRole = ref('Administrador');
    
    const filters = ref({
      region: '',
      status: ''
    });

    // Datos de ejemplo
    const farmers = ref([
      {
        id: 1,
        initials: 'CH',
        name: 'Camilo Hernandez',
        email: 'camilo@example.com',
        farm: 'Finca El Paraíso',
        hectares: '12 hectáreas',
        region: 'Santander',
        status: 'Activo'
      },
      {
        id: 2,
        initials: 'JA',
        name: 'Jeferson Alvarez',
        email: 'jeferson@example.com',
        farm: 'Finca Los Laureles',
        hectares: '8 hectáreas',
        region: 'Antioquia',
        status: 'Activo'
      },
      {
        id: 3,
        initials: 'CC',
        name: 'Cristian Camacho',
        email: 'cristian@example.com',
        farm: 'Finca El Mirador',
        hectares: '15 hectáreas',
        region: 'Huila',
        status: 'En revisión'
      },
      {
        id: 4,
        initials: 'JP',
        name: 'Juan Pablo Pérez',
        email: 'juanpablo@example.com',
        farm: 'Finca La Esperanza',
        hectares: '10 hectáreas',
        region: 'Nariño',
        status: 'Inactivo'
      }
    ]);

    // Configuración de la tabla
    const tableColumns = [
      { key: 'farmer', label: 'Agricultor' },
      { key: 'farm', label: 'Finca' },
      { key: 'region', label: 'Región' },
      { key: 'status', label: 'Estado' },
      { key: 'actions', label: 'Acciones', align: 'right' }
    ];

    // Opciones de filtros
    const regionOptions = [
      { value: '', label: 'Todas las regiones' },
      { value: 'Antioquia', label: 'Antioquia' },
      { value: 'Santander', label: 'Santander' },
      { value: 'Nariño', label: 'Nariño' },
      { value: 'Huila', label: 'Huila' }
    ];

    const statusOptions = [
      { value: '', label: 'Todos los estados' },
      { value: 'Activo', label: 'Activo' },
      { value: 'En Revisión', label: 'En Revisión' },
      { value: 'Inactivo', label: 'Inactivo' }
    ];

    // Computed properties
    const filteredFarmers = computed(() => {
      let filtered = farmers.value;

      // Filtro por búsqueda
      if (searchQuery.value) {
        filtered = filtered.filter(farmer => 
          farmer.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          farmer.email.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      }

      // Filtro por región
      if (filters.value.region) {
        filtered = filtered.filter(farmer => farmer.region === filters.value.region);
      }

      // Filtro por estado
      if (filters.value.status) {
        filtered = filtered.filter(farmer => farmer.status === filters.value.status);
      }

      return filtered;
    });

    const totalItems = computed(() => filteredFarmers.value.length);
    const itemsPerPage = 4;
    const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage));

    // Métodos
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
    };

    const handleNewFarmer = () => {
      console.log('Nuevo agricultor');
      // Implementar lógica para crear nuevo agricultor
    };

    const applyFilters = () => {
      currentPage.value = 1; // Resetear a la primera página
      console.log('Aplicando filtros:', filters.value);
    };

    const handlePageChange = (page) => {
      currentPage.value = page;
    };

    const getStatusClasses = (status) => {
      switch (status) {
        case 'Activo':
          return 'bg-green-100 text-green-800';
        case 'En revisión':
          return 'bg-yellow-100 text-yellow-800';
        case 'Inactivo':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    // Lifecycle
    onMounted(() => {
      console.log('Vista Agricultores montada');
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    return {
      // Estado
      searchQuery,
      currentPage,
      loading,
      sidebarCollapsed,
      userInitials,
      userName,
      userRole,
      
      // Filtros
      filters,
      
      // Datos
      farmers,
      tableColumns,
      regionOptions,
      statusOptions,
      filteredFarmers,
      totalItems,
      itemsPerPage,
      totalPages,
      
      // Métodos
      toggleSidebar,
      handleNewFarmer,
      applyFilters,
      handlePageChange,
      getStatusClasses
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de agricultores */
.min-h-screen {
  min-height: 100vh;
}

.h-screen {
  height: 100vh;
}

/* Asegurar que el contenido principal no se desborde */
.min-w-0 {
  min-width: 0;
}

/* Eliminar espacio blanco excesivo */
.flex-1 {
  flex: 1 1 0%;
}

/* Asegurar que el contenido principal ocupe toda la altura disponible */
main {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* Controlar el overflow */
.overflow-hidden {
  overflow: hidden;
}

.overflow-y-auto {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Asegurar que el contenido se ajuste correctamente */
.flex.flex-col {
  display: flex;
  flex-direction: column;
}

/* Asegurar que el contenido se ajuste al viewport */
.min-h-0 {
  min-height: 0;
}

/* Layout específico para la vista de agricultores */
.bg-gray-50 {
  background-color: #f9fafb;
}

/* Asegurar que el sidebar y contenido principal se alineen correctamente */
.flex.h-screen {
  height: 100vh;
  max-height: 100vh;
}

/* Estilos para cuando el sidebar está colapsado */
.main-expanded {
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

/* Transición suave para el contenido principal */
.flex-1.flex.flex-col {
  transition: margin-left 0.3s ease;
}

/* Mejoras de responsividad */
@media (max-width: 768px) {
  .p-4 {
    padding: 1rem;
  }
  
  .md\:p-6 {
    padding: 1.5rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
  
  /* Ajustar el grid en tablets */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Reducir padding inferior en móviles */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en móviles */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el overflow en móviles */
  .overflow-y-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  
  .overflow-y-auto::-webkit-scrollbar {
    display: none;
  }
  
  /* Asegurar que el sidebar esté colapsado en móviles */
  .sidebar-collapsed {
    width: 70px;
  }
  
  /* Ajustar el contenido principal en móviles */
  .main-expanded {
    margin-left: 0;
  }
}

@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 0.75rem;
  }
  
  .mb-8 {
    margin-bottom: 1rem;
  }
  
  .gap-4 {
    gap: 0.75rem;
  }
  
  /* Forzar una columna en móviles */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Eliminar padding inferior en pantallas pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
}

@media (max-width: 480px) {
  .p-4 {
    padding: 0.5rem;
  }
  
  .mb-6 {
    margin-bottom: 0.5rem;
  }
  
  .mb-8 {
    margin-bottom: 0.75rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
  
  /* Una sola columna en pantallas muy pequeñas */
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado de botones en móviles */
  .flex.gap-2 {
    gap: 0.5rem;
  }
  
  /* Eliminar padding inferior en pantallas muy pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en pantallas muy pequeñas */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el contenido para pantallas muy pequeñas */
  main {
    padding: 0.5rem;
  }
  
  /* Reducir espaciado en pantallas muy pequeñas */
  .mb-4 {
    margin-bottom: 0.5rem;
  }
  
  /* Asegurar que el sidebar esté completamente colapsado en pantallas muy pequeñas */
  .sidebar-collapsed {
    width: 60px;
  }
  
  /* Ajustar el contenido principal en pantallas muy pequeñas */
  .main-expanded {
    margin-left: 0;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  .min-h-screen {
    min-height: 100vh;
  }
  
  /* Asegurar que los botones tengan el tamaño mínimo táctil */
  button {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:p-8 {
    padding: 2rem;
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
}

/* Animaciones de entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

main {
  animation: fadeIn 0.5s ease-out;
}

/* Mejoras para accesibilidad */
*:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para tablas responsivas */
@media (max-width: 640px) {
  .grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Ajustar el layout de filtros en móviles */
  .flex-col.sm\:flex-row {
    flex-direction: column;
  }
  
  .items-start.sm\:items-center {
    align-items: flex-start;
  }
  
  .justify-between {
    justify-content: flex-start;
  }
  
  .flex.gap-2 {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado en pantallas muy pequeñas */
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
  
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
}

/* Mejoras para el scroll en móviles */
@media (max-width: 640px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
}

/* Optimizaciones para pantallas de alta densidad */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .bg-white {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
}

/* Mejoras para dispositivos con pantallas pequeñas y alta densidad */
@media (max-width: 640px) and (-webkit-min-device-pixel-ratio: 2) {
  .text-sm {
    font-size: 0.8125rem;
  }
  
  .text-xs {
    font-size: 0.6875rem;
  }
}

/* Mejoras de responsividad adicionales para la tabla */
@media (max-width: 640px) {
  .chart-container {
    min-height: 250px;
  }
}

@media (max-width: 480px) {
  .chart-container {
    min-height: 300px;
  }
}

/* Transiciones suaves para mejor UX */
* {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  button, a {
    min-height: 44px;
    min-width: 44px;
  }
  
  .table-responsive {
    -webkit-overflow-scrolling: touch;
  }
}

/* Optimizaciones para pantallas pequeñas */
@media (max-width: 768px) {
  .sidebar-collapsed {
    width: 4rem;
  }
  
  .main-content-expanded {
    margin-left: 4rem;
  }
}
</style>