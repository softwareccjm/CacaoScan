import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GlobalLoader from '../GlobalLoader.vue'

describe('GlobalLoader', () => {
  let wrapper

  const mountComponent = () => {
    return mount(GlobalLoader)
  }

  const triggerLoading = async (title, message) => {
    globalThis.showGlobalLoading(title, message)
    await wrapper.vm.$nextTick()
  }

  beforeEach(() => {
    vi.useFakeTimers()
    globalThis.addEventListener = vi.fn()
    globalThis.removeEventListener = vi.fn()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('should render when isLoading is true', async () => {
    wrapper = mountComponent()
    await triggerLoading('Test', 'Message')
    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should not render when isLoading is false', () => {
    wrapper = mountComponent()
    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should display loading text and message', async () => {
    wrapper = mountComponent()
    await triggerLoading('Loading...', 'Please wait')
    const text = wrapper.text()
    expect(text).toContain('Loading...')
    expect(text).toContain('Please wait')
  })

  it('should show progress bar', async () => {
    wrapper = mountComponent()
    await triggerLoading()
    expect(wrapper.find('.bg-gray-200').exists()).toBe(true)
  })

  const testEventListening = (eventName) => {
    it(`should listen to ${eventName} event`, () => {
      wrapper = mountComponent()
      expect(globalThis.addEventListener).toHaveBeenCalledWith(eventName, expect.any(Function))
    })
  }

  testEventListening('route-loading-start')
  testEventListening('route-loading-end')
  testEventListening('api-loading-start')
  testEventListening('api-loading-end')

  it('should clean up event listeners on unmount', () => {
    wrapper = mountComponent()
    wrapper.unmount()
    expect(globalThis.removeEventListener).toHaveBeenCalled()
  })
})


