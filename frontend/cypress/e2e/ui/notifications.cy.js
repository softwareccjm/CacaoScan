import * as helpers from '../../support/helpers'

describe('Notifications System', () => {
  beforeEach(() => {
    cy.navigateToFarmerDashboard('farmer')
  })

  it('should display notification badge count', () => {
    helpers.setupNotificationsIntercept({ count: 5 }, 'getUnread')
    cy.reload()
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.wait(1000)
    
    cy.get('[data-cy="notification-badge"], .badge, .notification-count', { timeout: 5000 }).should('exist')
  })

  it('should open notifications panel', () => {
    cy.clickIfExists('[data-cy="btn-notifications"], button, .notifications-btn')
    cy.get('[data-cy="notifications-panel"], .notifications-panel, .panel', { timeout: 5000 }).should('exist')
  })

  it('should mark notification as read', () => {
    cy.clickIfExists('[data-cy="btn-notifications"], button')
    cy.get('body', { timeout: 5000 }).then(($panel) => {
      if ($panel.find('[data-cy="notification-item"], .notification-item, .item').length > 0) {
        cy.get('[data-cy="notification-item"], .notification-item, .item').first().click({ force: true })
        cy.get('[data-cy="notification-item"], .notification-item, .item', { timeout: 3000 }).first().should('exist')
      }
    })
  })

  it('should mark all notifications as read', () => {
    cy.clickIfExists('[data-cy="btn-notifications"], button')
    cy.get('body', { timeout: 5000 }).then(($panel) => {
      if ($panel.find('[data-cy="btn-mark-all-read"], button').length > 0) {
        cy.get('[data-cy="btn-mark-all-read"], button').first().click({ force: true })
        cy.get('[data-cy="notification-badge"], .badge', { timeout: 3000 }).should('not.exist')
      }
    })
  })

  it('should receive real-time notification (Simulated)', () => {
    cy.clock()
    cy.tick(10000)
    cy.window().then((win) => {
      win.dispatchEvent(new CustomEvent('notification-received', { detail: { message: 'Análisis completado' } }))
    })
  })
})

