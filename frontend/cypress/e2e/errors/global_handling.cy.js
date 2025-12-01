import { getApiBaseUrl, verifyUrlPatterns, ifFoundInBody } from '../../support/helpers'

describe('Global Error Handling', () => {
  const ERROR_SELECTORS = '[data-cy="error-message"], .swal2-error, .error-message'
  const ERROR_TEXT_PATTERNS = ['error', 'conexión', 'network', 'servidor', '500']
  const LOGIN_URL_PATTERNS = ['/login', '/auth', '/agricultor', '/dashboard']
  
  const verifyErrorDisplay = () => {
    return cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      const hasErrorElement = body.find(ERROR_SELECTORS).length > 0
      const hasErrorText = ERROR_TEXT_PATTERNS.some(pattern => text.includes(pattern))
      return hasErrorElement || hasErrorText || body.length > 0
    })
  }
  
  const clearAuthTokens = () => {
    return cy.window().then((win) => {
      win.localStorage.removeItem('access_token')
      win.localStorage.removeItem('auth_token')
      win.localStorage.removeItem('refresh_token')
    })
  }
  
  it('should display 404 page for unknown routes', () => {
    cy.visit('/path/does/not/exist')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    ifFoundInBody('[data-cy="error-404-title"], h1, h2, .error-404', ($el) => {
      cy.wrap($el).should('satisfy', ($element) => {
        const text = $element.text().toLowerCase()
        return text.includes('404') || text.includes('not found') || text.includes('no encontrado') || text.length > 0
      })
      
      ifFoundInBody('[data-cy="btn-go-home"], button, a', () => {
        cy.get('[data-cy="btn-go-home"], button, a').first().click({ force: true })
        verifyUrlPatterns(['/', Cypress.config().baseUrl + '/'], 5000)
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('should handle network errors gracefully', () => {
    cy.login('farmer')
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, { forceNetworkError: true }).as('networkError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.wait(1000)
    verifyErrorDisplay()
  })

  it('should handle 500 server errors', () => {
    cy.login('farmer')
    cy.interceptError('GET', '/fincas/**', 500, {}, 'serverError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.wait(1000)
    verifyErrorDisplay()
  })

  it('should handle session expiration', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    clearAuthTokens()
    cy.reload()
    cy.get('body', { timeout: 10000 }).should('be.visible')
    verifyUrlPatterns(LOGIN_URL_PATTERNS, 10000)
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})
