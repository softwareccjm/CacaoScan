describe('Admin Training E2E Tests', () => {
  beforeEach(() => {
    cy.navigateToTraining('admin')
  })

  it('should display training jobs list', () => {
    cy.waitForTrainingJobs()
  })

  it('should create new training job', () => {
    cy.get('[data-cy="create-training-job"]').click()
    cy.get('[data-cy="training-job-form"]').should('be.visible')
    
    cy.get('[data-cy="job-type"]').select('regression')
    cy.get('[data-cy="epochs"]').type('100')
    cy.get('[data-cy="batch-size"]').type('32')
    cy.get('[data-cy="submit-training"]').click()
    
    cy.waitForTrainingJobs()
  })

  it('should view training job status', () => {
    cy.get('[data-cy="view-job-status"]').first().click()
    cy.get('[data-cy="job-status-modal"]').should('be.visible')
  })

  it('should cancel training job', () => {
    cy.get('[data-cy="cancel-job"]').first().click()
    cy.confirmAction('[data-cy="confirm-cancel"]')
    cy.waitForTrainingJobs()
  })
})

