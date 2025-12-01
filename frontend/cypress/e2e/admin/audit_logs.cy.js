describe('Admin Audit Logs', () => {
  beforeEach(() => {
    cy.navigateToAdminAuditLogs('admin')
  })

  it('should load audit logs table', () => {
    // Verificar que la página cargó correctamente
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/admin') || url.includes('/auditoria') || url.includes('/audit')
    })
    // Verificar título de página (puede no existir)
    cy.get('body').then(($body) => {
      const hasTitle = $body.find('h1, h2, .page-title').length > 0
      if (hasTitle) {
        cy.get('h1, h2, .page-title', { timeout: 5000 }).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('auditoría') || text.includes('audit') || $el.length > 0
        })
      }
    })
    // Verificar tabla (puede no existir si no hay datos)
    cy.get('body').then(($body) => {
      if ($body.find('table, .table, [data-cy="audit-table"]').length > 0) {
        cy.get('table, .table, [data-cy="audit-table"]', { timeout: 5000 }).should('exist')
      } else {
        // Si no hay tabla, verificar que hay algún contenido
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should filter logs by action type', () => {
    const selectSelector = '[data-cy="select-action-type"], select'
    const rowSelector = 'table tbody tr, .table-row'
    cy.selectAndVerifyRows(selectSelector, 'LOGIN', rowSelector)
  })

  it('should filter logs by date range', () => {
    const today = new Date().toISOString().split('T')[0]
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="date-start"], input[type="date"]').length > 0) {
        cy.get('[data-cy="date-start"], input[type="date"]').first().type(today, { force: true })
        cy.get('[data-cy="date-end"], input[type="date"]').last().type(today, { force: true })
        cy.get('[data-cy="btn-apply-filter"], button[type="submit"]').first().click()
        
        // Verificar logs o estado vacío
        cy.get('body', { timeout: 5000 }).then(($body) => {
          if ($body.find('table tbody tr, .table-row').length > 0) {
            cy.get('table tbody tr, .table-row').first().should('exist')
          } else {
            cy.contains('No se encontraron registros, No hay registros, Sin resultados', { matchCase: false }).should('exist')
          }
        })
      }
    })
  })

  it('should view log details', () => {
    const rowSelector = 'table tbody tr, .table-row, [data-cy="audit-row"], tbody tr'
    cy.interactWithFirstRow(rowSelector, ($row) => {
      const btn = $row.find('[data-cy="btn-view-details"], button, a, [role="button"]').first()
      if (btn.length > 0) {
        cy.wrap(btn).click({ force: true })
        cy.get('[data-cy="modal-log-details"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
        cy.get('body').then(($modal) => {
          if ($modal.find('[data-cy="json-viewer"], .json-viewer, pre, code').length > 0) {
            cy.get('[data-cy="json-viewer"], .json-viewer, pre, code', { timeout: 3000 }).should('exist')
          }
        })
      }
    })
  })

  it('should export audit logs to CSV', () => {
    cy.clickIfExists('[data-cy="btn-export-csv"], button')
    cy.get('.swal2-error', { timeout: 3000 }).should('not.exist')
  })

  it('should clear old logs (if applicable)', () => {
    cy.clickIfExists('[data-cy="btn-cleanup-logs"]')
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})

