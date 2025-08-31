<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Mi Perfil</h1>
              <p class="text-gray-600">Gestiona tu información personal y configuraciones</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="h-12 w-12 rounded-full bg-green-600 flex items-center justify-center text-white text-lg font-medium">
                {{ authStore.userInitials }}
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">{{ authStore.userFullName }}</p>
                <p class="text-sm text-gray-500 capitalize">{{ getRoleText(authStore.userRole) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado de verificación -->
      <div v-if="!authStore.isVerified" class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-yellow-800">Email no verificado</h3>
            <p class="mt-1 text-sm text-yellow-700">Verifica tu email para acceder a todas las funcionalidades.</p>
            <div class="mt-3">
              <router-link
                to="/verificar-email"
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-800 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
              >
                Verificar Ahora
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Información Personal -->
        <div class="lg:col-span-2">
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Información Personal</h2>
            </div>
            <div class="px-6 py-4">
              <form @submit.prevent="updateProfile" class="space-y-6">
                <!-- Nombres -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label for="firstName" class="block text-sm font-medium text-gray-700 mb-2">
                      Nombre
                    </label>
                    <input
                      id="firstName"
                      v-model="profileForm.firstName"
                      type="text"
                      required
                      :disabled="isLoading"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      :class="{ 'border-red-500': errors.firstName }"
                    />
                    <p v-if="errors.firstName" class="mt-1 text-sm text-red-600">{{ errors.firstName }}</p>
                  </div>
                  
                  <div>
                    <label for="lastName" class="block text-sm font-medium text-gray-700 mb-2">
                      Apellido
                    </label>
                    <input
                      id="lastName"
                      v-model="profileForm.lastName"
                      type="text"
                      required
                      :disabled="isLoading"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      :class="{ 'border-red-500': errors.lastName }"
                    />
                    <p v-if="errors.lastName" class="mt-1 text-sm text-red-600">{{ errors.lastName }}</p>
                  </div>
                </div>

                <!-- Email (solo lectura) -->
                <div>
                  <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <div class="relative">
                    <input
                      id="email"
                      :value="authStore.user?.email"
                      type="email"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />
                    <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                      <span v-if="authStore.isVerified" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        Verificado
                      </span>
                      <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                        No verificado
                      </span>
                    </div>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">El email no se puede cambiar por motivos de seguridad.</p>
                </div>

                <!-- Teléfono -->
                <div>
                  <label for="phoneNumber" class="block text-sm font-medium text-gray-700 mb-2">
                    Teléfono (opcional)
                  </label>
                  <input
                    id="phoneNumber"
                    v-model="profileForm.phoneNumber"
                    type="tel"
                    :disabled="isLoading"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                    :class="{ 'border-red-500': errors.phoneNumber }"
                    placeholder="+57 300 123 4567"
                  />
                  <p v-if="errors.phoneNumber" class="mt-1 text-sm text-red-600">{{ errors.phoneNumber }}</p>
                </div>

                <!-- Campos específicos para agricultores -->
                <div v-if="authStore.isFarmer" class="space-y-4 pt-4 border-t border-gray-200">
                  <h3 class="text-lg font-medium text-gray-900">Información de Finca</h3>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="region" class="block text-sm font-medium text-gray-700 mb-2">
                        Región
                      </label>
                      <input
                        id="region"
                        v-model="profileForm.region"
                        type="text"
                        :disabled="isLoading"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                        placeholder="Huila, Tolima, etc."
                      />
                    </div>
                    
                    <div>
                      <label for="municipality" class="block text-sm font-medium text-gray-700 mb-2">
                        Municipio
                      </label>
                      <input
                        id="municipality"
                        v-model="profileForm.municipality"
                        type="text"
                        :disabled="isLoading"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                        placeholder="Pitalito, Ibagué, etc."
                      />
                    </div>
                  </div>

                  <div>
                    <label for="farmName" class="block text-sm font-medium text-gray-700 mb-2">
                      Nombre de la Finca
                    </label>
                    <input
                      id="farmName"
                      v-model="profileForm.farmName"
                      type="text"
                      :disabled="isLoading"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      placeholder="Finca El Cacao"
                    />
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="yearsExperience" class="block text-sm font-medium text-gray-700 mb-2">
                        Años de Experiencia
                      </label>
                      <input
                        id="yearsExperience"
                        v-model.number="profileForm.yearsExperience"
                        type="number"
                        min="0"
                        max="100"
                        :disabled="isLoading"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                        placeholder="10"
                      />
                    </div>
                    
                    <div>
                      <label for="farmSizeHectares" class="block text-sm font-medium text-gray-700 mb-2">
                        Tamaño de Finca (hectáreas)
                      </label>
                      <input
                        id="farmSizeHectares"
                        v-model.number="profileForm.farmSizeHectares"
                        type="number"
                        step="0.1"
                        min="0"
                        :disabled="isLoading"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                        placeholder="5.5"
                      />
                    </div>
                  </div>
                </div>

                <!-- Preferencias -->
                <div class="pt-4 border-t border-gray-200">
                  <h3 class="text-lg font-medium text-gray-900 mb-4">Preferencias</h3>
                  
                  <div class="space-y-4">
                    <div>
                      <label for="preferredLanguage" class="block text-sm font-medium text-gray-700 mb-2">
                        Idioma Preferido
                      </label>
                      <select
                        id="preferredLanguage"
                        v-model="profileForm.preferredLanguage"
                        :disabled="isLoading"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      >
                        <option value="es">Español</option>
                        <option value="en">English</option>
                      </select>
                    </div>

                    <div class="flex items-center">
                      <input
                        id="emailNotifications"
                        v-model="profileForm.emailNotifications"
                        type="checkbox"
                        :disabled="isLoading"
                        class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                      />
                      <label for="emailNotifications" class="ml-2 block text-sm text-gray-700">
                        Recibir notificaciones por email
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Botones -->
                <div class="flex justify-end space-x-3 pt-6">
                  <button
                    type="button"
                    @click="resetForm"
                    :disabled="isLoading"
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    :disabled="isLoading"
                    class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                  >
                    <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isLoading ? 'Guardando...' : 'Guardar Cambios' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Panel lateral -->
        <div class="space-y-6">
          <!-- Cambiar contraseña -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Seguridad</h2>
            </div>
            <div class="px-6 py-4">
              <button
                @click="showPasswordForm = !showPasswordForm"
                class="w-full flex justify-between items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <span>Cambiar Contraseña</span>
                <svg class="h-5 w-5" :class="{ 'rotate-180': showPasswordForm }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>

              <!-- Formulario de cambio de contraseña -->
              <div v-show="showPasswordForm" class="mt-4 space-y-4">
                <form @submit.prevent="changePassword">
                  <div class="space-y-4">
                    <div>
                      <label for="currentPassword" class="block text-sm font-medium text-gray-700 mb-2">
                        Contraseña Actual
                      </label>
                      <input
                        id="currentPassword"
                        v-model="passwordForm.currentPassword"
                        type="password"
                        required
                        :disabled="isLoadingPassword"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      />
                    </div>

                    <div>
                      <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-2">
                        Nueva Contraseña
                      </label>
                      <input
                        id="newPassword"
                        v-model="passwordForm.newPassword"
                        type="password"
                        required
                        :disabled="isLoadingPassword"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      />
                    </div>

                    <div>
                      <label for="confirmNewPassword" class="block text-sm font-medium text-gray-700 mb-2">
                        Confirmar Nueva Contraseña
                      </label>
                      <input
                        id="confirmNewPassword"
                        v-model="passwordForm.confirmPassword"
                        type="password"
                        required
                        :disabled="isLoadingPassword"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                      />
                    </div>

                    <button
                      type="submit"
                      :disabled="isLoadingPassword"
                      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      {{ isLoadingPassword ? 'Cambiando...' : 'Cambiar Contraseña' }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Información de cuenta -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Información de Cuenta</h2>
            </div>
            <div class="px-6 py-4 space-y-4">
              <div>
                <dt class="text-sm font-medium text-gray-500">Usuario desde</dt>
                <dd class="text-sm text-gray-900">{{ formatDate(authStore.user?.date_joined) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Última actividad</dt>
                <dd class="text-sm text-gray-900">{{ formatDate(authStore.user?.last_login) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Rol</dt>
                <dd class="text-sm text-gray-900 capitalize">{{ getRoleText(authStore.userRole) }}</dd>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mensajes de estado -->
      <div v-if="statusMessage" class="fixed bottom-4 right-4 max-w-sm">
        <div class="rounded-md p-4" :class="statusMessageClass">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg v-if="statusType === 'success'" class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <svg v-else class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium" :class="statusType === 'success' ? 'text-green-800' : 'text-red-800'">
                {{ statusMessage }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Store
const authStore = useAuthStore()

// Estado del componente
const isLoading = ref(false)
const isLoadingPassword = ref(false)
const showPasswordForm = ref(false)
const statusMessage = ref('')
const statusType = ref('info')
const errors = ref({})

// Formularios
const profileForm = ref({
  firstName: '',
  lastName: '',
  phoneNumber: '',
  region: '',
  municipality: '',
  farmName: '',
  yearsExperience: null,
  farmSizeHectares: null,
  preferredLanguage: 'es',
  emailNotifications: true
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Computed
const statusMessageClass = computed(() => {
  return statusType.value === 'success' 
    ? 'bg-green-50 border border-green-200'
    : 'bg-red-50 border border-red-200'
})

// Métodos
const getRoleText = (role) => {
  const roleTexts = {
    farmer: 'Agricultor',
    analyst: 'Analista',
    admin: 'Administrador'
  }
  return roleTexts[role] || 'Usuario'
}

const formatDate = (dateString) => {
  if (!dateString) return 'No disponible'
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const setStatusMessage = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const loadUserData = () => {
  if (authStore.user) {
    const user = authStore.user
    const profile = user.profile || {}
    
    profileForm.value = {
      firstName: user.first_name || '',
      lastName: user.last_name || '',
      phoneNumber: user.phone_number || '',
      region: profile.region || '',
      municipality: profile.municipality || '',
      farmName: profile.farm_name || '',
      yearsExperience: profile.years_experience || null,
      farmSizeHectares: profile.farm_size_hectares || null,
      preferredLanguage: profile.preferred_language || 'es',
      emailNotifications: profile.email_notifications !== false
    }
  }
}

const resetForm = () => {
  loadUserData()
  errors.value = {}
}

const validateProfileForm = () => {
  errors.value = {}
  
  if (!profileForm.value.firstName.trim()) {
    errors.value.firstName = 'El nombre es requerido'
  }
  
  if (!profileForm.value.lastName.trim()) {
    errors.value.lastName = 'El apellido es requerido'
  }
  
  if (profileForm.value.phoneNumber && !isValidPhone(profileForm.value.phoneNumber)) {
    errors.value.phoneNumber = 'Ingresa un número de teléfono válido'
  }
  
  return Object.keys(errors.value).length === 0
}

const isValidPhone = (phone) => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  return phoneRegex.test(phone.replace(/\s/g, ''))
}

const updateProfile = async () => {
  if (!validateProfileForm()) {
    return
  }

  isLoading.value = true

  try {
    const result = await authStore.updateProfile(profileForm.value)
    
    if (result.success) {
      setStatusMessage('Perfil actualizado exitosamente', 'success')
    } else {
      setStatusMessage(result.error || 'Error al actualizar perfil', 'error')
    }
  } catch (error) {
    console.error('Error actualizando perfil:', error)
    setStatusMessage('Error inesperado al actualizar perfil', 'error')
  } finally {
    isLoading.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    setStatusMessage('Las contraseñas no coinciden', 'error')
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    setStatusMessage('La nueva contraseña debe tener al menos 8 caracteres', 'error')
    return
  }

  isLoadingPassword.value = true

  try {
    const result = await authStore.changePassword({
      oldPassword: passwordForm.value.currentPassword,
      newPassword: passwordForm.value.newPassword,
      confirmPassword: passwordForm.value.confirmPassword
    })
    
    if (result.success) {
      setStatusMessage('Contraseña cambiada exitosamente', 'success')
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      showPasswordForm.value = false
    } else {
      setStatusMessage(result.error || 'Error al cambiar contraseña', 'error')
    }
  } catch (error) {
    console.error('Error cambiando contraseña:', error)
    setStatusMessage('Error inesperado al cambiar contraseña', 'error')
  } finally {
    isLoadingPassword.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
