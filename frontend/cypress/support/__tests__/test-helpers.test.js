import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock Cypress and cy
const mockIntercept = vi.fn()
const mockGet = vi.fn()
const mockCypress = {
  env: vi.fn()
}

// Set up global mocks before importing
global.Cypress = mockCypress
global.cy = {
  intercept: mockIntercept,
  get: mockGet
}

import {
  getApiBaseUrl,
  interceptApi,
  shouldIncludeRoute,
  shouldContainText,
  waitForElement,
  shouldShowError,
  conditionalClick,
  conditionalShould
} from '../test-helpers'

describe('test-helpers.js', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.Cypress = mockCypress
    global.cy = {
      intercept: mockIntercept,
      get: mockGet
    }
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('getApiBaseUrl', () => {
    it('should return default URL when Cypress.env is not set', () => {
      mockCypress.env.mockReturnValue(undefined)
      const url = getApiBaseUrl()
      expect(url).toBe('http://localhost:8000/api/v1')
    })

    it('should return URL from Cypress.env when API_BASE_URL is set', () => {
      mockCypress.env.mockImplementation((key) => {
        if (key === 'API_BASE_URL') return 'https://api.example.com/api/v1'
        return undefined
      })
      const url = getApiBaseUrl()
      expect(url).toBe('https://api.example.com/api/v1')
    })

    it('should call Cypress.env with correct key', () => {
      mockCypress.env.mockReturnValue(undefined)
      getApiBaseUrl()
      expect(mockCypress.env).toHaveBeenCalledWith('API_BASE_URL')
    })
  })

  describe('interceptApi', () => {
    beforeEach(() => {
      mockIntercept.mockReturnValue({})
      mockCypress.env.mockReturnValue('http://localhost:8000/api/v1')
    })

    it('should intercept API call with full URL when endpoint is relative', () => {
      interceptApi('GET', '/lotes', { data: [] })
      
      expect(mockIntercept).toHaveBeenCalledWith(
        'GET',
        'http://localhost:8000/api/v1/lotes',
        { statusCode: 200, body: { data: [] } }
      )
    })

    it('should intercept API call with endpoint without leading slash', () => {
      interceptApi('POST', 'lotes', { id: 1 })
      
      expect(mockIntercept).toHaveBeenCalledWith(
        'POST',
        'http://localhost:8000/api/v1/lotes',
        { statusCode: 200, body: { id: 1 } }
      )
    })

    it('should intercept API call with absolute URL directly', () => {
      interceptApi('GET', 'http://example.com/api/lotes', { data: [] })
      
      expect(mockIntercept).toHaveBeenCalledWith(
        'GET',
        'http://example.com/api/lotes',
        { statusCode: 200, body: { data: [] } }
      )
    })

    it('should use custom status code when provided', () => {
      interceptApi('GET', '/lotes', { error: 'Not found' }, 404)
      
      expect(mockIntercept).toHaveBeenCalledWith(
        'GET',
        'http://localhost:8000/api/v1/lotes',
        { statusCode: 404, body: { error: 'Not found' } }
      )
    })

    it('should handle different HTTP methods', () => {
      interceptApi('POST', '/lotes', {})
      expect(mockIntercept).toHaveBeenCalledWith(
        'POST',
        expect.stringContaining('/lotes'),
        expect.any(Object)
      )
      
      interceptApi('PUT', '/lotes/1', {})
      expect(mockIntercept).toHaveBeenCalledWith(
        'PUT',
        expect.stringContaining('/lotes/1'),
        expect.any(Object)
      )
      
      interceptApi('DELETE', '/lotes/1', {})
      expect(mockIntercept).toHaveBeenCalledWith(
        'DELETE',
        expect.stringContaining('/lotes/1'),
        expect.any(Object)
      )
    })
  })

  describe('shouldIncludeRoute', () => {
    it('should return true when URL includes single expected route', () => {
      const result = shouldIncludeRoute('/fincas/1/lotes', '/fincas')
      expect(result).toBe(true)
    })

    it('should return false when URL does not include expected route', () => {
      const result = shouldIncludeRoute('/fincas/1/lotes', '/users')
      expect(result).toBe(false)
    })

    it('should return true when URL includes any of the expected routes', () => {
      const result = shouldIncludeRoute('/fincas/1/lotes', ['/users', '/fincas', '/lotes'])
      expect(result).toBe(true)
    })

    it('should return false when URL does not include any expected routes', () => {
      const result = shouldIncludeRoute('/fincas/1/lotes', ['/users', '/admin', '/dashboard'])
      expect(result).toBe(false)
    })

    it('should handle single route as string', () => {
      const result = shouldIncludeRoute('http://example.com/fincas', 'fincas')
      expect(result).toBe(true)
    })

    it('should handle empty routes array', () => {
      const result = shouldIncludeRoute('/fincas/1/lotes', [])
      expect(result).toBe(false)
    })
  })

  describe('shouldContainText', () => {
    it('should return true when element contains single expected text', () => {
      const mockElement = {
        text: vi.fn(() => 'This is a test message')
      }
      const result = shouldContainText(mockElement, 'test')
      expect(result).toBe(true)
    })

    it('should return false when element does not contain expected text', () => {
      const mockElement = {
        text: vi.fn(() => 'This is a test message')
      }
      const result = shouldContainText(mockElement, 'notfound')
      expect(result).toBe(false)
    })

    it('should return true when element contains any of expected texts', () => {
      const mockElement = {
        text: vi.fn(() => 'This is a test message')
      }
      const result = shouldContainText(mockElement, ['notfound', 'test', 'other'])
      expect(result).toBe(true)
    })

    it('should be case insensitive', () => {
      const mockElement = {
        text: vi.fn(() => 'This is a TEST message')
      }
      const result = shouldContainText(mockElement, 'test')
      expect(result).toBe(true)
    })

    it('should handle empty texts array', () => {
      const mockElement = {
        text: vi.fn(() => 'This is a test message')
      }
      const result = shouldContainText(mockElement, [])
      expect(result).toBe(false)
    })
  })

  describe('waitForElement', () => {
    it('should call cy.get with default timeout', () => {
      const mockChain = {
        should: vi.fn().mockReturnThis()
      }
      mockGet.mockReturnValue(mockChain)
      
      waitForElement('.test-selector')
      
      expect(mockGet).toHaveBeenCalledWith('.test-selector', { timeout: 10000 })
      expect(mockChain.should).toHaveBeenCalledWith('be.visible')
    })

    it('should use custom timeout when provided', () => {
      const mockChain = {
        should: vi.fn().mockReturnThis()
      }
      mockGet.mockReturnValue(mockChain)
      
      waitForElement('.test-selector', { timeout: 5000 })
      
      expect(mockGet).toHaveBeenCalledWith('.test-selector', { timeout: 5000 })
    })
  })

  describe('shouldShowError', () => {
    it('should check for error message elements', () => {
      const mockBody = {
        text: vi.fn(() => 'Some content'),
        find: vi.fn(() => ({
          length: 1
        }))
      }
      
      mockGet.mockReturnValue({
        should: vi.fn((assertion, callback) => {
          if (typeof callback === 'function') {
            const result = callback(mockBody)
            expect(result).toBe(true)
          }
          return {}
        })
      })
      
      shouldShowError()
      
      expect(mockGet).toHaveBeenCalledWith('body', { timeout: 5000 })
    })

    it('should detect error in text content', () => {
      const mockBody = {
        text: vi.fn(() => 'Error occurred during operation'),
        find: vi.fn(() => ({
          length: 0
        }))
      }
      
      mockGet.mockReturnValue({
        should: vi.fn((assertion, callback) => {
          if (typeof callback === 'function') {
            const result = callback(mockBody)
            expect(result).toBe(true)
          }
          return {}
        })
      })
      
      shouldShowError()
    })

    it('should detect Spanish error words', () => {
      const mockBody = {
        text: vi.fn(() => 'Datos inválidos'),
        find: vi.fn(() => ({
          length: 0
        }))
      }
      
      mockGet.mockReturnValue({
        should: vi.fn((assertion, callback) => {
          if (typeof callback === 'function') {
            const result = callback(mockBody)
            expect(result).toBe(true)
          }
          return {}
        })
      })
      
      shouldShowError()
    })
  })

  describe('conditionalClick', () => {
    it('should click element when it exists', () => {
      const mockElement = {
        click: vi.fn()
      }
      const mockBody = {
        find: vi.fn(() => ({
          length: 1
        }))
      }
      
      mockGet.mockImplementation((selector) => {
        if (selector === 'body') {
          return {
            then: vi.fn((callback) => {
              callback(mockBody)
              return {
                then: vi.fn((callback) => {
                  callback(mockElement)
                })
              }
            })
          }
        }
        return {
          first: vi.fn(() => ({
            click: vi.fn()
          }))
        }
      })
      
      conditionalClick('.test-button')
      
      expect(mockBody.find).toHaveBeenCalledWith('.test-button')
    })

    it('should not click when element does not exist', () => {
      const mockBody = {
        find: vi.fn(() => ({
          length: 0
        }))
      }
      
      mockGet.mockReturnValue({
        then: vi.fn((callback) => {
          callback(mockBody)
        })
      })
      
      conditionalClick('.non-existent')
      
      expect(mockBody.find).toHaveBeenCalledWith('.non-existent')
    })

    it('should pass options to click method', () => {
      const mockClick = vi.fn()
      const mockBody = {
        find: vi.fn(() => ({
          length: 1
        }))
      }
      
      mockGet.mockImplementation((selector) => {
        if (selector === 'body') {
          return {
            then: vi.fn((callback) => {
              callback(mockBody)
              return {
                then: vi.fn((callback) => {
                  callback({ click: mockClick })
                })
              }
            })
          }
        }
        return {
          first: vi.fn(() => ({
            click: mockClick
          }))
        }
      })
      
      conditionalClick('.test-button', { force: true })
      
      expect(mockClick).toHaveBeenCalledWith({ force: true })
    })
  })

  describe('conditionalShould', () => {
    it('should assert when element exists', () => {
      const mockChain = {
        should: vi.fn().mockReturnThis()
      }
      const mockBody = {
        find: vi.fn(() => ({
          length: 1
        }))
      }
      
      mockGet.mockImplementation((selector, options) => {
        if (selector === 'body') {
          return {
            then: vi.fn((callback) => {
              callback(mockBody)
            })
          }
        }
        return mockChain
      })
      
      conditionalShould('.test-element', 'be.visible')
      
      expect(mockBody.find).toHaveBeenCalledWith('.test-element')
      expect(mockGet).toHaveBeenCalledWith('.test-element', { timeout: 5000 })
      expect(mockChain.should).toHaveBeenCalledWith('be.visible')
    })

    it('should not assert when element does not exist', () => {
      const mockBody = {
        find: vi.fn(() => ({
          length: 0
        }))
      }
      
      mockGet.mockReturnValue({
        then: vi.fn((callback) => {
          callback(mockBody)
        })
      })
      
      conditionalShould('.non-existent', 'be.visible')
      
      expect(mockBody.find).toHaveBeenCalledWith('.non-existent')
    })

    it('should use custom timeout when provided', () => {
      const mockChain = {
        should: vi.fn().mockReturnThis()
      }
      const mockBody = {
        find: vi.fn(() => ({
          length: 1
        }))
      }
      
      mockGet.mockImplementation((selector, options) => {
        if (selector === 'body') {
          return {
            then: vi.fn((callback) => {
              callback(mockBody)
            })
          }
        }
        return mockChain
      })
      
      conditionalShould('.test-element', 'be.visible', { timeout: 10000 })
      
      expect(mockGet).toHaveBeenCalledWith('.test-element', { timeout: 10000 })
    })
  })
})

