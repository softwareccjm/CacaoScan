describe('Admin Usuarios E2E Tests', () => {
  beforeEach(() => {
    cy.navigateToAdminUsers('admin')
  })

  it('should display users list', () => {
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should filter users by role', () => {
    cy.filterUsersByRole('farmer')
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should search users', () => {
    cy.searchUsers('test@example.com')
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should view user details', () => {
    cy.viewUser(0)
  })

  it('should edit user', () => {
    cy.editUser(0)
  })

  it('should delete user with confirmation', () => {
    cy.deleteUserWithConfirmation(0)
    cy.get('[data-cy="users-table"]').should('be.visible')
  })
})

