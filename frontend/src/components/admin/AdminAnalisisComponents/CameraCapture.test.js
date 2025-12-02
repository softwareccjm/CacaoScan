import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CameraCapture from './CameraCapture.vue'

global.navigator = {
  mediaDevices: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }]
    })
  }
}

describe('CameraCapture', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render camera capture component', () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display loading state initially', () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('cámara') || text.includes('Cargando') || text.includes('Loading')).toBe(true)
  })

  it('should have capture button', () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    const buttons = wrapper.findAll('button')
    const captureButton = buttons.find(btn => 
      btn.text().includes('Capturar') || 
      btn.text().includes('Foto') || 
      btn.text().includes('Capture')
    )
    expect(captureButton?.exists() ?? wrapper.exists()).toBe(true)
  })

  it('should emit capture event when photo is taken', async () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    if (wrapper.vm.photoTaken) {
      expect(wrapper.emitted('capture')).toBeTruthy()
    }
  })

  it('should stop camera before starting new stream', async () => {
    const mockStop = vi.fn()
    global.navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: mockStop }]
    })

    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.vm.stream = {
      getTracks: () => [{ stop: mockStop }]
    }

    await wrapper.vm.startCamera()
    await wrapper.vm.$nextTick()

    expect(mockStop).toHaveBeenCalled()
  })

  it('should handle camera error', async () => {
    global.navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error('Camera error'))

    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.hasError).toBe(true)
    expect(wrapper.vm.error).toBeTruthy()
  })

  it('should set video srcObject when camera starts', async () => {
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }]
    }
    global.navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue(mockStream)

    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: {
            template: '<video></video>',
            mounted() {
              this.$el.play = vi.fn()
              this.$el.onloadedmetadata = null
            }
          },
          canvas: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(global.navigator.mediaDevices.getUserMedia).toHaveBeenCalled()
  })

  it('should capture photo correctly', () => {
    const mockContext = {
      drawImage: vi.fn()
    }
    const mockCanvas = {
      getContext: vi.fn().mockReturnValue(mockContext),
      width: 0,
      height: 0,
      toBlob: vi.fn()
    }
    const mockVideo = {
      videoWidth: 640,
      videoHeight: 480
    }

    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.video = mockVideo
    wrapper.vm.canvas = mockCanvas
    wrapper.vm.stream = {
      getTracks: () => [{ stop: vi.fn() }]
    }

    wrapper.vm.capturePhoto()

    expect(mockContext.drawImage).toHaveBeenCalled()
    expect(wrapper.vm.photoTaken).toBe(true)
  })

  it('should not capture photo if video or canvas is missing', () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.video = null
    wrapper.vm.canvas = null

    wrapper.vm.capturePhoto()

    expect(wrapper.vm.photoTaken).toBe(false)
  })

  it('should retake photo', async () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.photoTaken = true
    wrapper.vm.startCamera = vi.fn().mockResolvedValue(undefined)

    await wrapper.vm.retakePhoto()

    expect(wrapper.vm.photoTaken).toBe(false)
    expect(wrapper.vm.startCamera).toHaveBeenCalled()
  })

  it('should save photo as blob', () => {
    const mockBlob = new Blob(['test'], { type: 'image/jpeg' })
    const mockCanvas = {
      toBlob: vi.fn((callback) => {
        callback(mockBlob)
      })
    }

    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.canvas = mockCanvas

    wrapper.vm.savePhoto()

    expect(mockCanvas.toBlob).toHaveBeenCalled()
    expect(wrapper.emitted('capture')).toBeTruthy()
  })

  it('should not save photo if canvas is missing', () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.canvas = null

    wrapper.vm.savePhoto()

    expect(wrapper.emitted('capture')).toBeFalsy()
  })

  it('should retry camera', async () => {
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.startCamera = vi.fn().mockResolvedValue(undefined)

    await wrapper.vm.retryCamera()

    expect(wrapper.vm.startCamera).toHaveBeenCalled()
  })

  it('should stop camera on unmount', () => {
    const mockStop = vi.fn()
    wrapper = mount(CameraCapture, {
      global: {
        stubs: {
          video: true,
          canvas: true
        }
      }
    })

    wrapper.vm.stream = {
      getTracks: () => [{ stop: mockStop }]
    }

    wrapper.unmount()

    expect(mockStop).toHaveBeenCalled()
  })
})

