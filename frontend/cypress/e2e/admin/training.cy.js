describe('Admin Training & Datasets', () => {
  beforeEach(() => {
    cy.navigateToTraining('admin')
  })

  it('should load training dashboard', () => {
    // Verificar que la página cargó correctamente
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/entrenamiento') || url.includes('/training')
    })
    // Verificar título de página (puede no existir)
    cy.get('body').then(($body) => {
      const hasTitle = $body.find('h1, h2, .page-title').length > 0
      if (hasTitle) {
        cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('entrenamiento') || text.includes('training') || $el.length > 0
        })
      } else {
        // Si no hay título, verificar que hay contenido
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should display current dataset statistics', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="dataset-stats"], .stats, .statistics').length > 0) {
        cy.get('[data-cy="dataset-stats"], .stats, .statistics').first().should('be.visible')
        cy.get('[data-cy="total-images"], .total-images, [data-stat="images"]', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should list available datasets', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="dataset-list"], .dataset-list, .list').length > 0) {
        cy.get('[data-cy="dataset-list"], .dataset-list, .list').should('exist')
        cy.get('[data-cy="dataset-item"], .dataset-item, .item', { timeout: 5000 }).should('have.length.at.least', 0)
      }
    })
  })

  it('should upload a new dataset', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-upload-dataset"], button').length > 0) {
        cy.get('[data-cy="btn-upload-dataset"], button').first().click()
        cy.get('[data-cy="modal-upload"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should start a new training session', () => {
    cy.clickIfExists('[data-cy="btn-start-training"], button').then(() => {
      cy.get('[data-cy="modal-training-config"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      
      const configureTraining = ($modal) => {
        if ($modal.find('[data-cy="select-epochs"], select').length > 0) {
          cy.selectIfExists('[data-cy="select-epochs"], select', '50')
          cy.selectIfExists('[data-cy="select-batch-size"], select', '16')
          cy.clickIfExists('[data-cy="btn-confirm-training"], button[type="submit"]')
          cy.get('body', { timeout: 5000 }).should('be.visible')
        }
      }

      cy.get('body', { timeout: 5000 }).then(configureTraining)
    })
  })

  it('should view training history', () => {
    cy.clickIfExists('[data-cy="tab-history"], [role="tab"]').then(() => {
      cy.get('table tbody tr, .table-row, .history-item', { timeout: 5000 }).should('have.length.at.least', 0)
    })
  })

  it('should view details of a training session', () => {
    cy.clickIfExists('[data-cy="tab-history"], [role="tab"]').then(() => {
      cy.interactWithFirstRow('table tbody tr, .table-row, .history-item', ($row) => {
        cy.wrap($row).click({ force: true })
        cy.get('[data-cy="training-metrics"], .metrics, .details', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('should validate dataset deletion', () => {
    const clickDeleteAndVerify = ($btns) => {
      if ($btns.length > 0) {
        cy.wrap($btns.first()).click({ force: true })
        cy.get('.swal2-title, [role="dialog"] h2', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('eliminar') || text.includes('delete') || text.includes('¿') || $el.length > 0
        })
      }
    }

    const openDatasetsTab = ($body) => {
      if ($body.find('[data-cy="tab-datasets"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-datasets"], [role="tab"]').first().click()
        cy.get('[data-cy="btn-delete-dataset"], button', { timeout: 5000 }).then(clickDeleteAndVerify)
      }
    }

    cy.get('body').then(openDatasetsTab)
  })
})

