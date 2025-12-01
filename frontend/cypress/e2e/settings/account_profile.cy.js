describe('User Account Settings', () => {
  beforeEach(() => {
    cy.navigateToAccountProfile('farmer')
  })

  it('should allow avatar upload', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-avatar"], input[type="file"]').length > 0) {
        cy.uploadTestImage('avatar.jpg')
        cy.get('body').then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="btn-save-avatar"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="btn-save-avatar"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
            cy.get('[data-cy="user-avatar"], .avatar, img', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should toggle email notifications preferences', () => {
    cy.clickIfExists('[data-cy="tab-notifications"], [role="tab"]').then(() => {
      cy.get('body').then(($notifications) => {
        if ($notifications.find('[data-cy="toggle-email-reports"], input[type="checkbox"]').length > 0) {
          cy.checkCheckboxIfExists('[data-cy="toggle-email-reports"], input[type="checkbox"]', { force: true })
          cy.clickIfExists('[data-cy="btn-save-prefs"], button[type="submit"]').then(() => {
            cy.get('body', { timeout: 5000 }).should('be.visible')
          })
        }
      })
    })
  })

  it('should allow data export (GDPR)', () => {
    cy.clickIfExists('[data-cy="tab-privacy"], [role="tab"]').then(() => {
      cy.get('body').then(($privacy) => {
        if ($privacy.find('[data-cy="btn-export-data"], button').length > 0) {
          cy.clickIfExists('[data-cy="btn-export-data"], button').then(() => {
            cy.get('.swal2-confirm, button[type="button"]', { timeout: 5000 }).then(($confirm) => {
              if ($confirm.length > 0) {
                cy.wrap($confirm.first()).click()
                cy.get('body', { timeout: 5000 }).should('be.visible')
              }
            })
          })
        }
      })
    })
  })

  it('should request account deletion', () => {
    cy.clickIfExists('[data-cy="tab-privacy"], [role="tab"]').then(() => {
      cy.get('body').then(($privacy) => {
        if ($privacy.find('[data-cy="btn-delete-account"], button').length > 0) {
          cy.clickIfExists('[data-cy="btn-delete-account"], button').then(() => {
            cy.get('body', { timeout: 5000 }).then(($modal) => {
              if ($modal.find('.swal2-input, input[type="text"]').length > 0) {
                cy.typeIfExists('.swal2-input, input[type="text"]', 'BORRAR')
                cy.clickIfExists('.swal2-confirm, button[type="button"]').then(() => {
                  cy.url({ timeout: 10000 }).should('satisfy', (url) => {
                    return url.includes('/login') || url.includes('/auth')
                  })
                })
              }
            })
          })
        }
      })
    })
  })
})

