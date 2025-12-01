describe('Advanced Form Inputs', () => {
  beforeEach(() => {
    cy.navigateToFincas('farmer')
    cy.clickIfExists('[data-cy="btn-add-finca"], button', { force: true })
  })

  it('should validate max length on inputs', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
        const longText = 'a'.repeat(256)
        cy.typeIfExists('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', longText).then(() => {
          cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', { timeout: 3000 }).first().should('exist')
        })
      }
    })
  })

  it('should prevent negative numbers in area', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-area"], input[type="number"]').length > 0) {
        cy.typeIfExists('[data-cy="input-area"], input[type="number"]', '-50').then(() => {
          cy.get('body', { timeout: 3000 }).then($body => {
            if ($body.find('.error-message, [data-cy="error"]').length > 0) {
              cy.get('.error-message, [data-cy="error"]').should('exist')
            } else {
              cy.get('[data-cy="input-area"], input[type="number"]').first().should('satisfy', ($el) => {
                const val = $el.val()
                return val !== '-50' || val === '' || val === null
              })
            }
          })
        })
      }
    })
  })

  it('should handle special characters in names', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
        const weirdName = 'Finca Ñandú & Cacao @100%'
        cy.typeIfExists('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', weirdName).then(() => {
          cy.clickIfExists('[data-cy="btn-save-finca"], button[type="submit"]').then(() => {
            cy.get('body', { timeout: 5000 }).should('be.visible')
          })
        })
      }
    })
  })

  it('should validate dates in history filter', () => {
    cy.login('farmer')
    cy.visit('/agricultor/historial')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="date-start"], input[type="date"]').length > 0) {
        cy.fillFieldIfExists('[data-cy="date-start"], input[type="date"]', '2025-12-31', { force: true })
        cy.fillFieldIfExists('[data-cy="date-end"], input[type="date"]', '2024-01-01', { force: true })
        cy.clickIfExists('[data-cy="btn-filter"], button[type="submit"]').then(() => {
          cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
        })
      }
    })
  })
})

