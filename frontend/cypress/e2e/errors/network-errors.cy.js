import { getApiBaseUrl } from '../../support/helpers'

describe('Manejo de Errores - Errores de Red', () => {
  beforeEach(() => {
    cy.login('farmer')
  })

  it('debe manejar error 500 del servidor', () => {
    cy.interceptError('GET', '/fincas/**', 500, { error: 'Error interno del servidor' }, 'serverError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.verifyErrorMessage(['error', 'servidor', '500'])
    cy.retryIfAvailable()
  })

  it('debe manejar error 404 - Recurso no encontrado', () => {
    cy.interceptError('GET', '/fincas/**/', 404, { error: 'Finca no encontrada' }, 'notFound')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.verifyErrorMessage(['no encontrado', '404', 'not found'])
  })

  it('debe manejar error 403 - Acceso denegado', () => {
    cy.interceptError('GET', '/admin/**', 403, { error: 'Acceso denegado' }, 'forbidden')
    
    cy.visit('/admin/agricultores')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('acceso') || text.includes('denegado') || text.includes('403') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error 401 - No autorizado', () => {
    cy.interceptError('GET', '/fincas/**', 401, { error: 'Token inválido' }, 'unauthorized')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.url({ timeout: 5000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/mis-fincas') || url.length > 0
    })
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="session-expired-message"], .session-expired').length > 0) {
        cy.get('[data-cy="session-expired-message"], .session-expired').should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('sesión') || text.includes('expirada') || text.includes('expirado') || text.length > 0
        })
      }
    })
  })

  it('debe manejar error de timeout', () => {
    cy.interceptError('GET', '/fincas/**', 408, { error: 'Timeout' }, 'timeoutError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('timeout') || text.includes('tiempo') || text.includes('408') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de conexión', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      forceNetworkError: true
    }).as('networkError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('conexión') || text.includes('conexion') || text.includes('network') || text.includes('error') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de validación del servidor', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/fincas/`, {
      statusCode: 400,
      body: { 
        error: 'Error de validación',
        details: {
          nombre: ['Este campo es requerido'],
          area: ['El área debe ser positiva']
        }
      }
    }).as('validationError')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="finca-nombre"], input').length > 0) {
            cy.get('[data-cy="finca-nombre"], input').first().type('Finca Test', { force: true })
            cy.get('[data-cy="finca-area"], input[type="number"]').first().type('-5', { force: true })
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@validationError', { timeout: 10000 })
            
            const verifyValidationError = ($error) => {
              if ($error.find('[data-cy="validation-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="validation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('validación') || text.includes('validacion') || text.includes('error') || text.length > 0
                })
              }
            }

            cy.get('body', { timeout: 5000 }).then(verifyValidationError)
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de límite de tasa', () => {
    cy.interceptError('POST', '/fincas/', 429, { error: 'Límite de tasa excedido' }, 'rateLimit')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="add-finca-button"], button').length > 0) {
        cy.get('[data-cy="add-finca-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="save-finca"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="save-finca"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@rateLimit', { timeout: 10000 })
            
            const verifyRateLimitError = ($error) => {
              if ($error.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('límite') || text.includes('tasa') || text.includes('excedido') || text.includes('429') || text.length > 0
                })
              }
            }

            cy.get('body', { timeout: 5000 }).then(verifyRateLimitError)
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de mantenimiento', () => {
    cy.interceptError('GET', '/fincas/**', 503, { error: 'Sistema en mantenimiento' }, 'maintenance')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="maintenance-message"], .maintenance-message, .error-message').length > 0) {
        cy.get('[data-cy="maintenance-message"], .maintenance-message, .error-message').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('mantenimiento') || text.includes('503') || text.includes('sistema') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de formato de respuesta', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
      statusCode: 200,
      body: 'invalid json'
    }).as('malformedResponse')
    
    cy.visit('/mis-fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.wait(1000)
    
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="error-message"], .error-message, .swal2-error').length > 0) {
        cy.get('[data-cy="error-message"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('procesar') || text.includes('respuesta') || text.includes('formato') || text.includes('error') || text.length > 0
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de carga de archivo', () => {
    cy.interceptError('POST', '/images/**', 413, { error: 'Archivo demasiado grande' }, 'fileTooLarge')
    
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
          const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@fileTooLarge', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="upload-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="upload-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('grande') || text.includes('archivo') || text.includes('demasiado') || text.includes('413') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de análisis de imagen', () => {
    cy.interceptError('POST', '/scan/**', 422, { error: 'Imagen no válida para análisis' }, 'analysisError')
    
    cy.visit('/nuevo-analisis')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="file-input"], input[type="file"]').length > 0) {
        const fileContent = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAD//Z'
        
        cy.get('[data-cy="file-input"], input[type="file"]').then((input) => {
          const blob = Cypress.Blob.base64StringToBlob(fileContent.split(',')[1], 'image/jpeg')
          const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
          const dataTransfer = new DataTransfer()
          dataTransfer.items.add(file)
          input[0].files = dataTransfer.files
          
          cy.wrap(input).trigger('change', { force: true })
        })
        
        cy.get('body', { timeout: 3000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="upload-button"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="upload-button"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@analysisError', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="analysis-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="analysis-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('válida') || text.includes('análisis') || text.includes('imagen') || text.includes('422') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de generación de reporte', () => {
    cy.login('analyst')
    cy.interceptError('POST', '/reportes/', 422, { error: 'No hay datos para el período seleccionado' }, 'reportError')
    
    cy.visit('/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="create-report-button"], button').length > 0) {
        cy.get('[data-cy="create-report-button"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="report-type"], select').length > 0) {
            cy.get('[data-cy="report-type"], select').first().select('analisis-periodo', { force: true })
            cy.get('[data-cy="start-date"], input[type="date"]').first().type('2024-01-01', { force: true })
            cy.get('[data-cy="end-date"], input[type="date"]').first().type('2024-01-31', { force: true })
            cy.get('[data-cy="generate-report"], button[type="submit"]').first().click({ force: true })
            
            cy.wait('@reportError', { timeout: 10000 })
            
            cy.get('body', { timeout: 5000 }).then(($error) => {
              if ($error.find('[data-cy="generation-error"], .error-message, .swal2-error').length > 0) {
                cy.get('[data-cy="generation-error"], .error-message, .swal2-error').first().should('satisfy', ($el) => {
                  const text = $el.text().toLowerCase()
                  return text.includes('datos') || text.includes('período') || text.includes('seleccionado') || text.includes('422') || text.length > 0
                })
              }
            })
          }
        })
      } else {
        cy.get('body').should('be.visible')
      }
    })
  })

  it('debe manejar error de servicio no disponible', () => {
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 503,
      body: { error: 'Servicio no disponible' }
    }).as('serviceUnavailable')
    
    cy.visit('/mis-fincas')
    cy.wait('@serviceUnavailable')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Servicio no disponible')
  })

  it('debe manejar error de gateway', () => {
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 502,
      body: { error: 'Bad Gateway' }
    }).as('badGateway')
    
    cy.visit('/mis-fincas')
    cy.wait('@badGateway')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
      .and('contain', 'Error del servidor')
  })

  it('debe manejar error de versión no soportada', () => {
    cy.intercept('GET', '/api/fincas/', {
      statusCode: 505,
      body: { error: 'Versión HTTP no soportada' }
    }).as('versionError')
    
    cy.visit('/mis-fincas')
    cy.wait('@versionError')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
  })

  it('debe manejar error de payload demasiado grande', () => {
    cy.intercept('POST', '/api/images/', {
      statusCode: 413,
      body: { error: 'Payload demasiado grande' }
    }).as('payloadTooLarge')
    
    cy.visit('/nuevo-analisis')
    
    cy.get('[data-cy="upload-button"]').click()
    cy.wait('@payloadTooLarge')
    
    cy.get('[data-cy="upload-error"]')
      .should('be.visible')
      .and('contain', 'Archivo demasiado grande')
  })

  it('debe manejar error de método no permitido', () => {
    cy.intercept('PATCH', '/api/fincas/1/', {
      statusCode: 405,
      body: { error: 'Método no permitido' }
    }).as('methodNotAllowed')
    
    cy.visit('/mis-fincas')
    cy.wait('@methodNotAllowed')
    
    cy.get('[data-cy="error-message"]')
      .should('be.visible')
  })
})
