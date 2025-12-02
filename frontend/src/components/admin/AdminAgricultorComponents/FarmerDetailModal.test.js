import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FarmerDetailModal from './FarmerDetailModal.vue'

const mockGetUser = vi.fn()
const mockGetFincas = vi.fn()

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show"><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

vi.mock('@/services/authApi', () => ({
  default: {
    getUser: mockGetUser
  }
}))

vi.mock('@/services/fincasApi', () => ({
  getFincas: mockGetFincas
}))

describe('FarmerDetailModal', () => {
  const mockFarmer = {
    id: 1,
    name: 'John Doe',
    email: 'john@test.com',
    initials: 'JD',
    status: 'Activo',
    fincas: []
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetUser.mockResolvedValue({ persona: { id: 1 } })
    mockGetFincas.mockResolvedValue({ results: [] })
  })

  it('should render modal', () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: mockFarmer
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should open modal', async () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: mockFarmer
      }
    })

    await wrapper.vm.openModal()
    expect(wrapper.vm.isOpen).toBe(true)
  })

  it('should close modal and emit close event', async () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: mockFarmer
      }
    })

    await wrapper.vm.openModal()
    await wrapper.vm.closeModal()

    expect(wrapper.vm.isOpen).toBe(false)
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should calculate total area correctly', async () => {
    const fincas = [
      { id: 1, hectareas: '10.5' },
      { id: 2, hectareas: '20.3' }
    ]
    mockGetFincas.mockResolvedValue({ results: fincas })

    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadFarmersFincas(1)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.totalArea).toBe('30.8')
  })

  it('should return 0.0 for total area when no fincas', async () => {
    mockGetFincas.mockResolvedValue({ results: [] })

    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadFarmersFincas(1)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.totalArea).toBe('0.0')
  })

  it('should return 0 for totalAnalisis', () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: mockFarmer
      }
    })

    expect(wrapper.vm.totalAnalisis).toBe(0)
  })

  it('should return correct status classes', () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: mockFarmer
      }
    })

    expect(wrapper.vm.getStatusClasses('Activo')).toBe('bg-green-100 text-green-800')
    expect(wrapper.vm.getStatusClasses('Inactivo')).toBe('bg-red-100 text-red-800')
    expect(wrapper.vm.getStatusClasses('Unknown')).toBe('bg-gray-100 text-gray-800')
  })

  it('should load farmer details when farmer prop changes', async () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ farmer: { ...mockFarmer, id: 2 } })
    await wrapper.vm.$nextTick()

    expect(mockGetFincas).toHaveBeenCalled()
    expect(mockGetUser).toHaveBeenCalled()
  })

  it('should handle error when loading fincas', async () => {
    mockGetFincas.mockRejectedValue(new Error('Network error'))

    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadFarmersFincas(1)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.fincasList).toEqual([])
  })

  it('should handle error when loading farmer details', async () => {
    mockGetUser.mockRejectedValue(new Error('Network error'))

    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: 1 }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadFarmerDetails(1)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.persona).toBeNull()
  })

  it('should not load details when farmer has no id', async () => {
    const wrapper = mount(FarmerDetailModal, {
      props: {
        farmer: { ...mockFarmer, id: null }
      }
    })

    await wrapper.vm.$nextTick()
    await wrapper.setProps({ farmer: { ...mockFarmer, id: null } })
    await wrapper.vm.$nextTick()

    expect(mockGetFincas).not.toHaveBeenCalled()
    expect(mockGetUser).not.toHaveBeenCalled()
  })
})

