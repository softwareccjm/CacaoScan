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
      <!-- Overview Section -->
      <div v-if="activeSection === 'overview'" class="dashboard-section">
        <WelcomeHeader :farmer-name="farmerName" />
        
        <StatsCards 
          :total-batches="formattedStats.totalBatches"
          :avg-quality="formattedStats.avgQuality"
          :defect-rate="formattedStats.defectRate"
        />
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentActivity :recent-analyses="recentAnalyses" />
          <QuickActions 
            @nuevo-analisis="handleNuevoAnalisis"
            @gestionar-fincas="handleGestionarFincas"
          />
        </div>
      </div>

      <!-- Analysis Section -->
      <div v-if="activeSection === 'analysis'" class="dashboard-section">
        <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Nuevo Análisis de Lote</h1>
            <p class="text-gray-600">Sube imágenes de granos de cacao y completa la información del lote</p>
        </div>
        </div>
        
        <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
          <div class="p-8 space-y-8">
            <!-- Progress Indicator -->
            <ProgressIndicator v-if="isUploading" :progress="uploadProgress" label="Procesando imágenes..." />

            <!-- Batch Info Form -->
            <div class="bg-gray-50 rounded-lg p-6">
              <BatchInfoForm 
                v-model="batchData" 
                :errors="formErrors" 
                :user-role="'agricultor'"
                :user-name="farmerName"
                :user-id="authStore.user?.id"
                @update:modelValue="updateBatchData" 
              />
                  </div>
                  
            <!-- Image Upload Section -->
            <div class="space-y-6">
              <div class="text-center">
                <h2 class="text-2xl font-semibold text-gray-900 mb-3">Imágenes del Lote</h2>
                <p class="text-gray-600">Captura fotos de alta calidad de los granos de cacao</p>
              </div>

              <!-- Tabs -->
              <div class="bg-white border border-gray-200 rounded-lg p-1">
                <nav class="flex space-x-1">
                  <button
                    v-for="tab in tabs"
                    :key="tab.name"
                    @click="currentTab = tab.name"
                    :class="[
                      currentTab === tab.name
                        ? 'bg-green-600 text-white shadow-sm'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
                      'flex-1 py-3 px-4 text-sm font-medium rounded-md transition-colors duration-200'
                    ]"
                  >
                    {{ tab.label }}
                  </button>
                </nav>
              </div>

              <!-- Tab Content -->
              <div class="mt-6">
                <!-- File Upload Tab -->
                <div v-if="currentTab === 'upload'" class="bg-gray-50 rounded-lg p-6">
                  <ImageUploader
                    v-model="images"
                    @update:modelValue="updateImages"
                  />
                </div>

                <!-- Camera Capture Tab -->
                <div v-else-if="currentTab === 'camera'" class="space-y-6">
                  <div class="bg-gray-50 rounded-lg p-6">
                  <CameraCapture @capture="handleCapturedImage" />
                  </div>

                  <!-- Captured Images Preview -->
                  <div v-if="capturedImages.length > 0" class="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      Fotos capturadas ({{ capturedImages.length }})
                    </h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                      <div v-for="(img, index) in capturedImages" :key="index" class="relative group">
                        <div class="aspect-square rounded-lg overflow-hidden bg-gray-200">
                          <img :src="getImageUrl(img)" alt="Imagen capturada" class="w-full h-full object-cover" />
                        </div>
                        <button 
                          @click="removeCapturedImage(index)"
                          class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Submit Section -->
            <div class="pt-6 border-t border-gray-200">
              <div class="flex justify-between">
                <button 
                  @click="resetForm"
                  class="px-6 py-3 rounded-lg font-semibold text-gray-700 bg-white border-2 border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200"
                >
                  Limpiar
                </button>
                
                <button 
                  @click="submitAnalysis"
                  :disabled="!isFormValid || isSubmitting"
                  :class="[
                    'px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 shadow-md hover:shadow-lg',
                    (!isFormValid || isSubmitting) ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                  ]"
                >
                  {{ isSubmitting ? 'Procesando...' : 'Iniciar Análisis' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- History Section -->
      <div v-if="activeSection === 'history'" class="dashboard-section">
            <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900">Historial de Análisis</h1>
            <p class="text-gray-600 mt-1">Revisa todos tus análisis de granos de cacao</p>
          </div>
        </div>
        
        <ImageHistoryCard 
          :initial-images="recentAnalyses"
          :auto-load="true"
          @image-selected="handleImageSelected"
          @refresh-requested="refreshData"
        />
      </div>

      <!-- Reports Section -->
      <div v-if="activeSection === 'reports'" class="dashboard-section">
            <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900">Reportes</h1>
            <p class="text-gray-600 mt-1">Genera y visualiza reportes detallados de tus análisis</p>
                </div>
                </div>
                
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <p class="text-gray-600">Funcionalidad de reportes próximamente disponible</p>
              </div>
            </div>

      <!-- Settings Section -->
      <div v-if="activeSection === 'settings'" class="dashboard-section">
            <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900">Configuración</h1>
            <p class="text-gray-600 mt-1">Gestiona tu perfil y preferencias</p>
                </div>
                </div>
                
        <div class="settings-grid">
          <div class="settings-card">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Perfil de Usuario</h3>
            <div class="space-y-4">
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Nombre completo</label>
                <input type="text" v-model="userProfile.fullName" placeholder="Tu nombre completo" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                <input type="email" v-model="userProfile.email" placeholder="tu@email.com" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Teléfono</label>
                <input type="tel" v-model="userProfile.phone" placeholder="+57 300 123 4567" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
              <button type="button" class="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg">
                Guardar Cambios
              </button>
        </div>
      </div>

          <div class="settings-card">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Preferencias</h3>
            <div class="space-y-4 mb-6">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.notifications" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Recibir notificaciones por email</span>
                </label>
              </div>
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.autoReports" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Generar reportes automáticamente</span>
                </label>
              </div>
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.dataSharing" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Compartir datos anónimos para investigación</span>
                </label>
              </div>
            </div>
            <button type="button" class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg">
              Guardar Preferencias
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useAnalysisStore } from '@/stores/analysis';
import { useImageStats } from '@/composables/useImageStats'
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import WelcomeHeader from '@/components/agricultor/WelcomeHeader.vue'
import StatsCards from '@/components/agricultor/StatsCards.vue'
import RecentActivity from '@/components/agricultor/RecentActivity.vue'
import QuickActions from '@/components/agricultor/QuickActions.vue'
import ProgressIndicator from '@/components/admin/AdminAnalisisComponents/ProgressIndicator.vue'
import BatchInfoForm from '@/components/admin/AdminAnalisisComponents/BatchInfoForm.vue'
import ImageUploader from '@/components/admin/AdminAnalisisComponents/ImageUploader.vue'
import CameraCapture from '@/components/admin/AdminAnalisisComponents/CameraCapture.vue'

export default {
  name: 'AgricultorDashboard',
  components: {
    Sidebar,
    ImageHistoryCard,
    WelcomeHeader,
    StatsCards,
    RecentActivity,
    QuickActions,
    ProgressIndicator,
    BatchInfoForm,
    ImageUploader,
    CameraCapture
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Initialize activeSection from query parameter if present
    const sectionParam = router.currentRoute.value.query.section;
    const activeSection = ref(sectionParam || 'overview');
    
    // Usar composable para estadísticas reales
    const { 
      stats, 
      loading, 
      error, 
      fetchStats, 
      fetchImages, 
      generateReport,
      totalImages,
      processedImages,
      processingRate,
      averageConfidence,
      averageDimensions,
      regionStats,
      topFincas
    } = useImageStats();
    
    // Usar datos reales del usuario autenticado
    const farmerName = computed(() => authStore.userFullName || 'Usuario');
    
    // Datos de análisis recientes (ahora desde API)
    const recentAnalyses = ref([]);
    const imagesLoading = ref(false);
    
    // Cargar datos reales al montar el componente
    onMounted(async () => {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    });
    
    // Función para cargar análisis recientes
    async function loadRecentAnalyses() {
      imagesLoading.value = true;
      try {
        const data = await fetchImages(1, { page_size: '5' });
        recentAnalyses.value = data.results.map(image => ({
          id: `CAC-${image.id}`,
          status: image.processed ? 'completed' : 'pending',
          statusLabel: image.processed ? 'Completado' : 'Pendiente',
          quality: image.prediction ? Math.round(image.prediction.average_confidence * 100) : 0,
          defects: image.prediction ? Math.round((1 - image.prediction.average_confidence) * 100 * 10) / 10 : 0,
          avgSize: image.prediction ? Math.round((image.prediction.alto_mm + image.prediction.ancho_mm + image.prediction.grosor_mm) / 3 * 10) / 10 : 0,
          date: new Date(image.created_at).toLocaleDateString('es-ES')
        }));
      } catch (err) {
        console.error('Error loading recent analyses:', err);
      } finally {
        imagesLoading.value = false;
      }
    }
    
    // Función para generar reportes
    async function handleGenerateReport(reportType) {
      const success = await generateReport(reportType, {});
      if (success) {
        // Mostrar mensaje de éxito
        console.log(`Reporte ${reportType} generado exitosamente`);
      }
    }
    
    // Función para refrescar datos
    async function refreshData() {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    }
    
    // Función para manejar selección de imagen
    function handleImageSelected(image) {
      console.log('Imagen seleccionada:', image);
      // Aquí se puede agregar lógica adicional si es necesario
    }

    const handleNuevoAnalisis = () => {
      // Navegar a la vista de nuevo análisis (se debe crear como vista separada)
      alert('Redirigiendo a Nuevo Análisis...');
    };

    const handleGestionarFincas = () => {
      router.push({ name: 'AgricultorFincas' });
    };
    
    // Computed para estadísticas formateadas
    const formattedStats = computed(() => ({
      totalBatches: totalImages.value,
      batchesChange: '+0%', // TODO: Calcular cambio porcentual
      avgQuality: Math.round(averageConfidence.value * 100),
      qualityChange: '+0%', // TODO: Calcular cambio porcentual
      defectRate: Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
      defectChange: '+0%' // TODO: Calcular cambio porcentual
    }));
    
    

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        isSidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    const setActiveSection = (section) => {
      activeSection.value = section;
    };

    const handleMenuClick = (item) => {
      if (item.route && item.route !== null) {
        // If navigating to the same route, just update the activeSection
        if (router.currentRoute.value.path === item.route) {
          activeSection.value = 'overview';
        } else {
          router.push(item.route);
        }
      } else {
        // For internal sections without routes, just update activeSection
        // This allows switching between sections within the dashboard
        activeSection.value = item.id;
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

    // Variables para configuración
    const userProfile = ref({
      fullName: authStore.user?.full_name || '',
      email: authStore.user?.email || '',
      phone: ''
    });

    const userPreferences = ref({
      notifications: true,
      autoReports: false,
      dataSharing: false
    });

    // Analysis state
    const analysisStore = useAnalysisStore();
    const batchData = ref({
      name: '',
      collectionDate: '',
      origin: '',
      notes: ''
    });
    
    const images = ref([]);
    const capturedImages = ref([]);
    const currentTab = ref('upload');
    const isSubmitting = ref(false);
    const formErrors = ref({});
    const analysisResult = ref(null);
    const isUploading = ref(false);
    const uploadProgress = ref(0);

    const tabs = [
      { name: 'upload', label: 'Subir imágenes' },
      { name: 'camera', label: 'Tomar foto' }
    ];

    // Watch for captured images changes
    watch(capturedImages, (newVal) => {
      const uploadedImages = images.value.filter(img => !capturedImages.value.includes(img));
      images.value = [...uploadedImages, ...newVal];
    }, { deep: true });

    const isFormValid = computed(() => {
      return (
        batchData.value.name.trim() !== '' &&
        batchData.value.collectionDate &&
        images.value.length > 0
      );
    });

    const updateBatchData = (data) => {
      batchData.value = { ...data };
    };

    const updateImages = (newImages) => {
      images.value = newImages;
    };

    const getImageUrl = (img) => {
      if (img && img.preview) return img.preview;
      if (typeof img === 'string' && img.startsWith('data:')) return img;
      if (img && img.url) return img.url;
      return '';
    };

    const handleFileUpload = (event) => {
      const files = event.target.files;
      if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          const reader = new FileReader();
          reader.onload = (e) => {
            images.value.push({
              file: files[i],
              preview: e.target.result
            });
          };
          reader.readAsDataURL(files[i]);
        }
      }
    };

    const removeImage = (index) => {
      images.value.splice(index, 1);
    };

    const handleCapturedImage = (imageFile) => {
      if (!capturedImages.value.some(img => img.name === imageFile.name)) {
        capturedImages.value = [...capturedImages.value, imageFile];
      }
    };

    const removeCapturedImage = (index) => {
      capturedImages.value.splice(index, 1);
    };

    const resetForm = () => {
      batchData.value = {
        name: '',
        collectionDate: '',
        origin: '',
        notes: ''
      };
      images.value = [];
      capturedImages.value = [];
      currentTab.value = 'upload';
      analysisResult.value = null;
      formErrors.value = {};
    };

    const submitAnalysis = async () => {
      if (!isFormValid.value) return;

      try {
      isSubmitting.value = true;
        isUploading.value = true;
        uploadProgress.value = 0;
      analysisResult.value = null;

        analysisStore.setBatchData(batchData.value);
        analysisStore.images = [...images.value];

        // Simulate progress
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 90) {
            uploadProgress.value += 10;
          }
        }, 200);

        const result = await analysisStore.submitBatch();
        
        clearInterval(progressInterval);
        uploadProgress.value = 100;
        analysisResult.value = result;
        
        setTimeout(() => {
          resetForm();
        }, 3000);
      } catch (err) {
        console.error('Error submitting analysis:', err);
        formErrors.value = { general: err.message || 'Error al procesar el análisis' };
      } finally {
        isSubmitting.value = false;
        isUploading.value = false;
      }
    };

    return {
      // Stores
      authStore,
      // Sidebar
      isSidebarCollapsed,
      activeSection,
      // Dashboard
      farmerName,
      recentAnalyses,
      formattedStats,
      loading,
      error,
      imagesLoading,
      userProfile,
      userPreferences,
      checkScreenSize,
      setActiveSection,
      handleMenuClick,
      toggleSidebarCollapse,
      logout,
      handleGenerateReport,
      refreshData,
      loadRecentAnalyses,
      handleImageSelected,
      handleNuevoAnalisis,
      handleGestionarFincas,
      // Analysis
      batchData,
      images,
      capturedImages,
      currentTab,
      isSubmitting,
      formErrors,
      analysisResult,
      isUploading,
      uploadProgress,
      tabs,
      isFormValid,
      updateBatchData,
      updateImages,
      getImageUrl,
      removeImage,
      handleCapturedImage,
      removeCapturedImage,
      resetForm,
      submitAnalysis
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