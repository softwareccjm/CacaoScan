import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VerifyPrompt from '../VerifyPrompt.vue'

describe('VerifyPrompt', () => {
  it('should render verify prompt', () => {
    const wrapper = mount(VerifyPrompt, {
      global: {
        stubs: { 'router-link': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})

