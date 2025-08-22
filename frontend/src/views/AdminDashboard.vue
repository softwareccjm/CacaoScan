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
        <header class="bg-white shadow-sm mb-4 md:mb-6">
          <div class="px-3 sm:px-4 lg:px-8 py-4 md:py-6">
            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
              <div>
                <h1 class="text-lg md:text-2xl font-bold text-gray-800">Panel de Administración</h1>
                <p class="text-xs md:text-sm text-gray-600">Vista general del sistema</p>
              </div>
            </div>
          </div>
        </header>
        
        <!-- Contenido principal -->
        <main class="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
          <!-- Dashboard Title & Controls -->
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 md:mb-6">
            <div>
              <h2 class="text-lg md:text-2xl font-bold text-gray-800">Vista General</h2>
              <p class="text-xs md:text-sm text-gray-600 mt-1">Resumen de actividad y métricas clave</p>
            </div>
            <div class="mt-3 md:mt-0 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
              <div class="relative">
                <select class="w-full sm:w-auto bg-white border border-gray-300 rounded-md py-2 pl-3 pr-10 text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500">
                  <option>Último mes</option>
                  <option>Últimos 3 meses</option>
                  <option>Último año</option>
                  <option>Todo el tiempo</option>
                </select>
              </div>
              <button class="w-full sm:w-auto bg-green-100 text-green-800 hover:bg-green-200 px-4 py-2 rounded-md text-xs md:text-sm font-medium flex items-center justify-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                <span class="hidden sm:inline">Exportar</span>
                <span class="sm:hidden">Exportar</span>
              </button>
            </div>
          </div>

          <!-- Summary Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
              <div class="p-4 md:p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-green-50 rounded-lg p-2 md:p-3">
                    <svg class="w-6 h-6 md:w-8 md:h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                  </div>
                  <div class="ml-3 md:ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-xs md:text-sm font-medium text-gray-500 truncate">Agricultores registrados</dt>
                      <dd>
                        <div class="text-lg md:text-2xl font-semibold text-gray-900">221,324</div>
                        <div class="text-xs md:text-sm text-green-600 flex items-center mt-1">
                          <svg class="w-3 h-3 md:w-4 md:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                          </svg>
                          <span>12% desde el mes pasado</span>
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
              <div class="p-4 md:p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-emerald-50 rounded-lg p-2 md:p-3">
                    <svg class="w-6 h-6 md:w-8 md:h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  </div>
                  <div class="ml-3 md:ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-xs md:text-sm font-medium text-gray-500 truncate">Lotes analizados</dt>
                      <dd>
                        <div class="text-lg md:text-2xl font-semibold text-gray-900">2,324</div>
                        <div class="text-xs md:text-sm text-emerald-600 flex items-center mt-1">
                          <svg class="w-3 h-3 md:w-4 md:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                          </svg>
                          <span>8% desde el mes pasado</span>
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
              <div class="p-4 md:p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-blue-50 rounded-lg p-2 md:p-3">
                    <svg class="w-6 h-6 md:w-8 md:h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2zm0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                  <div class="ml-3 md:ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-xs md:text-sm font-medium text-gray-500 truncate">Total de análisis</dt>
                      <dd>
                        <div class="text-lg md:text-2xl font-semibold text-gray-900">16,703</div>
                        <div class="text-xs md:text-sm text-blue-600 flex items-center mt-1">
                          <svg class="w-3 h-3 md:w-4 md:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                          </svg>
                          <span>15% desde el mes pasado</span>
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Charts and Table -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <!-- Gráfico de líneas -->
            <div class="col-span-1 lg:col-span-2 bg-white p-4 md:p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-300">
              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 md:mb-6 space-y-3 sm:space-y-0">
                <div>
                  <h2 class="text-base md:text-lg font-semibold text-gray-800">
                    Evolución de análisis por tipo de defecto
                  </h2>
                  <p class="text-xs md:text-sm text-gray-500 mt-1">Tendencias de los últimos 5 meses</p>
                </div>
                <div class="flex space-x-2">
                  <button class="p-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
                    <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path>
                    </svg>
                  </button>
                  <button class="p-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="relative">
                <BarChart 
                  :chart-data="lineChartData"
                  :chart-options="lineChartOptions"
                  type="line"
                  class="h-72"
                />
              </div>
            </div>
            
            <!-- Gráfico de dona -->
            <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-300">
              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 md:mb-6 space-y-3 sm:space-y-0">
                <div>
                  <h2 class="text-base md:text-lg font-semibold text-gray-800">
                    Distribución por tipo de cacao
                  </h2>
                  <p class="text-xs md:text-sm text-gray-500 mt-1">Porcentaje del total analizado</p>
                </div>
                <div class="flex space-x-2">
                  <button class="p-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
                    <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="flex flex-col items-center justify-center">
                <PieChart 
                  :chart-data="doughnutChartData"
                  :chart-options="doughnutChartOptions"
                  class="h-48 md:h-64 w-full"
                />
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 w-full mt-4">
                  <div v-for="(label, index) in doughnutChartData.labels" :key="index" 
                    class="flex items-center text-xs md:text-sm">
                    <div class="w-3 h-3 rounded-full mr-2" 
                      :style="{ backgroundColor: doughnutChartData.datasets[0].backgroundColor[index] }"></div>
                    <span class="text-gray-700">{{ label }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Últimos análisis realizados -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 mb-6 md:mb-8 overflow-hidden hover:shadow-md transition-shadow duration-300">
            <div class="p-4 md:p-6 border-b border-gray-100">
              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
                <div>
                  <h2 class="text-base md:text-lg font-semibold text-gray-800">Últimos análisis realizados</h2>
                  <p class="text-xs md:text-sm text-gray-500 mt-1">Análisis más recientes en el sistema</p>
                </div>
                <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                  <div class="relative">
                    <input type="text" placeholder="Buscar análisis..." class="w-full sm:w-64 pl-9 pr-4 py-2 border border-gray-300 rounded-md text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500" />
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <button class="w-full sm:w-auto bg-green-600 text-white hover:bg-green-700 px-4 py-2 rounded-md text-xs md:text-sm font-medium flex items-center justify-center transition-colors duration-150">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    <span class="hidden sm:inline">Nuevo análisis</span>
                    <span class="sm:hidden">+ Nuevo</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agricultor</th>
                    <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lote</th>
                    <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                    <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resultado</th>
                    <th scope="col" class="px-3 md:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(item, idx) in paginatedAnalyses" :key="idx" class="hover:bg-gray-50 transition-colors duration-150">
                    <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="h-6 w-6 md:h-8 md:w-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-xs md:text-sm">{{ item.agricultor.charAt(0) }}</div>
                        <div class="ml-2 md:ml-3">
                          <div class="text-xs md:text-sm font-medium text-gray-900">{{ item.agricultor }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                      <div class="text-xs md:text-sm text-gray-900">Lote #{{ item.lote }}</div>
                    </td>
                    <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                      <div class="text-xs md:text-sm text-gray-900">{{ new Date().toLocaleDateString('es-ES') }}</div>
                    </td>
                    <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                      <span :class="{
                        'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full': true,
                        'bg-green-100 text-green-800': item.resultado === 'Aceptado',
                        'bg-yellow-100 text-yellow-800': item.resultado === 'Condicional',
                        'bg-red-100 text-red-800': item.resultado === 'Rechazado'
                      }">
                        {{ item.resultado }}
                      </span>
                    </td>
                    <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-sm font-medium">
                      <a href="#" class="text-green-600 hover:text-green-900 mr-3">Ver</a>
                      <a href="#" class="text-blue-600 hover:text-blue-900">Editar</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Paginación mejorada -->
            <div class="bg-gray-50 px-3 md:px-6 py-3 md:py-4 border-t border-gray-100">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                <div class="flex justify-center sm:justify-start">
                  <p class="text-xs md:text-sm text-gray-700">
                    Mostrando <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span> a <span class="font-medium">{{ Math.min(currentPage * pageSize, analyses.length) }}</span> de <span class="font-medium">{{ analyses.length }}</span> resultados
                  </p>
                </div>
                <div class="flex justify-center sm:justify-end">
                  <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                      <span class="sr-only">Anterior</span>
                      <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="[
                      'relative inline-flex items-center px-3 md:px-4 py-2 border text-xs md:text-sm font-medium',
                      currentPage === page ? 'z-10 bg-green-50 border-green-500 text-green-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    ]">
                      {{ page }}
                    </button>
                    <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                      <span class="sr-only">Siguiente</span>
                      <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import AdminSidebar from '@/components/common/AdminSidebar.vue';
import BarChart from '@/components/charts/BarChart.vue';
import PieChart from '@/components/charts/PieChart.vue';

export default {
  name: 'AdminDashboard',
  components: { 
    AdminSidebar,
    BarChart, 
    PieChart 
  },
  setup() {
    // Estado del sidebar
    const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Datos de usuario
    const userInitials = ref('AD');
    const userName = ref('Admin');
    const userRole = ref('Administrador');
    
    // Datos para el gráfico de líneas (evolución por tipo de defecto)
    const lineChartData = ref({
      labels: ['Abr', 'May', 'Jun', 'Jul', 'Ago'],
      datasets: [
        {
          label: 'Hongos',
          data: [24, 28, 42, 35, 31],
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Pizarrozo',
          data: [15, 12, 18, 22, 19],
          borderColor: '#8B5CF6',
          backgroundColor: 'rgba(139, 92, 246, 0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Insectos',
          data: [8, 10, 15, 12, 9],
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245,158,11,0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Planos',
          data: [5, 8, 6, 9, 7],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59,130,246,0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Mohoso',
          data: [3, 5, 8, 6, 10],
          borderColor: '#EC4899',
          backgroundColor: 'rgba(236, 72, 153, 0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'Violeta',
          data: [10, 7, 5, 8, 6],
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239,68,68,0.2)',
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    });
    const lineChartOptions = ref({
      responsive: true,
      plugins: {
        legend: { position: 'top' },
      },
    });

    // Datos de prueba para el gráfico de dona (tipo de cacao)
    const doughnutChartData = ref({
      labels: ['Fino aroma', 'Común', 'Híbrido'],
      datasets: [
        {
          data: [40, 30, 30],
          backgroundColor: ['#F59E0B', '#2563EB', '#10B981'],
          borderWidth: 2,
        },
      ],
    });
    const doughnutChartOptions = ref({
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom' },
      },
    });

    // Datos de prueba para la tabla de últimos análisis
    const analyses = ref([
      { agricultor: 'Camilo Hernandez', lote: 101, resultado: 'Aceptado' },
      { agricultor: 'Jeferson Alvarez', lote: 102, resultado: 'Condicional' },
      { agricultor: 'Cristian Camacho', lote: 103, resultado: 'Rechazado' },
      { agricultor: 'Juan Pablo Pérez', lote: 104, resultado: 'Aceptado' },
      { agricultor: 'Carlos Pérez', lote: 105, resultado: 'Aceptado' },
      { agricultor: 'María Gómez', lote: 106, resultado: 'Condicional' },
      { agricultor: 'Juan Torres', lote: 107, resultado: 'Rechazado' },
      { agricultor: 'Ana Ruiz', lote: 108, resultado: 'Aceptado' },
    ]);
    const currentPage = ref(1);
    const pageSize = 4;
    const totalPages = computed(() => Math.ceil(analyses.value.length / pageSize));
    const paginatedAnalyses = computed(() => {
      const start = (currentPage.value - 1) * pageSize;
      return analyses.value.slice(start, start + pageSize);
    });

    // Métodos
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
    };

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    // Lifecycle
    onMounted(() => {
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });

    return {
      // Estado del sidebar
      sidebarCollapsed,
      userInitials,
      userName,
      userRole,
      
      // Datos de gráficos
      lineChartData,
      lineChartOptions,
      doughnutChartData,
      doughnutChartOptions,
      
      // Datos de tabla
      analyses,
      currentPage,
      totalPages,
      paginatedAnalyses,
      
      // Métodos
      toggleSidebar
    };
  },
};
</script>

<style scoped>
/* Estilos para cuando el sidebar está colapsado */
.main-expanded {
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

/* Transición suave para el contenido principal */
.flex-1.flex.flex-col {
  transition: margin-left 0.3s ease;
}

/* Responsive */
@media (max-width: 768px) {
  .main-expanded {
    margin-left: 0;
  }
}

@media (max-width: 640px) {
  .main-expanded {
    margin-left: 0;
  }
}
</style>
