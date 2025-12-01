/**
 * Validation-specific helpers for form validation tests
 * Extracts common patterns from validation-forms.cy.js
 */
import {
  visitAndWaitForBody,
  openModalAndExecute,
  fillFieldSubmitAndVerifyError,
  verifyErrorMessageWithSelectors,
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue
} from './helpers'

/**
 * Validates a field in a modal with error verification
 * Common pattern: visit page -> open modal -> fill field -> submit -> verify error
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {string} fieldSelector - Selector for field to validate
 * @param {string} value - Invalid value to test
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateFieldInModal(
  pageUrl,
  buttonSelector,
  fieldSelector,
  value,
  submitSelector,
  errorSelector,
  expectedTexts
) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(fieldSelector).length > 0) {
      fillFieldSubmitAndVerifyError(fieldSelector, value, submitSelector, errorSelector, expectedTexts)
    }
  })
}

/**
 * Validates required fields in a modal
 * Common pattern: visit page -> open modal -> submit -> verify multiple errors
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {string} submitSelector - Selector for submit button
 * @param {Array<string>} errorSelectors - Array of error selectors to verify
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateRequiredFieldsInModal(pageUrl, buttonSelector, submitSelector, errorSelectors) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(submitSelector).length > 0) {
      cy.get(submitSelector).first().click()
      cy.get('body', { timeout: 5000 }).then(($afterSubmit) => {
        verifySelectorsExist(errorSelectors, $afterSubmit, 3000)
      })
    }
  })
}

/**
 * Validates field format (email, phone, document, etc.)
 * Common pattern: visit page -> fill field -> submit -> verify error
 * @param {string} pageUrl - URL to visit
 * @param {string} fieldSelector - Selector for field to validate
 * @param {string} invalidValue - Invalid value to test
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateFieldFormat(pageUrl, fieldSelector, invalidValue, submitSelector, errorSelector, expectedTexts) {
  visitAndWaitForBody(pageUrl)
  return fillFieldSubmitAndVerifyError(fieldSelector, invalidValue, submitSelector, errorSelector, expectedTexts)
}

/**
 * Validates multiple fields in a modal
 * Common pattern: visit page -> open modal -> fill multiple fields -> submit -> verify errors
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {Array<Object>} fields - Array of field objects { selector, value }
 * @param {string} submitSelector - Selector for submit button
 * @param {Array<string>} errorSelectors - Array of error selectors to verify
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateMultipleFieldsInModal(pageUrl, buttonSelector, fields, submitSelector, errorSelectors) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    fields.forEach(({ selector, value }) => {
      if ($modal.find(selector).length > 0) {
        const $field = cy.get(selector).first()
        // Check if it's a select element
        if ($modal.find(selector).is('select')) {
          $field.select(value, { force: true })
        } else {
          $field.type(value, { force: true })
        }
      }
    })
    if ($modal.find(submitSelector).length > 0) {
      cy.get(submitSelector).first().click({ force: true })
      cy.get('body', { timeout: 3000 }).then(($error) => {
        if (Array.isArray(errorSelectors)) {
          verifySelectorsExist(errorSelectors, $error, 3000)
        } else {
          verifyErrorMessageWithSelectors([errorSelectors], [])
        }
      })
    }
  })
}

/**
 * Validates conditional fields in a modal
 * Common pattern: visit page -> open modal -> select option -> verify conditional field -> submit -> verify error
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {string} triggerSelector - Selector for field that triggers conditional field
 * @param {string} triggerValue - Value to set in trigger field
 * @param {string} conditionalSelector - Selector for conditional field
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateConditionalFieldInModal(
  pageUrl,
  buttonSelector,
  triggerSelector,
  triggerValue,
  conditionalSelector,
  submitSelector,
  errorSelector,
  expectedTexts
) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(triggerSelector).length > 0) {
      cy.get(triggerSelector).first().select(triggerValue, { force: true })
      cy.get('body', { timeout: 3000 }).then(($afterSelect) => {
        ifFoundInBody(conditionalSelector, () => {
          cy.get(conditionalSelector).should('exist')
        })
        clickIfExistsAndContinue(submitSelector, () => {
          verifyErrorMessageWithSelectors([errorSelector], expectedTexts)
        })
      })
    }
  })
}

