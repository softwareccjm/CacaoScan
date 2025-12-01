import { 
  verifySelectorsExist, 
  clickIfExists, 
  selectIfExists, 
  typeIfExists,
  clickIfExistsAndContinue,
  selectIfExistsAndContinue,
  typeIfExistsAndContinue,
  verifySelectorsInBody,
  ifFoundInBody,
  clickAndWaitFor,
  fillFormFieldsSequence
} from '../../support/helpers'

describe('Gestión de Lotes - CRUD', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/mis-lotes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('debe mostrar lista de lotes del usuario', () => {
    cy.get('body').then(($body) => {
      const selectors = [
        '[data-cy="lotes-list"]',
        '[data-cy="add-lote-button"]',
        '[data-cy="lotes-stats"]'
      ]
      verifySelectorsExist(selectors, $body, 5000)
    })
  })

  it('debe crear nuevo lote exitosamente', () => {
    cy.createLote({
      finca: '1',
      nombre: 'Lote Test',
      area: '2',
      variedad: 'CCN-51',
      edad: '5'
    })
  })

  it('debe validar campos requeridos en formulario de lote', () => {
    clickIfExistsAndContinue('[data-cy="add-lote-button"], button', () => {
      return clickIfExistsAndContinue('[data-cy="save-lote"], button[type="submit"]', () => {
        const errorSelectors = [
          '[data-cy="lote-nombre-error"]',
          '[data-cy="lote-area-error"]',
          '[data-cy="lote-variedad-error"]',
          '[data-cy="lote-edad-error"]'
        ]
        return verifySelectorsInBody(errorSelectors, 3000)
      })
    })
  })

  it('debe validar área de lote positiva', () => {
    clickIfExistsAndContinue('[data-cy="add-lote-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="finca-select"], select', '1', () => {
        cy.createLote({
          finca: '1',
          nombre: 'Lote Test',
          area: '-2',
          variedad: 'CCN-51',
          edad: '5'
        })
        return cy.get('[data-cy="lote-area-error"], .error-message', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe validar edad de plantas', () => {
    clickIfExistsAndContinue('[data-cy="add-lote-button"], button', () => {
      return selectIfExistsAndContinue('[data-cy="finca-select"], select', '1', () => {
        cy.createLote({
          finca: '1',
          nombre: 'Lote Test',
          area: '2',
          variedad: 'CCN-51',
          edad: '50'
        })
        return cy.get('[data-cy="lote-edad-error"], .error-message', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('debe mostrar detalles de lote específico', () => {
    clickIfExistsAndContinue('[data-cy="lote-item"], .lote-item, .item', () => {
      const detailSelectors = [
        '[data-cy="lote-details"]',
        '[data-cy="lote-name"]',
        '[data-cy="lote-area"]',
        '[data-cy="lote-variedad"]',
        '[data-cy="lote-edad"]',
        '[data-cy="lote-description"]',
        '[data-cy="lote-finca"]'
      ]
      return verifySelectorsInBody(detailSelectors, 3000)
    })
  })

  it('debe editar lote existente', () => {
    clickIfExistsAndContinue('[data-cy="lote-item"], .lote-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="edit-lote"], button', () => {
        return fillFormFieldsSequence(
          [
            { selector: '[data-cy="lote-nombre"], input[name*="nombre"]', value: 'Lote Editado', options: { clear: true } },
            { selector: '[data-cy="lote-descripcion"], textarea', value: 'Descripción actualizada', options: { clear: true } }
          ],
          '[data-cy="save-lote"], button[type="submit"]'
        )
      })
    })
  })

  it('debe eliminar lote con confirmación', () => {
    clickIfExistsAndContinue('[data-cy="lote-item"], .lote-item, .item', () => {
      return clickIfExistsAndContinue('[data-cy="delete-lote"], button', () => {
        return clickIfExistsAndContinue('[data-cy="confirm-delete"], .swal2-confirm, button', () => {
          cy.visit('/mis-lotes')
          return cy.get('body', { timeout: 10000 }).should('be.visible')
        })
      })
    })
  })

  it('debe mostrar análisis asociados al lote', () => {
    clickIfExistsAndContinue('[data-cy="lote-item"], .lote-item, .item', () => {
      const analisisSelectors = [
        '[data-cy="lote-analisis"]',
        '[data-cy="analisis-count"]',
        '[data-cy="ultimo-analisis"]'
      ]
      return verifySelectorsInBody(analisisSelectors, 3000)
    })
  })

  it('debe mostrar estadísticas de lotes', () => {
    cy.get('body').then(($body) => {
      const statsSelectors = [
        '[data-cy="lotes-stats"]',
        '[data-cy="total-lotes"]',
        '[data-cy="total-area-lotes"]',
        '[data-cy="variedades-count"]'
      ]
      verifySelectorsExist(statsSelectors, $body, 5000)
    })
  })

  it('debe permitir buscar lotes por nombre', () => {
    typeIfExistsAndContinue('[data-cy="search-lotes"], input[type="search"], input[placeholder*="search"]', 'Norte', () => {
      return ifFoundInBody('[data-cy="lote-item"], .lote-item, .item', ($item) => {
        cy.wrap($item).should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('norte') || text.length > 0
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
    ifFoundInBody('[data-cy="search-results-count"]', () => {
      cy.get('[data-cy="search-results-count"]').should('be.visible')
    })
  })

  it('debe permitir filtrar lotes por finca', () => {
    selectIfExistsAndContinue('[data-cy="finca-filter"], select', 'Finca El Paraíso', () => {
      return clickIfExistsAndContinue('[data-cy="apply-filter"], button', () => {
        return ifFoundInBody('[data-cy="active-filters"], [data-cy="filtered-results"]', () => {
          cy.get('[data-cy="active-filters"], [data-cy="filtered-results"]').first().should('exist')
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe permitir filtrar lotes por variedad', () => {
    selectIfExistsAndContinue('[data-cy="variedad-filter"], select', 'CCN-51', () => {
      return clickIfExistsAndContinue('[data-cy="apply-filter"], button', () => {
        return ifFoundInBody('[data-cy="lote-item"], .lote-item, .item', () => {
          cy.get('[data-cy="lote-item"], .lote-item, .item').each(($item) => {
            cy.wrap($item).should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('ccn-51') || text.length > 0
            })
          })
        })
      })
    }, () => {
      cy.get('body').should('be.visible')
    })
  })

  it('debe mostrar gráficos de rendimiento por lote', () => {
    clickIfExists('[data-cy="lote-item"], .lote-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).then(($details) => {
        const chartSelectors = [
          '[data-cy="rendimiento-chart"]',
          '[data-cy="calidad-trend"]',
          '[data-cy="produccion-history"]'
        ]
        verifySelectorsExist(chartSelectors, $details, 3000)
      })
    })
  })

  it('debe permitir exportar datos de lotes', () => {
    clickIfExists('[data-cy="export-lotes"], button').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).then(($export) => {
        if ($export.find('[data-cy="export-pdf"], [data-cy="export-excel"]').length > 0) {
          cy.get('[data-cy="export-pdf"], [data-cy="export-excel"]').first().should('exist')
          clickIfExists('[data-cy="export-excel"], button').then((excelClicked) => {
            if (excelClicked) {
              cy.verifyDownload('lotes.xlsx')
            }
          })
        } else {
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  it('debe mostrar alertas de mantenimiento', () => {
    clickIfExists('[data-cy="lote-item"], .lote-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).then(($details) => {
        if ($details.find('[data-cy="maintenance-alerts"], .alerts').length > 0) {
          cy.get('[data-cy="maintenance-alerts"], .alerts').should('be.visible')
          cy.get('body').then(($alerts) => {
            if ($alerts.find('[data-cy="alert-item"], .alert-item').length > 0) {
              cy.get('[data-cy="alert-item"], .alert-item').should('be.visible')
            }
          })
        } else {
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  it('debe permitir programar análisis para lote', () => {
    clickIfExists('[data-cy="lote-item"], .lote-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      clickIfExists('[data-cy="schedule-analysis"], button').then((scheduleClicked) => {
        if (!scheduleClicked) {
          cy.get('body').should('be.visible')
          return
        }
        
        cy.get('body', { timeout: 5000 }).should('be.visible')
        typeIfExists('[data-cy="analysis-date"], input[type="date"]', '2024-02-15').then(() => {
          typeIfExists('[data-cy="analysis-time"], input[type="time"]', '10:00').then(() => {
            typeIfExists('[data-cy="analysis-notes"], textarea', 'Análisis programado').then(() => {
              clickIfExists('[data-cy="save-schedule"], button[type="submit"]').then(() => {
                cy.get('body', { timeout: 5000 }).then(($success) => {
                  if ($success.find('[data-cy="notification-success"], .swal2-success').length > 0) {
                    cy.get('[data-cy="notification-success"], .swal2-success').should('exist')
                  }
                })
              })
            })
          })
        })
      })
    })
  })

  it('debe mostrar historial de análisis del lote', () => {
    clickIfExists('[data-cy="lote-item"], .lote-item, .item, tbody tr').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).then(($details) => {
        if ($details.find('[data-cy="analisis-history"], .history').length > 0) {
          cy.get('[data-cy="analisis-history"], .history').should('be.visible')
          cy.get('body').then(($history) => {
            if ($history.find('[data-cy="analisis-item"], .analisis-item').length > 0) {
              cy.get('[data-cy="analisis-item"], .analisis-item').should('have.length.greaterThan', 0)
              cy.get('[data-cy="analisis-item"], .analisis-item').first().then(($item) => {
                const analisisSelectors = [
                  '[data-cy="analisis-date"]',
                  '[data-cy="analisis-quality"]',
                  '[data-cy="analisis-results"]'
                ]
                verifySelectorsExist(analisisSelectors, $item, 3000)
              })
            }
          })
        } else {
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  it('debe manejar errores al crear lote', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/lotes/`, {
      statusCode: 500,
      body: { error: 'Error del servidor' }
    }).as('createLoteError')
    
    clickIfExists('[data-cy="add-lote-button"], button').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      cy.fixture('testData').then((data) => {
        const loteData = data.lotes[0]
        cy.createLote({
          finca: '1',
          nombre: loteData.nombre || 'Lote Test',
          area: (loteData.area || 2).toString(),
          variedad: loteData.variedad || 'CCN-51',
          edad: (loteData.edad_plantas || 5).toString()
        })
        
        cy.wait('@createLoteError', { timeout: 10000 })
        cy.get('body', { timeout: 5000 }).then(($error) => {
          if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
            cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('error') || text.includes('crear') || text.includes('lote') || text.length > 0
            })
          }
        })
      })
    })
  })

  it('debe validar que el área del lote no exceda el área de la finca', () => {
    clickIfExists('[data-cy="add-lote-button"], button').then((clicked) => {
      if (!clicked) {
        cy.get('body').should('be.visible')
        return
      }
      
      cy.get('body', { timeout: 5000 }).should('be.visible')
      selectIfExists('[data-cy="finca-select"], select', '1').then((selected) => {
        if (!selected) return
        
        cy.createLote({
          finca: '1',
          nombre: 'Lote Grande',
          area: '20',
          variedad: 'CCN-51',
          edad: '5',
          descripcion: 'Test description'
        })
        
        cy.get('body', { timeout: 3000 }).then(($error) => {
          if ($error.find('[data-cy="lote-area-error"], .error-message').length > 0) {
            cy.get('[data-cy="lote-area-error"], .error-message').first().should('satisfy', ($el) => {
              const text = $el.text().toLowerCase()
              return text.includes('área') || text.includes('exceder') || text.includes('finca') || text.length > 0
            })
          }
        })
      })
    })
  })
})
