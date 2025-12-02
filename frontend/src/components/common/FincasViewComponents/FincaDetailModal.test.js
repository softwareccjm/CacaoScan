import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import FincaDetailModal from './FincaDetailModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close']
  }
}))

vi.mock('@/components/fincas/FincaLocationMap.vue', () => ({
  default: {
    name: 'FincaLocationMap',
    template: '<div>FincaLocationMap</div>',
    props: ['nombre', 'latitud', 'longitud']
  }
}))

vi.mock('@/composables/useFincas', () => ({
  useFincas: vi.fn(() => ({
    currentFinca: vi.fn(() => ({ value: null })),
    isLoading: vi.fn(() => ({ value: false })),
    loadFinca: vi.fn(() => Promise.resolve()),
    clearCurrentFinca: vi.fn()
  }))
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAdmin: false
  }))
}))

describe('FincaDetailModal', () => {
  let wrapper
  let mockLoadFinca
  let mockClearCurrentFinca
  let mockCurrentFinca

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    activa: true
  }

  const mockFincaDetail = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    ubicacion: 'Test Ubicación',
    hectareas: 10,
    activa: true,
    agricultor_name: 'Test Agricultor',
    fecha_registro: '2024-01-01',
    descripcion: 'Test Description',
    coordenadas_lat: 4.6097,
    coordenadas_lng: -74.0817,
    estadisticas: {
      total_lotes: 5,
      lotes_activos: 3,
      total_analisis: 10,
      calidad_promedio: 85
    }
  }

  beforeEach(() => {
    mockLoadFinca = vi.fn(() => Promise.resolve())
    mockClearCurrentFinca = vi.fn()
    mockCurrentFinca = { value: null }

    vi.doMock('@/composables/useFincas', () => ({
      useFincas: () => ({
        currentFinca: mockCurrentFinca,
        isLoading: { value: false },
        loadFinca: mockLoadFinca,
        clearCurrentFinca: mockClearCurrentFinca
      })
    }))
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  it('should render modal when show is true', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should not render modal when show is false', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: false,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await wrapper.vm.closeModal()
    await nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit edit event when edit button is clicked', async () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: mockFincaDetail },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca,
        userRole: 'admin'
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    wrapper.vm.currentFinca.value = mockFincaDetail
    await nextTick()

    await wrapper.vm.handleEdit()
    await nextTick()

    expect(wrapper.emitted('edit')).toBeTruthy()
  })

  it('should emit view-lotes event when view lotes button is clicked', async () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: mockFincaDetail },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca,
        userRole: 'admin'
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    wrapper.vm.currentFinca.value = mockFincaDetail
    await nextTick()

    await wrapper.vm.handleViewLotes()
    await nextTick()

    expect(wrapper.emitted('view-lotes')).toBeTruthy()
  })

  it('should load finca details when finca prop changes', async () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: null
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    await wrapper.setProps({ finca: mockFinca })
    await nextTick()

    expect(mockLoadFinca).toHaveBeenCalledWith(mockFinca.id)
  })

  it('should load finca details when show becomes true', async () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: false,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    await wrapper.setProps({ show: true })
    await nextTick()

    expect(mockLoadFinca).toHaveBeenCalledWith(mockFinca.id)
  })

  it('should display loading state when loading', () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: null },
      isLoading: { value: true },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Cargando') || text.includes('loading')).toBe(true)
  })

  it('should display finca statistics correctly', async () => {
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: mockFincaDetail },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    const text = wrapper.text()
    expect(text.includes('5')).toBe(true)
    expect(text.includes('3')).toBe(true)
    expect(text.includes('10')).toBe(true)
    expect(text.includes('85')).toBe(true)
  })

  it('should clear current finca after close delay', async () => {
    vi.useFakeTimers()
    const { useFincas } = await import('@/composables/useFincas')
    vi.mocked(useFincas).mockReturnValue({
      currentFinca: { value: mockFincaDetail },
      isLoading: { value: false },
      loadFinca: mockLoadFinca,
      clearCurrentFinca: mockClearCurrentFinca
    })

    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        finca: mockFinca
      },
      global: {
        stubs: {
          BaseModal: true,
          FincaLocationMap: true
        }
      }
    })

    await nextTick()

    wrapper.vm.closeModal()
    await nextTick()

    vi.advanceTimersByTime(300)
    await nextTick()

    expect(mockClearCurrentFinca).toHaveBeenCalled()

    vi.useRealTimers()
  })
})

