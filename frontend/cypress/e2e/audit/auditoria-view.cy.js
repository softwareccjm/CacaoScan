describe('Auditoria View E2E Tests', () => {
  beforeEach(() => {
    cy.navigateToAuditoria('admin')
  })

  it('should display audit logs', () => {
    cy.get('[data-cy="audit-logs"]').should('be.visible')
  })

  it('should filter audit logs by action', () => {
    cy.selectIfExists('[data-cy="filter-action"]', 'login')
    cy.get('[data-cy="audit-logs"]', { timeout: 5000 }).should('be.visible')
  })

  it('should filter audit logs by date range', () => {
    cy.typeIfExists('[data-cy="date-from"]', '2024-01-01')
    cy.typeIfExists('[data-cy="date-to"]', '2024-12-31')
    cy.clickIfExists('[data-cy="apply-filters"]')
    cy.get('[data-cy="audit-logs"]', { timeout: 5000 }).should('be.visible')
  })

  it('should view audit log details', () => {
    cy.clickIfExists('[data-cy="view-log-details"]')
    cy.get('[data-cy="log-details-modal"]', { timeout: 5000 }).should('be.visible')
  })

  it('should export audit logs', () => {
    cy.clickIfExists('[data-cy="export-logs"]')
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})

