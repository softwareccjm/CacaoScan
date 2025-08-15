<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Page Header -->
      <PageHeader
        title="Nuevo Análisis de Lote"
        description="Sube imágenes de granos de cacao y completa la información del lote para iniciar un análisis de calidad detallado y preciso."
      />

      <!-- Main Content -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="p-6 space-y-8">
          <!-- Progress Indicator -->
          <ProgressIndicator
            v-if="isUploading"
            :progress="uploadProgress"
            label="Procesando imágenes..."
          />

          <!-- Error Alert -->
          <ErrorAlert
            v-if="error"
            :message="error"
          />

          <!-- Success Alert -->
          <div v-if="analysisResult" class="bg-green-50 border-l-4 border-green-400 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-green-800">
                  Análisis completado exitosamente
                </p>
                <div class="mt-2">
                  <p class="text-sm text-green-700">
                    ID de análisis: {{ analysisResult.analysisId }}
                  </p>
                  <div class="mt-2">
                    <router-link
                      :to="{ name: 'analisis-detalle', params: { id: analysisResult.analysisId } }"
                      class="inline-flex items-center text-sm font-medium text-green-700 hover:text-green-600"
                    >
                      Ver resultados detallados
                      <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Batch Info Form -->
          <BatchInfoForm
            v-model="batchData"
            :errors="formErrors"
            @update:modelValue="updateBatchData"
          />

          <!-- Image Uploader -->
          <div class="space-y-4">
            <h2 class="text-lg font-medium text-gray-900">Imágenes del Lote</h2>
            <ImageUploader
              v-model="images"
              @update:modelValue="updateImages"
            />
          </div>

          <!-- Submit Button -->
          <div class="pt-4">
            <button
              type="button"
              @click="submitAnalysis"
              :disabled="isSubmitting || !isFormValid"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isSubmitting ? 'Procesando...' : 'Iniciar Análisis' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useAnalysisStore } from '@/stores/analysis';
import PageHeader from '@/components/common/PageHeader.vue';
import ProgressIndicator from '@/components/common/ProgressIndicator.vue';
import ErrorAlert from '@/components/common/ErrorAlert.vue';
import BatchInfoForm from '@/components/analysis/BatchInfoForm.vue';
import ImageUploader from '@/components/analysis/ImageUploader.vue';

export default {
  name: 'NuevoAnalisis',
  components: {
    PageHeader,
    ProgressIndicator,
    ErrorAlert,
    BatchInfoForm,
    ImageUploader
  },
  setup() {
    const analysisStore = useAnalysisStore();

    // Local state
    const batchData = ref({
      name: '',
      collectionDate: '',
      origin: '',
      notes: ''
    });

    const images = ref([]);
    const isSubmitting = ref(false);
    const formErrors = ref({});
    const analysisResult = ref(null);

    // Computed properties
    const isFormValid = computed(() => {
      return (
        batchData.value.name.trim() !== '' &&
        batchData.value.collectionDate &&
        images.value.length > 0
      );
    });

    const uploadProgress = computed(() => {
      return analysisStore.uploadProgress;
    });

    const isUploading = computed(() => {
      return analysisStore.isUploading;
    });

    const error = computed(() => {
      return analysisStore.uploadError;
    });

    // Methods
    const updateBatchData = (data) => {
      batchData.value = { ...data };
    };

    const updateImages = (newImages) => {
      images.value = [...newImages];
    };

    const validateForm = () => {
      const errors = {};

      if (!batchData.value.name.trim()) {
        errors.name = 'El nombre del lote es requerido';
      }

      if (!batchData.value.collectionDate) {
        errors.collectionDate = 'La fecha de recolección es requerida';
      }

      if (images.value.length === 0) {
        errors.images = 'Debes subir al menos una imagen';
      }

      formErrors.value = errors;
      return Object.keys(errors).length === 0;
    };

    const submitAnalysis = async () => {
      if (!validateForm()) return;

      try {
        isSubmitting.value = true;
        analysisResult.value = null;

        // Update store with form data
        analysisStore.setBatchData(batchData.value);

        // Add images to store
        analysisStore.images = [...images.value];

        // Submit to API
        const result = await analysisStore.submitBatch();

        // Handle success
        analysisResult.value = result;

        // Reset form after successful submission
        if (result) {
          resetForm();
        }

      } catch (error) {
        console.error('Error submitting analysis:', error);
      } finally {
        isSubmitting.value = false;
      }
    };

    const resetForm = () => {
      batchData.value = {
        name: '',
        collectionDate: '',
        origin: '',
        notes: ''
      };
      images.value = [];
      formErrors.value = {};
    };

    // Lifecycle hooks
    onMounted(() => {
      // Reset store when component is mounted
      analysisStore.clearBatch();
    });

    return {
      // State
      batchData,
      images,
      isSubmitting,
      formErrors,
      analysisResult,

      // Computed
      isFormValid,
      uploadProgress,
      isUploading,
      error,

      // Methods
      updateBatchData,
      updateImages,
      submitAnalysis,
      resetForm
    };
  }
};
</script>

<style scoped>
/* Add any custom styles here */
</style>
