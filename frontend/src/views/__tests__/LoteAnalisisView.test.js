import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoteAnalisisView from '../LoteAnalisisView.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    accessToken: 'mock-token'
  })
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => ({
    showNotification: vi.fn()
  }),
  useNotificationsStore: () => ({
    showNotification: vi.fn()
  })
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRoute: () => ({ params: { id: '1' }, query: {} }),
    useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() })
  }
})

import api from '@/services/api'

describe('LoteAnalisisView', () => {
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

  it('should render loading state initially', () => {
    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.text()).toContain('Cargando')
  })

  it('should render error state when error occurs', async () => {
    api.get.mockRejectedValue(new Error('Network error'))

    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('Error')
  })

  it('should render lote information when loaded', async () => {
    const mockLote = {
      id: 1,
      identificador: 'Lote A',
      variedad: 'Criollo',
      area_hectareas: 5.5,
      fecha_plantacion: '2024-01-01',
      finca: 1
    }

    api.get.mockImplementation((url) => {
      if (url.includes('/lotes/1/analisis/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/lotes/1/')) {
        return Promise.resolve({ data: mockLote })
      }
      if (url.includes('/fincas/')) {
        return Promise.resolve({ data: { id: 1, nombre: 'F' } })
      }
      return Promise.resolve({ data: {} })
    })

    wrapper = mount(LoteAnalisisView, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Lote A')
  })
})

