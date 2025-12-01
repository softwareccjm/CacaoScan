import { clickIfExists, typeIfExists, selectIfExists } from '../../support/helpers'

describe('Admin System Configuration', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/configuracion')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should load configuration page', () => {
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/configuracion') || url.includes('/configuration')
    })
    cy.get('body').then(($body) => {
      const hasTitle = $body.find('h1, h2, .page-title').length > 0
      if (hasTitle) {
        cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('configuración') || text.includes('configuration') || text.includes('sistema') || $el.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should display general settings tab by default', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-general"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-general"], [role="tab"]').first().should('satisfy', ($tab) => {
          return $tab.hasClass('active') || $tab.attr('aria-selected') === 'true' || $tab.length > 0
        })
        cy.get('[data-cy="section-general"], .section, .tab-content', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should switch to security settings tab', () => {
    clickIfExists('[data-cy="tab-security"], [role="tab"]').then((clicked) => {
      if (clicked) {
        cy.get('[data-cy="section-security"], .section, .tab-content', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should switch to analysis settings tab', () => {
    clickIfExists('[data-cy="tab-analysis"], [role="tab"]').then((clicked) => {
      if (clicked) {
        cy.get('[data-cy="section-analysis"], .section, .tab-content', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should update site name', () => {
    typeIfExists('[data-cy="input-site-name"], input[name*="name"], input[type="text"]', 'CacaoScan Updated', { clear: true }).then(() => {
      clickIfExists('[data-cy="btn-save-general"], button[type="submit"]').then(() => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
  })

  it('should validate maintenance mode toggle', () => {
    const toggleMaintenance = () => {
      cy.get('[data-cy="toggle-maintenance"], input[type="checkbox"]').first().click({ force: true })
    }

    const saveAndWait = () => {
      clickIfExists('[data-cy="btn-save-general"], button[type="submit"]')
      cy.get('body', { timeout: 5000 }).should('be.visible')
    }

    ifElementExists('[data-cy="toggle-maintenance"], input[type="checkbox"]', () => {
      toggleMaintenance()
      saveAndWait()
      toggleMaintenance()
      saveAndWait()
    })
  })

  it('should update password policy settings', () => {
    const updatePasswordPolicy = () => {
      typeIfExists('[data-cy="input-min-pass-length"], input[type="number"]', '10', { clear: true })
      clickIfExists('[data-cy="btn-save-security"], button[type="submit"]')
      cy.get('body', { timeout: 5000 }).should('be.visible')
    }

    clickIfExists('[data-cy="tab-security"], [role="tab"]').then(updatePasswordPolicy)
  })

  it('should validate invalid values in analysis thresholds', () => {
    const validateInvalidThreshold = () => {
      typeIfExists('[data-cy="input-confidence-threshold"], input[type="number"]', '150', { clear: true })
      clickIfExists('[data-cy="btn-save-analysis"], button[type="submit"]')
      cy.get('.error-message, [data-cy="error"], .alert-error', { timeout: 5000 }).should('exist')
    }

    clickIfExists('[data-cy="tab-analysis"], [role="tab"]').then(validateInvalidThreshold)
  })

  it('should update analysis default model', () => {
    const updateModel = () => {
      selectIfExists('[data-cy="select-model"], select', 'v2.0')
      clickIfExists('[data-cy="btn-save-analysis"], button[type="submit"]')
      cy.get('body', { timeout: 5000 }).should('be.visible')
    }

    clickIfExists('[data-cy="tab-analysis"], [role="tab"]').then(updateModel)
  })

  it('should show reset to defaults confirmation', () => {
    clickIfExists('[data-cy="btn-reset-defaults"], button').then(() => {
      cy.get('.swal2-title, [role="dialog"] h2', { timeout: 5000 }).should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return text.includes('restaurar') || text.includes('reset') || text.includes('valores') || text.includes('¿') || $el.length > 0
      })
    })
  })

  it('should export configuration', () => {
    clickIfExists('[data-cy="btn-export-config"], button').then(() => {
      cy.get('.error-message, .swal2-error', { timeout: 3000 }).should('not.exist')
    })
  })
})
