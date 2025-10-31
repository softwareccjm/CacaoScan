<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Component -->
    <AdminSidebar :brand-name="brandName" :user-name="userName" :user-role="userRole" :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick" @logout="handleLogout" @toggle-collapse="toggleSidebarCollapse" />

    <!-- Main Content -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'">
      <!-- Dashboard Header -->
      <div class="mb-8">
        <div
          class="bg-gradient-to-r from-white to-green-50 rounded-2xl border-2 border-gray-200 hover:shadow-xl hover:border-green-300 transition-all duration-300">
          <div class="px-8 py-6">
            <div class="flex-1">
            <div class="flex items-center gap-4">
              <div class="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-gray-900 mb-1">Dashboard de Administración</h1>
                <p class="text-gray-600 text-base">Panel de control completo del sistema CacaoScan</p>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-auto">
              <div v-if="isRefreshing" class="flex items-center gap-2 text-sm text-green-600">
                <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>Actualizando...</span>
              </div>
              <div v-else-if="lastUpdateTime" class="text-xs text-gray-500">
                Última actualización: {{ formatLastUpdate(lastUpdateTime) }}
              </div>
            </div>
            </div>
          </div>
          </div>
      </div>
      <!-- KPI Cards Component -->
      <div class="mb-8">
        <KPICards :cards="kpiCards" />
      </div>

      <!-- Charts Component -->
      <div class="mb-8">
        <DashboardCharts :activity-chart-title="activityChartTitle" :quality-chart-title="qualityChartTitle"
          :activity-chart-data="activityChartData" :quality-chart-data="qualityChartData"
          :activity-chart-options="activityChartOptions" :quality-chart-options="qualityChartOptions" :loading="loading"
          :initial-activity-chart-type="activityChartType" @activity-chart-type-change="handleActivityChartTypeChange"
          @activity-refresh="handleActivityRefresh" @quality-refresh="handleQualityRefresh"
          @activity-click="handleActivityClick" @quality-click="handleQualityClick" />
      </div>

      <!-- Tables Component -->
      <div class="mb-8">
        <DashboardTables :users-table-title="usersTableTitle" :users-table-link="usersTableLink"
          :users-table-link-text="usersTableLinkText" :activity-table-title="activityTableTitle"
          :activity-table-link="activityTableLink" :activity-table-link-text="activityTableLinkText"
          :recent-users="recentUsers" :recent-activities="recentActivities" @view-user="handleViewUser"
          @edit-user="handleEditUser" />
      </div>

      <!-- Alerts and Reports Component -->
      <div class="mb-8">
        <DashboardAlerts :alerts-title="alertsTitle" :no-alerts-message="noAlertsMessage" :reports-title="reportsTitle"
          :reports-link="reportsLink" :reports-link-text="reportsLinkText" :total-reports-label="totalReportsLabel"
          :completed-reports-label="completedReportsLabel" :generating-reports-label="generatingReportsLabel"
          :failed-reports-label="failedReportsLabel" :alerts="alerts" :report-stats="reportStats"
          @dismiss-alert="handleDismissAlert" />
      </div>

    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'
import { useAdminStore } from '@/stores/admin'
import AdminSidebar from '@/components/layout/Common/Sidebar.vue'
import KPICards from '@/components/admin/AdminDashboardComponents/KPICards.vue'
import DashboardCharts from '@/components/admin/AdminDashboardComponents/DashboardCharts.vue'
import DashboardTables from '@/components/admin/AdminDashboardComponents/DashboardTables.vue'
import DashboardAlerts from '@/components/admin/AdminDashboardComponents/DashboardAlerts.vue'
import LoadingSpinner from '@/components/admin/AdminGeneralComponents/LoadingSpinner.vue'

// Intentar importar WebSocket composable
import { useWebSocket } from '@/composables/useWebSocket'

