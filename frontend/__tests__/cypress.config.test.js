import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

describe('cypress.config.js', () => {
  let originalEnv
  let config

  beforeEach(() => {
    // Save original environment variables
    originalEnv = {
      CI: process.env.CI,
      CYPRESS_CI: process.env.CYPRESS_CI,
      CYPRESS_BASE_URL: process.env.CYPRESS_BASE_URL
    }

    // Clear module cache to re-import with different env vars
    vi.resetModules()
  })

  afterEach(() => {
    // Restore original environment variables
    Object.keys(originalEnv).forEach((key) => {
      if (originalEnv[key] === undefined) {
        delete process.env[key]
      } else {
        process.env[key] = originalEnv[key]
      }
    })

    vi.resetModules()
  })

  describe('config export', () => {
    it('should export a default configuration object', async () => {
      const configModule = await import('../cypress.config.js')
      expect(configModule.default).toBeDefined()
      expect(typeof configModule.default).toBe('object')
    })

    it('should have e2e configuration', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e).toBeDefined()
      expect(typeof config.e2e).toBe('object')
    })

    it('should have component configuration', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.component).toBeDefined()
      expect(typeof config.component).toBe('object')
    })
  })

  describe('e2e configuration', () => {
    it('should have correct specPattern', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.specPattern).toBe('cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}')
    })

    it('should use default baseUrl when CYPRESS_BASE_URL is not set', async () => {
      delete process.env.CYPRESS_BASE_URL
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.baseUrl).toBe('http://localhost:5173')
    })

    it('should use CYPRESS_BASE_URL when set', async () => {
      process.env.CYPRESS_BASE_URL = 'http://test.example.com:3000'
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.baseUrl).toBe('http://test.example.com:3000')
    })

    it('should have trashAssetsBeforeRuns set to false', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.trashAssetsBeforeRuns).toBe(false)
    })

    it('should have correct timeout values', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.defaultCommandTimeout).toBe(10000)
      expect(config.e2e.requestTimeout).toBe(10000)
      expect(config.e2e.responseTimeout).toBe(10000)
      expect(config.e2e.pageLoadTimeout).toBe(30000)
    })
  })

  describe('CI detection', () => {
    it('should disable video when CI is true', async () => {
      process.env.CI = 'true'
      delete process.env.CYPRESS_CI
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.video).toBe(false)
    })

    it('should disable video when CYPRESS_CI is true', async () => {
      delete process.env.CI
      process.env.CYPRESS_CI = 'true'
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.video).toBe(false)
    })

    it('should enable video when CI is not set', async () => {
      delete process.env.CI
      delete process.env.CYPRESS_CI
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.video).toBe(true)
    })

    it('should enable video when CI is false', async () => {
      process.env.CI = 'false'
      delete process.env.CYPRESS_CI
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.video).toBe(true)
    })

    it('should disable screenshotOnRunFailure when CI is true', async () => {
      process.env.CI = 'true'
      delete process.env.CYPRESS_CI
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.screenshotOnRunFailure).toBe(false)
    })

    it('should disable screenshotOnRunFailure when CYPRESS_CI is true', async () => {
      delete process.env.CI
      process.env.CYPRESS_CI = 'true'
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.screenshotOnRunFailure).toBe(false)
    })

    it('should enable screenshotOnRunFailure when CI is not set', async () => {
      delete process.env.CI
      delete process.env.CYPRESS_CI
      vi.resetModules()
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.e2e.screenshotOnRunFailure).toBe(true)
    })
  })

  describe('component configuration', () => {
    it('should have correct specPattern', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.component.specPattern).toBe('src/**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}')
    })

    it('should have devServer configuration', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.component.devServer).toBeDefined()
      expect(typeof config.component.devServer).toBe('object')
    })

    it('should have framework set to vue', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.component.devServer.framework).toBe('vue')
    })

    it('should have bundler set to vite', async () => {
      const configModule = await import('../cypress.config.js')
      config = configModule.default
      expect(config.component.devServer.bundler).toBe('vite')
    })
  })
})

