<template>
  <div class="space-y-6">
    <h2 class="text-lg font-medium text-gray-900">Información del Lote</h2>
    
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <!-- Finca -->
      <div>
        <label for="farm" class="block text-sm font-medium text-gray-700">
          Finca <span class="text-red-500">*</span>
        </label>
        <select
          id="farm"
          v-model="formData.farm"
          @change="updateForm"
          :disabled="loadingFincas"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.farm, 'bg-gray-100 cursor-wait': loadingFincas }"
        >
          <option value="">{{ loadingFincas ? 'Cargando fincas...' : 'Selecciona una finca' }}</option>
          <option v-for="finca in fincas" :key="finca.id" :value="finca.nombre">
            {{ finca.nombre }} - {{ finca.ubicacion || 'Sin ubicación' }}
          </option>
        </select>
        <p v-if="errors.farm" class="mt-1 text-sm text-red-600">{{ errors.farm }}</p>
        <p v-if="fincas.length === 0 && !loadingFincas" class="mt-1 text-xs text-amber-600">
          {{ userRole === 'agricultor' ? 'No tienes fincas registradas' : 'No hay fincas disponibles' }}
        </p>
      </div>

      <!-- Lugar de Origen -->
      <div>
        <label for="originPlace" class="block text-sm font-medium text-gray-700">
          Lugar de origen <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="originPlace"
          v-model="formData.originPlace"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.originPlace }"
        />
        <p v-if="errors.originPlace" class="mt-1 text-sm text-red-600">{{ errors.originPlace }}</p>
      </div>

      <!-- Agricultor -->
      <div>
        <label for="farmer" class="block text-sm font-medium text-gray-700">
          Agricultor <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="farmer"
          v-model="formData.farmer"
          @input="updateForm"
          :readonly="userRole === 'agricultor'"
          :class="[
            'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500',
            { 'border-red-500': errors.farmer },
            { 'bg-gray-100 cursor-not-allowed': userRole === 'agricultor' }
          ]"
        />
        <p v-if="errors.farmer" class="mt-1 text-sm text-red-600">{{ errors.farmer }}</p>
        <p v-if="userRole === 'agricultor'" class="mt-1 text-xs text-gray-500">
          Este campo se completa automáticamente con tu nombre
        </p>
      </div>

      <!-- Genética -->
      <div>
        <label for="genetics" class="block text-sm font-medium text-gray-700">
          Genética <span class="text-red-500">*</span>
        </label>
        <select
          id="genetics"
          v-model="formData.genetics"
          @change="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.genetics }"
        >
          <option value="">Selecciona la genética</option>
          <option value="Criollo">Criollo</option>
          <option value="Forastero">Forastero</option>
          <option value="Trinitario">Trinitario</option>
          <option value="Nacional">Nacional</option>
          <option value="Híbrido">Híbrido</option>
          <option value="Otra">Otra</option>
        </select>
        <p v-if="errors.genetics" class="mt-1 text-sm text-red-600">{{ errors.genetics }}</p>
      </div>

      <!-- Nombre del Lote -->
      <div class="col-span-full sm:col-span-2">
        <label for="batchName" class="block text-sm font-medium text-gray-700">
          Nombre o código del lote <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="batchName"
          v-model="formData.name"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.name }"
        />
        <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
      </div>

      <!-- Fecha de Recolección -->
      <div>
        <label for="collectionDate" class="block text-sm font-medium text-gray-700">
          Fecha de recolección <span class="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="collectionDate"
          v-model="formData.collectionDate"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.collectionDate }"
          max=""
        />
        <p v-if="errors.collectionDate" class="mt-1 text-sm text-red-600">{{ errors.collectionDate }}</p>
      </div>

      <!-- Origen -->
      <div>
        <label for="origin" class="block text-sm font-medium text-gray-700">
          Origen
        </label>
        <div class="mt-1">
          <select
            id="origin"
            v-model="formData.origin"
            @change="updateForm"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="">Selecciona un origen</option>
            <option value="Piura">Piura</option>
            <option value="San Martín">San Martín</option>
            <option value="Cajamarca">Cajamarca</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Observaciones -->
    <div>
      <label for="notes" class="block text-sm font-medium text-gray-700">
        Observaciones (opcional)
      </label>
      <div class="mt-1">
        <textarea
          id="notes"
          v-model="formData.notes"
          @input="updateForm"
          rows="3"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          placeholder="Notas adicionales sobre el lote..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { getFincas } from '@/services/fincasApi';

export default {
  name: 'BatchInfoForm',
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    errors: {
      type: Object,
      default: () => ({})
    },
    userRole: {
      type: String,
      default: 'admin'
    },
    userName: {
      type: String,
      default: ''
    },
    userId: {
      type: Number,
      default: null
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const formData = ref({
      farm: '',
      originPlace: '',
      farmer: '',
      genetics: '',
      ...props.modelValue
    });

    const fincas = ref([]);
    const loadingFincas = ref(false);

    // Load fincas from backend
    const loadFincas = async () => {
      loadingFincas.value = true;
      try {
        const response = await getFincas();
        
        if (props.userRole === 'agricultor' && props.userId) {
          // Filter only fincas owned by the current user
          fincas.value = response.results?.filter(finca => finca.propietario === props.userId) || [];
        } else {
          // Admin sees all fincas
          fincas.value = response.results || [];
        }
      } catch (error) {
        console.error('Error loading fincas:', error);
        fincas.value = [];
      } finally {
        loadingFincas.value = false;
      }
    };

    // Set max date to today and auto-fill farmer name for agricultor role
    onMounted(async () => {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('collectionDate')?.setAttribute('max', today);
      
      // Load fincas
      await loadFincas();
      
      // Auto-fill farmer name if user is agricultor
      if (props.userRole === 'agricultor' && props.userName && !formData.value.farmer) {
        formData.value.farmer = props.userName;
        emit('update:modelValue', { ...formData.value });
      }
    });

    const updateForm = () => {
      emit('update:modelValue', { ...formData.value });
    };

    // Watch for changes in modelValue from parent
    watch(() => props.modelValue, (newValue) => {
      formData.value = { ...newValue };
    }, { deep: true });

    return {
      formData,
      updateForm,
      userRole: props.userRole,
      fincas,
      loadingFincas
    };
  }
};
</script>