export default {
  name: 'AdminDashboard',
  components: {
    AdminSidebar,
    KPICards,
    DashboardCharts,
    DashboardTables,
    DashboardAlerts,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const adminStore = useAdminStore()
    const configStore = useConfigStore()

    // Intentar usar WebSocket si está disponible
    let websocket = null
    try {
      websocket = useWebSocket()
    } catch (e) {
      console.warn('⚠️ WebSocket no disponible, usando solo polling:', e.message)
    }

    // Reactive data
    const loading = ref(false)
    const isRefreshing = ref(false)
    const lastUpdateTime = ref(null)
    const stats = ref({})
    const recentUsers = ref([])
    const recentActivities = ref([])
    const alerts = ref([])
    const reportStats = ref({})
    const selectedPeriod = ref('30')
    const activityChartType = ref('line')
    
    // Debug: Watch stats para ver cuando cambia
    watch(() => stats.value, (newStats) => {
      console.log('🔄 Stats cambiaron:', newStats)
      if (newStats?.users) {
        console.log('👥 Usuarios en stats:', newStats.users)
      }
      if (newStats?.fincas) {
        console.log('🏡 Fincas en stats:', newStats.fincas)
      }
      if (newStats?.images) {
        console.log('🖼️ Imágenes en stats:', newStats.images)
      }
      if (newStats?.predictions) {
        console.log('⭐ Predictions en stats:', newStats.predictions)
      }
    }, { deep: true })

    // Los gráficos se manejan completamente en DashboardCharts

    // Datos de gráficos
    const activityData = ref({ labels: [], datasets: [] })
    const qualityData = ref({ labels: [], datasets: [] })

    // Sidebar properties
    const brandName = computed(() => configStore.brandName)
    const userName = computed(() => {
      const user = authStore.user
      return user ? `${user.first_name} ${user.last_name}`.trim() || user.username : 'Admin User'
    })
    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario'
      // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin' // Default to admin for AdminDashboard
    })

    // Navbar properties
    const navbarTitle = ref('Dashboard de Administración')
    const navbarSubtitle = ref('Panel de control completo del sistema CacaoScan')
    const searchPlaceholder = ref('Buscar usuarios, análisis, reportes...')
    const refreshButtonText = ref('Actualizar')
    const searchQuery = ref('')

    // Sidebar collapse state
    const isSidebarCollapsed = ref(false)

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
    }

    // Charts properties
    const activityChartTitle = ref('Actividad de Usuarios')
    const qualityChartTitle = ref('Distribución de Calidad')

    // Tables properties
    const usersTableTitle = ref('Usuarios Recientes')
    const usersTableLink = ref('/admin/agricultores')
    const usersTableLinkText = ref('Ver Todos')
    const activityTableTitle = ref('Actividad Reciente')
    const activityTableLink = ref('/admin/audit')
    const activityTableLinkText = ref('Ver Auditoría')

    // Alerts properties
    const alertsTitle = ref('Alertas del Sistema')
    const noAlertsMessage = ref('No hay alertas activas')
    const reportsTitle = ref('Reportes Generados')
    const reportsLink = ref('/admin/reports')
    const reportsLinkText = ref('Gestionar Reportes')
    const totalReportsLabel = ref('Total Reportes')
    const completedReportsLabel = ref('Completados')
    const generatingReportsLabel = ref('Generando')
    const failedReportsLabel = ref('Fallidos')

    // KPI Cards data - mapear desde estructura anidada del backend
    const kpiCards = computed(() => {
      // Asegurarnos de que stats.value existe
      if (!stats.value || Object.keys(stats.value).length === 0) {
        console.warn('⚠️ Stats vacías, retornando valores por defecto')
        return [
          { id: 'users', value: 0, label: 'Usuarios Totales', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'primary', trend: { data: [], direction: 'stable' } },
          { id: 'fincas', value: 0, label: 'Fincas Registradas', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'success', trend: { data: [], direction: 'stable' } },
          { id: 'analyses', value: 0, label: 'Análisis Realizados', iconPath: '', change: 0, changePeriod: 'esta semana', variant: 'info', trend: { data: [], direction: 'stable' } },
          { id: 'quality', value: 0, label: 'Calidad Promedio', iconPath: '', suffix: '%', change: 0, changePeriod: 'vs mes anterior', variant: 'warning', trend: { data: [], direction: 'stable' } }
        ]
      }
      
      // Debug: Log para ver qué datos tenemos
      console.log('🔍 Calculando KPI cards con stats:', stats.value)
      
      // Obtener datos de la estructura anidada del backend - asegurar valores numéricos
      const usersTotal = Number(stats.value?.users?.total) || Number(stats.value?.total_users) || 0
      const usersThisWeek = Number(stats.value?.users?.this_week) || 0
      const fincasTotal = Number(stats.value?.fincas?.total) || 0
      const fincasThisWeek = Number(stats.value?.fincas?.this_week) || 0
      const imagesTotal = Number(stats.value?.images?.total) || Number(stats.value?.total_images) || 0
      const imagesThisWeek = Number(stats.value?.images?.this_week) || 0
      
      // Para calidad promedio, convertir de decimal (0-1) a porcentaje (0-100)
      let avgQuality = 0
      const confidence = stats.value?.predictions?.average_confidence
      if (confidence !== undefined && confidence !== null) {
        avgQuality = Math.round(Number(confidence) * 100)
      } else if (stats.value?.avg_quality !== undefined && stats.value?.avg_quality !== null) {
        avgQuality = Number(stats.value.avg_quality)
      }
      
      const qualityChange = 0 // Por ahora sin cambio calculado
      
      console.log('📈 Valores calculados para KPI cards:', {
        usersTotal,
        fincasTotal,
        imagesTotal,
        avgQuality,
        'confidence raw': confidence,
        'stats.value completo': stats.value
      })

      return [
        {
          id: 'users',
          value: usersTotal,
          label: 'Usuarios Totales',
          iconPath: 'M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z',
          change: usersThisWeek,
          changePeriod: 'esta semana',
          variant: 'primary',
          trend: {
            data: [],
            direction: usersThisWeek > 0 ? 'up' : 'stable'
          }
        },
        {
          id: 'fincas',
          value: fincasTotal,
          label: 'Fincas Registradas',
          iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z',
          fillRule: 'evenodd',
          clipRule: 'evenodd',
          change: fincasThisWeek,
          changePeriod: 'esta semana',
          variant: 'success',
          trend: {
            data: [],
            direction: fincasThisWeek > 0 ? 'up' : 'stable'
          }
        },
        {
          id: 'analyses',
          value: imagesTotal,
          label: 'Análisis Realizados',
          iconPath: 'M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
          fillRule: 'evenodd',
          clipRule: 'evenodd',
          change: imagesThisWeek,
          changePeriod: 'esta semana',
          variant: 'info',
          trend: {
            data: [],
            direction: imagesThisWeek > 0 ? 'up' : 'stable'
          }
        },
        {
          id: 'quality',
          value: avgQuality,
          label: 'Calidad Promedio',
          iconPath: 'M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z',
          suffix: '%',
          change: Math.round(qualityChange),
          changePeriod: 'vs mes anterior',
          variant: 'warning',
          trend: {
            data: [],
            direction: qualityChange > 0 ? 'up' : qualityChange < 0 ? 'down' : 'stable'
          }
        }
      ]
    })

    // Configuración de gráficos
    const activityChartData = computed(() => activityData.value)
    const qualityChartData = computed(() => qualityData.value)

    const activityChartOptions = computed(() => ({
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => value.toLocaleString()
          }
        }
      }
    }))

    const qualityChartOptions = computed(() => ({
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }))

    // Methods
    const loadDashboardData = async () => {
      loading.value = true
      try {
        await Promise.all([
          loadStats(),
          loadRecentUsers(),
          loadRecentActivities(),
          loadAlerts(),
          loadReportStats(),
          loadQualityData(),
          updateActivityChart()
        ])
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudieron cargar los datos del dashboard'
        })
      } finally {
        loading.value = false
      }
    }

    const loadStats = async () => {
      try {
        isRefreshing.value = true
        const response = await adminStore.getGeneralStats()
        // response.data ya contiene los datos directamente del backend
        const data = response.data || {}
        console.log('📊 Stats cargadas (raw):', data)
        
        // Asegurar que la estructura esté completa antes de asignar
        const statsData = {
          users: data.users || { total: 0, this_week: 0, this_month: 0 },
          fincas: data.fincas || { total: 0, this_week: 0, this_month: 0 },
          images: data.images || { total: 0, this_week: 0, this_month: 0 },
          predictions: data.predictions || { average_confidence: 0 },
          activity_by_day: data.activity_by_day || { labels: [], data: [] },
          quality_distribution: data.quality_distribution || { excelente: 0, buena: 0, regular: 0, baja: 0 },
          ...data
        }
        
        // Asignar usando Object.assign para mantener reactividad
        Object.assign(stats.value, statsData)
        lastUpdateTime.value = new Date()
        console.log('✅ Stats asignadas a stats.value')
        
        // Actualizar gráficos con datos reales
        updateActivityChartFromStats()
        updateQualityChartFromStats()
      } catch (error) {
        console.error('Error loading stats:', error)
        stats.value = {
          users: { total: 0 },
          fincas: { total: 0 },
          images: { total: 0 },
          predictions: { average_confidence: 0 }
        }
      } finally {
        isRefreshing.value = false
      }
    }

    const processUserData = (user) => {
      // Usar el rol que viene del backend (UserSerializer ya lo calcula)
      // Valores posibles: 'admin', 'analyst', 'farmer'
      return {
        id: user.id,
        username: user.username || user.email?.split('@')[0] || 'Usuario',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        role: user.role || 'farmer', // Usar el role que viene del backend
        is_active: user.is_active !== false,
        date_joined: user.date_joined || user.created_at
      }
    }

    const loadRecentUsers = async () => {
      try {
        isRefreshing.value = true
        const response = await adminStore.getRecentUsers(5)
        const data = response.data
        
        // Procesar datos según el formato de respuesta
        let usersArray = []
        if (Array.isArray(data)) {
          usersArray = data
        } else if (data?.results && Array.isArray(data.results)) {
          usersArray = data.results
        } else if (data?.data && Array.isArray(data.data)) {
          usersArray = data.data
        }
        
        // Procesar cada usuario para asegurar formato consistente
        recentUsers.value = usersArray.map(processUserData)
        lastUpdateTime.value = new Date()
        console.log('👥 Recent users loaded:', recentUsers.value.length, 'items')
      } catch (error) {
        console.error('Error loading recent users:', error)
        recentUsers.value = []
      } finally {
        isRefreshing.value = false
      }
    }

    const processActivityData = (activity) => {
      // El backend ya devuelve los datos en el formato correcto:
      // - usuario: string (username)
      // - accion: string
      // - accion_display: string (ya traducido)
      // - modelo: string
      // - timestamp: string (ISO format)
      
      return {
        id: activity.id,
        usuario: activity.usuario || activity.user?.username || activity.username || 'Anónimo',
        accion: activity.accion || activity.action || 'unknown',
        accion_display: activity.accion_display || activity.action_display || 
          (activity.accion === 'create' ? 'Crear' :
           activity.accion === 'update' ? 'Actualizar' :
           activity.accion === 'delete' ? 'Eliminar' :
           activity.accion === 'view' ? 'Ver' :
           activity.accion === 'login' ? 'Login' :
           activity.accion === 'logout' ? 'Logout' : 
           activity.accion === 'read' ? 'Leer' :
           activity.accion || 'Desconocida'),
        modelo: activity.modelo || activity.model || activity.content_type || 'N/A',
        timestamp: activity.timestamp || activity.created_at || activity.date || new Date().toISOString(),
        descripcion: activity.descripcion || activity.description || '',
        ip_address: activity.ip_address || activity.ip || ''
      }
    }

    const loadRecentActivities = async () => {
      try {
        isRefreshing.value = true
        const response = await adminStore.getRecentActivities(20)
        const data = response.data || {}
        
        // Procesar datos según el formato de respuesta del backend
        let activitiesArray = []
        if (Array.isArray(data)) {
          activitiesArray = data
        } else if (data?.results && Array.isArray(data.results)) {
          activitiesArray = data.results
        } else if (data?.data && Array.isArray(data.data)) {
          activitiesArray = data.data
        }
        
        // Procesar cada actividad para asegurar formato consistente
        recentActivities.value = activitiesArray.map(processActivityData)
        lastUpdateTime.value = new Date()
        console.log('📊 [AdminDashboard] Recent activities loaded:', recentActivities.value.length, 'items')
      } catch (error) {
        console.error('❌ [AdminDashboard] Error loading recent activities:', error)
        recentActivities.value = []
      } finally {
        isRefreshing.value = false
      }
    }

    const processAlertData = (notification) => {
      // Convertir notificación del backend a formato de alerta del componente
      // El backend devuelve: id, tipo, tipo_display, titulo, mensaje, leida, fecha_creacion
      // El componente espera: id, title, message, type, created_at
      
      // Mapear tipos de notificación a tipos de alerta
      const typeMapping = {
        'success': 'success',
        'warning': 'warning',
        'error': 'error',
        'info': 'info',
        'critical': 'error'
      }
      
      return {
        id: notification.id,
        title: notification.titulo || notification.title || 'Alerta',
        message: notification.mensaje || notification.message || '',
        type: typeMapping[notification.tipo?.toLowerCase()] || notification.tipo || 'info',
        created_at: notification.fecha_creacion || notification.created_at || notification.fecha_creacion || new Date().toISOString(),
        leida: notification.leida || false
      }
    }

    const loadAlerts = async () => {
      try {
        isRefreshing.value = true
        const response = await adminStore.getSystemAlerts()
        const data = response.data || {}
        
        // Procesar datos según el formato de respuesta
        let notificationsArray = []
        if (Array.isArray(data)) {
          notificationsArray = data
        } else if (data?.results && Array.isArray(data.results)) {
          notificationsArray = data.results
        } else if (data?.data && Array.isArray(data.data)) {
          notificationsArray = data.data
        }
        
        // Procesar cada notificación para asegurar formato consistente
        alerts.value = notificationsArray.map(processAlertData)
        lastUpdateTime.value = new Date()
        console.log('🚨 [AdminDashboard] Alerts loaded:', alerts.value.length, 'items')
      } catch (error) {
        console.error('❌ [AdminDashboard] Error loading alerts:', error)
        alerts.value = []
      } finally {
        isRefreshing.value = false
      }
    }

    const loadReportStats = async () => {
      try {
        isRefreshing.value = true
        const response = await adminStore.getReportStats()
        const data = response.data || {}
        
        // Mapear datos del backend al formato esperado por el componente
        reportStats.value = {
          total_reportes: data.total_reportes || 0,
          reportes_completados: data.reportes_completados || 0,
          reportes_generando: data.reportes_generando || 0,
          reportes_fallidos: data.reportes_fallidos || 0,
          ...data
        }
        
        lastUpdateTime.value = new Date()
        console.log('📊 [AdminDashboard] Report stats processed')
      } catch (error) {
        console.error('❌ [AdminDashboard] Error loading report stats:', error)
        reportStats.value = {
          total_reportes: 0,
          reportes_completados: 0,
          reportes_generando: 0,
          reportes_fallidos: 0
        }
      } finally {
        isRefreshing.value = false
      }
    }

    const updateQualityChartFromStats = () => {
      // Usar datos de distribución de calidad de stats.value que vienen del backend
      const quality = stats.value?.quality_distribution || { excelente: 0, buena: 0, regular: 0, baja: 0 }
      
      qualityData.value = {
        labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
        datasets: [{
          data: [
            quality.excelente || 0,
            quality.buena || 0,
            quality.regular || 0,
            quality.baja || 0
          ],
          backgroundColor: [
            '#22c55e',  // Excelente - Verde
            '#3b82f6',  // Buena - Azul
            '#f59e0b',  // Regular - Amarillo/Naranja
            '#ef4444'   // Baja - Rojo
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      }
      console.log('📊 Quality chart data updated:', qualityData.value)
    }

    const loadQualityData = async () => {
      try {
        // Primero intentar usar datos de stats
        if (stats.value?.quality_distribution) {
          updateQualityChartFromStats()
          return
        }
        
        // Si no hay datos en stats, intentar cargar desde el endpoint
        const response = await adminStore.getQualityDistribution()
        const quality = response.data || { excelente: 0, buena: 0, regular: 0, baja: 0 }
        
        qualityData.value = {
          labels: ['Excelente', 'Buena', 'Regular', 'Baja'],
          datasets: [{
            data: [
              quality.excelente || 0,
              quality.buena || 0,
              quality.regular || 0,
              quality.baja || 0
            ],
            backgroundColor: [
              '#22c55e',
              '#3b82f6',
              '#f59e0b',
              '#ef4444'
            ],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        }
        console.log('📊 Quality chart data loaded from endpoint:', qualityData.value)
      } catch (error) {
        console.error('Error loading quality data:', error)
        // Usar datos vacíos si hay error
        updateQualityChartFromStats()
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const updateActivityChartFromStats = () => {
      // Usar datos de actividad de stats.value que vienen del backend
      const activity = stats.value?.activity_by_day || { labels: [], data: [] }
      
      activityData.value = {
        labels: activity.labels || [],
        datasets: [{
          label: 'Actividad del Sistema',
          data: activity.data || [],
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#22c55e',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2
        }]
      }
      console.log('📊 Activity chart data updated:', activityData.value)
    }

    const updateActivityChart = async () => {
      try {
        // Primero intentar usar datos de stats
        if (stats.value?.activity_by_day) {
          updateActivityChartFromStats()
          return
        }
        
        // Si no hay datos en stats, intentar cargar desde el endpoint
        const response = await adminStore.getActivityData(selectedPeriod.value)
        if (!response.data || !response.data.results) {
          updateActivityChartFromStats()
          return
        }
        
        updateActivityChartFromStats()
      } catch (error) {
        // Silenciosamente manejar errores sin mostrar notificaciones
        console.debug('Error updating activity chart:', error)
        updateActivityChartFromStats()
      }
    }

    const refreshActivityData = () => {
      updateActivityChart()
    }

    const refreshQualityData = () => {
      loadQualityData()
    }

    const updatePeriod = () => {
      loadDashboardData()
    }

    // Los gráficos se manejan completamente en DashboardCharts
    // No necesitamos crear instancias aquí

    // Utility methods
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('es-ES')
    }

    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('es-ES')
    }

    const formatLastUpdate = (date) => {
      if (!date) return 'Nunca'
      const now = new Date()
      const updateDate = new Date(date)
      const diffMs = now - updateDate
      const diffSecs = Math.floor(diffMs / 1000)
      const diffMins = Math.floor(diffSecs / 60)
      
      if (diffSecs < 5) return 'Ahora'
      if (diffSecs < 60) return `Hace ${diffSecs}s`
      if (diffMins < 60) return `Hace ${diffMins}m`
      return updateDate.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    }

    const getRoleBadgeClass = (role) => {
      const classes = {
        'Administrador': 'bg-red-100 text-red-800',
        'Agricultor': 'bg-green-100 text-green-800',
        'Técnico': 'bg-blue-100 text-blue-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    }

    const getActionBadgeClass = (action) => {
      const classes = {
        'create': 'bg-green-100 text-green-800',
        'update': 'bg-amber-100 text-amber-800',
        'delete': 'bg-red-100 text-red-800',
        'view': 'bg-blue-100 text-blue-800',
        'login': 'bg-indigo-100 text-indigo-800',
        'logout': 'bg-gray-100 text-gray-800'
      }
      return classes[action] || 'bg-gray-100 text-gray-800'
    }

    const getAlertBorderClass = (type) => {
      const classes = {
        'success': 'border-green-400 bg-green-50',
        'warning': 'border-amber-400 bg-amber-50',
        'error': 'border-red-400 bg-red-50',
        'info': 'border-blue-400 bg-blue-50'
      }
      return classes[type] || 'border-gray-400 bg-gray-50'
    }

    const getAlertIconClass = (type) => {
      const classes = {
        'success': 'text-green-500',
        'warning': 'text-amber-500',
        'error': 'text-red-500',
        'info': 'text-blue-500'
      }
      return classes[type] || 'text-gray-500'
    }

    const getAlertIconPath = (type) => {
      const paths = {
        'success': 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        'warning': 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
        'error': 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
        'info': 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
      }
      return paths[type] || 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
    }

    const getQualityChangeClass = (change) => {
      if (change > 0) return 'positive'
      if (change < 0) return 'negative'
      return 'neutral'
    }

    const getQualityChangeIcon = (change) => {
      if (change > 0) return 'fas fa-arrow-up'
      if (change < 0) return 'fas fa-arrow-down'
      return 'fas fa-minus'
    }

    const getAlertIcon = (type) => {
      const icons = {
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle',
        'info': 'fas fa-info-circle'
      }
      return icons[type] || 'fas fa-info-circle'
    }

    const viewUser = (userId) => {
      router.push(`/admin/users/${userId}`)
    }

    const editUser = (userId) => {
      router.push(`/admin/users/${userId}/edit`)
    }

    const dismissAlert = async (alertId) => {
      try {
        await adminStore.dismissAlert(alertId)
        alerts.value = alerts.value.filter(alert => alert.id !== alertId)
        Swal.fire({
          icon: 'success',
          title: 'Alerta Descartada',
          text: 'La alerta ha sido descartada exitosamente'
        })
      } catch (error) {
        console.error('Error dismissing alert:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo descartar la alerta'
        })
      }
    }

    // Sidebar event handlers
    const handleMenuClick = (menuItem) => {
      console.log('Menu clicked:', menuItem)
      
      if (menuItem.route) {
        // Navigate to the route
        router.push(menuItem.route)
      }
    }

    const handleLogout = async () => {
      try {
        await authStore.logout()
        // No redirigir aquí - authStore.logout() ya maneja la redirección
      } catch (error) {
        console.error('Error during logout:', error)
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'No se pudo cerrar la sesión'
        })
      }
    }

    // Navbar event handlers
    const handleSearch = (query) => {
      console.log('Search query:', query)
      searchQuery.value = query
      // Implementar lógica de búsqueda aquí
      if (query.trim()) {
        // Filtrar datos según la búsqueda
        console.log('Searching for:', query)
      }
    }

    const handlePeriodChange = (period) => {
      console.log('Period changed to:', period)
      selectedPeriod.value = period
      updatePeriod()
    }

    const handleRefresh = () => {
      console.log('Refreshing data...')
      refreshData()
    }

    // KPI Cards event handler - deshabilitado (sin navegación)
    const handleKPICardClick = (card) => {
      // Las cards ya no redirigen, esto es solo para compatibilidad
      console.log('KPI Card clicked (navigation disabled):', card.id)
    }

    // Charts event handlers
    const handleActivityChartTypeChange = (chartType) => {
      console.log('Activity chart type changed to:', chartType)
      activityChartType.value = chartType
      updateActivityChart()
    }

    const handleActivityRefresh = () => {
      console.log('Refreshing activity data...')
      refreshActivityData()
    }

    const handleQualityRefresh = () => {
      console.log('Refreshing quality data...')
      refreshQualityData()
    }

    const handleActivityClick = (event) => {
      console.log('Activity chart clicked:', event)
    }

    const handleQualityClick = (event) => {
      console.log('Quality chart clicked:', event)
    }

    // Tables event handlers
    const handleViewUser = (userId) => {
      console.log('View user clicked:', userId)
      router.push(`/admin/users/${userId}`)
    }

    const handleEditUser = (userId) => {
      console.log('Edit user clicked:', userId)
      router.push(`/admin/users/${userId}/edit`)
    }

    // Alerts event handlers
    const handleDismissAlert = (alertId) => {
      console.log('Dismiss alert clicked:', alertId)
      // Implementar lógica para descartar alerta
      Swal.fire({
        title: '¿Descartar alerta?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, descartar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          // Aquí implementarías la lógica para descartar la alerta
          console.log('Alert dismissed:', alertId)
          Swal.fire('Descartada', 'La alerta ha sido descartada', 'success')
        }
      })
    }

    // Event handlers para gráficos
    const handleStatClick = (stat) => {
      console.log('Stat clicked:', stat)
      // Implementar navegación según la estadística
    }

    // Lifecycle
    // Auto-refresh para datos en tiempo real
    let refreshInterval = null
    let statsInterval = null
    let quickRefreshInterval = null
    
    // Intervalos optimizados para tiempo real sin recargar página
    const QUICK_REFRESH_INTERVAL = 3000 // 3 segundos para datos críticos (alertas y actividades)
    const REFRESH_INTERVAL = 8000 // 8 segundos para datos dinámicos (usuarios, reportes)
    const STATS_INTERVAL = 25000 // 25 segundos para estadísticas completas (stats y gráficos)

    const setupRealtimeUpdates = () => {
      // Si WebSockets están disponibles, usarlos como principal
      if (websocket && websocket.hasAnyConnection?.value) {
        setupWebSocketListeners()
        // Usar polling como backup
        startPollingUpdates()
      } else {
        // Solo usar polling mejorado
        startPollingUpdates()
      }
    }

    const setupWebSocketListeners = () => {
      if (!websocket) return

      console.log('🔌 Configurando listeners de WebSocket para tiempo real...')

      // Escuchar actualizaciones de estadísticas de auditoría
      websocket.on?.('audit-stats-update', (data) => {
        console.log('📊 Stats actualizadas via WebSocket:', data)
        if (data) {
          if (data.users) stats.value.users = { ...stats.value.users, ...data.users }
          if (data.images) stats.value.images = { ...stats.value.images, ...data.images }
          if (data.fincas) stats.value.fincas = { ...stats.value.fincas, ...data.fincas }
          updateActivityChartFromStats()
          updateQualityChartFromStats()
        }
      })

      // Escuchar nuevas actividades en tiempo real
      websocket.on?.('audit-activity', (data) => {
        console.log('🆕 Nueva actividad recibida en tiempo real:', data)
        const processed = processActivityData(data)
        recentActivities.value = [processed, ...recentActivities.value].slice(0, 20)
      })

      // Escuchar nuevas notificaciones/alertas en tiempo real
      websocket.on?.('notification-received', (data) => {
        console.log('🚨 Nueva alerta recibida en tiempo real:', data)
        const processed = processAlertData(data)
        alerts.value = [processed, ...alerts.value].slice(0, 10)
      })

      // Escuchar actualizaciones de estadísticas de usuarios
      websocket.on?.('user-stats-update', (data) => {
        console.log('👥 Stats de usuarios actualizadas en tiempo real:', data)
        if (data?.users) {
          stats.value.users = { ...stats.value.users, ...data.users }
        }
      })
    }

    const startPollingUpdates = () => {
      console.log('🔄 Iniciando sistema de polling optimizado para tiempo real...')

      // Quick refresh cada 3 segundos para datos críticos
      quickRefreshInterval = setInterval(() => {
        Promise.all([
          loadAlerts(),
          loadRecentActivities()
        ]).catch(err => {
          console.error('Error en quick refresh:', err)
        })
      }, QUICK_REFRESH_INTERVAL)

      // Refresh normal cada 8 segundos para datos dinámicos
      refreshInterval = setInterval(() => {
        Promise.all([
          loadRecentUsers(),
          loadReportStats()
        ]).catch(err => {
          console.error('Error en refresh normal:', err)
        })
      }, REFRESH_INTERVAL)

      // Stats refresh cada 25 segundos (más costoso)
      statsInterval = setInterval(() => {
        Promise.all([
          loadStats(),
          loadQualityData(),
          updateActivityChart()
        ]).catch(err => {
          console.error('Error en refresh de stats:', err)
        })
      }, STATS_INTERVAL)

      console.log('✅ Sistema de polling iniciado (quick: 3s, normal: 8s, stats: 25s)')
    }

    const stopAutoRefresh = () => {
      if (quickRefreshInterval) {
        clearInterval(quickRefreshInterval)
        quickRefreshInterval = null
      }
      if (refreshInterval) {
        clearInterval(refreshInterval)
        refreshInterval = null
      }
      if (statsInterval) {
        clearInterval(statsInterval)
        statsInterval = null
      }

      // Limpiar listeners de WebSocket
      if (websocket) {
        websocket.off?.('audit-stats-update')
        websocket.off?.('audit-activity')
        websocket.off?.('notification-received')
        websocket.off?.('user-stats-update')
      }

      console.log('⏹️ Sistema de actualización en tiempo real detenido')
    }

    const startAutoRefresh = setupRealtimeUpdates

    onMounted(async () => {
      // Verificar permisos de administrador usando el sistema de roles
      if (!authStore.isAdmin) {
        console.warn('🚫 Usuario sin permisos de admin:', {
          userRole: authStore.userRole,
          isAdmin: authStore.isAdmin,
          user: authStore.user
        })
        router.push('/acceso-denegado')
        return
      }

      // Cargar datos iniciales
      await loadDashboardData()
      
      // Intentar conectar WebSocket para tiempo real
      if (websocket && authStore.user?.id) {
        try {
          await websocket.connect()
          console.log('✅ WebSocket conectado para actualizaciones en tiempo real')
        } catch (error) {
          console.warn('⚠️ No se pudo conectar WebSocket, usando polling:', error)
        }
      }
      
      // Iniciar sistema de actualización (WebSocket o polling)
      startAutoRefresh()
      
      // Los gráficos se crean automáticamente en DashboardCharts cuando los datos están listos
    })

    onUnmounted(() => {
      stopAutoRefresh()
      // Los gráficos se destruyen automáticamente en DashboardCharts
    })

    return {
      loading,
      stats,
      recentUsers,
      isSidebarCollapsed,
      toggleSidebarCollapse,
      recentActivities,
      alerts,
      reportStats,
      selectedPeriod,
      activityChartType,
      isRefreshing,
      lastUpdateTime,
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      searchQuery,
      activityChartTitle,
      qualityChartTitle,
      usersTableTitle,
      usersTableLink,
      usersTableLinkText,
      activityTableTitle,
      activityTableLink,
      activityTableLinkText,
      alertsTitle,
      noAlertsMessage,
      reportsTitle,
      reportsLink,
      reportsLinkText,
      totalReportsLabel,
      completedReportsLabel,
      generatingReportsLabel,
      failedReportsLabel,
      kpiCards,
      activityChartData,
      qualityChartData,
      activityChartOptions,
      qualityChartOptions,
      refreshData,
      updateActivityChart,
      refreshActivityData,
      refreshQualityData,
      updatePeriod,
      handleStatClick,
      handleMenuClick,
      handleLogout,
      handleSearch,
      handlePeriodChange,
      handleRefresh,
      handleKPICardClick: () => {}, // Removed navigation
      handleActivityChartTypeChange,
      handleActivityRefresh,
      handleQualityRefresh,
      handleActivityClick,
      handleQualityClick,
      handleViewUser,
      handleEditUser,
      handleDismissAlert,
      formatDate,
      formatDateTime,
      formatLastUpdate,
      getRoleBadgeClass,
      getActionBadgeClass,
      getAlertBorderClass,
      getAlertIconClass,
      getAlertIconPath,
      getQualityChangeClass,
      getQualityChangeIcon,
      getAlertIcon,
      viewUser,
      editUser,
      dismissAlert
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para el dashboard */
.dashboard-container {
  background-color: #f9fafb;
}

/* Mejoras para gráficos */
canvas {
  max-height: 320px;
  border-radius: 0.5rem;
}

/* Asegurar que los gráficos sean responsivos */
@media (max-width: 768px) {
  canvas {
    max-height: 250px;
  }
}

/* Animaciones suaves para elementos interactivos */
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Estilos para elementos de carga */
.loading-overlay {
  background-color: rgba(249, 250, 251, 0.8);
  backdrop-filter: blur(2px);
}

/* Espaciado consistente */
.section-spacing {
  margin-bottom: 2rem;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 640px) {
  .dashboard-header h1 {
    font-size: 1.875rem;
  }

  .dashboard-header p {
    font-size: 1rem;
  }
}

/* Estilos para elementos de estado */
.status-success {
  color: rgb(34 197 94);
}

.status-warning {
  color: rgb(245 158 11);
}

.status-error {
  color: rgb(239 68 68);
}

.status-info {
  color: rgb(59 130 246);
}
</style>