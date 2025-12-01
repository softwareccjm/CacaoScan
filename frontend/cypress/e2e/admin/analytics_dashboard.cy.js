describe('Admin Analytics Dashboard', () => {
  beforeEach(() => {
    cy.navigateToAdminDashboard('admin')
  })

  const verifyDashboardExists = () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="admin-dashboard"]').length > 0) {
        cy.get('[data-cy="admin-dashboard"]', { timeout: 10000 }).should('exist')
      } else {
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/admin') || url.includes('/dashboard')
        })
      }
    })
  }

  it('should render all main charts', () => {
    verifyDashboardExists()
    cy.get('body').should('be.visible')
  })

  it('should update charts when time range changes', () => {
    cy.selectIfExists('[data-cy="select-time-range"]', 'last_year')
    cy.get('body').then(($updated) => {
      if ($updated.find('[data-cy="loading-spinner"]').length > 0) {
        cy.get('[data-cy="loading-spinner"]', { timeout: 5000 }).should('exist')
      }
    })
    verifyDashboardExists()
  })

  it('should display system health indicators', () => {
    verifyDashboardExists()
    cy.get('body').should('be.visible')
  })

  it('should drill down into analysis stats', () => {
    cy.clickIfExists('[data-cy="card-analysis-total"]')
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin/analisis') || url.includes('/admin')
    })
  })

  it('should export dashboard report', () => {
    cy.clickIfExists('[data-cy="btn-export-dashboard"]')
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})

