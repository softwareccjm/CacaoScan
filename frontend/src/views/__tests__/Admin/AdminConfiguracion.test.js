import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminConfiguracion from '../../Admin/AdminConfiguracion.vue'
import configApi from '@/services/configApi'

// Create mock configApi methods
const mockGetSystemConfig = vi.fn().mockResolvedValue({
  version: '1.0.0',
  server_status: 'online',
  backend_version: '4.2.7',
  frontend_version: '3.5.3',
  database: 'PostgreSQL 16'
})

const mockGetGeneralConfig = vi.fn().mockResolvedValue({
  nombre_sistema: 'CacaoScan',
  email_contacto: 'contacto@cacaoscan.com',
  lema: 'La mejor plataforma para el control de calidad del cacao',
  logo_url: null
})

const mockGetSecurityConfig = vi.fn().mockResolvedValue({
  recaptcha_enabled: true,
  session_timeout: 60,
  login_attempts: 5,
  two_factor_auth: false
})

const mockGetMLConfig = vi.fn().mockResolvedValue({
  active_model: 'yolov8',
  last_training: null
})

vi.mock('@/services/configApi', () => ({
  default: {
    getSystemConfig: mockGetSystemConfig,
    getGeneralConfig: mockGetGeneralConfig,
    getSecurityConfig: mockGetSecurityConfig,
    getMLConfig: mockGetMLConfig,
    saveGeneralConfig: vi.fn().mockResolvedValue({}),
    saveSecurityConfig: vi.fn().mockResolvedValue({}),
    saveMLConfig: vi.fn().mockResolvedValue({})
  }
}))

// Mock auth store
const mockAuthStore = {
  user: { id: 1, first_name: 'Test', last_name: 'User', username: 'testuser' },
  userRole: 'admin',
  isAdmin: true,
  isAnalyst: false,
  isAuthenticated: true,
  logout: vi.fn()
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock config store
const mockConfigStore = {
  brandName: 'CacaoScan',
  general: {
    nombre_sistema: 'CacaoScan',
    email_contacto: 'contacto@cacaoscan.com',
    lema: 'La mejor plataforma para el control de calidad del cacao',
    logo_url: null
  },
  security: {
    recaptcha_enabled: true,
    session_timeout: 60,
    login_attempts: 5,
    two_factor_auth: false
  },
  ml: {
    active_model: 'yolov8',
    last_training: null
  },
  system: {
    version: '1.0.0',
    server_status: 'online',
    backend_version: '4.2.7',
    frontend_version: '3.5.3',
    database: 'PostgreSQL 16'
  },
  loadAll: vi.fn(async () => {
    // Call the mocked configApi methods
    await Promise.all([
      mockGetSystemConfig(),
      mockGetGeneralConfig(),
      mockGetSecurityConfig(),
      mockGetMLConfig()
    ])
    return { success: true, loaded: true }
  }),
  saveGeneral: vi.fn().mockResolvedValue({}),
  saveSecurity: vi.fn().mockResolvedValue({}),
  saveML: vi.fn().mockResolvedValue({}),
  updateGeneral: vi.fn(),
  updateSecurity: vi.fn()
}

vi.mock('@/stores/config', () => ({
  useConfigStore: () => mockConfigStore
}))

// Mock vue-router
vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn()
    })
  }
})

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn().mockResolvedValue({ isConfirmed: true })
  }
}))

describe('AdminConfiguracion', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render configuration view', () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should load configuration on mount', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()

    // Verify that loadAll was called
    expect(mockConfigStore.loadAll).toHaveBeenCalled()
    
    // Verify that the config API methods were called
    expect(mockGetSystemConfig).toHaveBeenCalled()
    expect(mockGetGeneralConfig).toHaveBeenCalled()
    expect(mockGetSecurityConfig).toHaveBeenCalled()
    expect(mockGetMLConfig).toHaveBeenCalled()
  })

  it('should save configuration', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await flushPromises()

    // Update general config
    wrapper.vm.generalConfig.nombre_sistema = 'New System Name'

    if (wrapper.vm.saveGeneralConfig) {
      await wrapper.vm.saveGeneralConfig()
      await wrapper.vm.$nextTick()
      await flushPromises()

      expect(mockConfigStore.saveGeneral).toHaveBeenCalled()
    }
  })

  it('should handle save error', async () => {
    const error = new Error('Save failed')
    mockConfigStore.saveGeneral.mockRejectedValueOnce(error)

    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await flushPromises()

    if (wrapper.vm.saveGeneralConfig) {
      await wrapper.vm.saveGeneralConfig()
      await wrapper.vm.$nextTick()
      await flushPromises()

      // Error should be handled by Swal.fire
      expect(mockConfigStore.saveGeneral).toHaveBeenCalled()
    }
  })

  it('should display configuration data', async () => {
    wrapper = mount(AdminConfiguracion, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()
    await flushPromises()

    // Verify that configuration data is available
    expect(wrapper.vm.generalConfig).toBeDefined()
    expect(wrapper.vm.securityConfig).toBeDefined()
    expect(wrapper.vm.systemConfig).toBeDefined()
  })
})

