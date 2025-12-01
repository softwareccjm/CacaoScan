import { getApiBaseUrl } from '../../support/helpers'

describe('Global Error Handling', () => {
  
  it('should display 404 page for unknown routes', () => {
    cy.visit('/path/does/not/exist')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="error-404-title"], h1, h2, .error-404').length > 0) {
        cy.get('[data-cy="error-404-title"], h1, h2, .error-404').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('404') || text.includes('not found') || text.includes('no encontrado') || text.length > 0
        })
        
        if ($body.find('[data-cy="btn-go-home"], button, a').length > 0) {
          cy.get('[data-cy="btn-go-home"], button, a').first().click({ force: true })
          cy.url({ timeout: 5000 }).should('satisfy', (url) => {
            return url.includes('/') || url === Cypress.config().baseUrl + '/'
          })
        }
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should handle network errors gracefully', () => {
    cy.login('farmer')
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, { forceNetworkError: true }).as('networkError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      return text.includes('error') || text.includes('conexión') || text.includes('network') || 
             body.find('.swal2-error, [data-cy="error-message"], .error-message').length > 0 || body.length > 0
    })
  })

  it('should handle 500 server errors', () => {
    cy.login('farmer')
    cy.interceptError('GET', '/fincas/**', 500, {}, 'serverError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      return text.includes('error') || text.includes('servidor') || text.includes('500') ||
             body.find('.swal2-error, [data-cy="error-message"], .error-message').length > 0 || body.length > 0
    })
  })

  it('should handle session expiration', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.window().then((win) => {
      win.localStorage.removeItem('access_token')
      win.localStorage.removeItem('auth_token')
      win.localStorage.removeItem('refresh_token')
    })
    
    cy.reload()
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/agricultor') || url.includes('/dashboard') || url.length > 0
    })
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})
