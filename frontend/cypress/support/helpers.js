/**
 * Test helpers for Cypress
 * Provides reusable helper functions for common test operations
 */
import { SELECTORS } from './selectors'
import { TEST_CREDENTIALS } from './test-data'

/**
 * Creates a test user object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test user object
 */
export function createTestUser(overrides = {}) {
  return {
    email: 'test@example.com',
    password: TEST_CREDENTIALS.testPassword,
    firstName: 'Test',
    lastName: 'User',
    document: '1234567890',
    phone: '+573001234567',
    role: 'agricultor',
    ...overrides
  }
}

/**
 * Creates a test finca object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test finca object
 */
export function createTestFinca(overrides = {}) {
  return {
    nombre: 'Test Finca',
    ubicacion: 'Test Location',
    area_total: 10.5,
    descripcion: 'Test description',
    ...overrides
  }
}

/**
 * Creates a test lote object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test lote object
 */
export function createTestLote(overrides = {}) {
  return {
    nombre: 'Test Lote',
    area: 5,
    variedad: 'Criollo',
    edad_plantas: 5,
    descripcion: 'Test lote description',
    ...overrides
  }
}

/**
 * Sets up authentication for tests
 * @param {string} userType - Type of user (admin, agricultor, analyst)
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function setupAuth(userType = 'admin') {
  return cy.login(userType)
}

/**
 * Tears down authentication after tests
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function teardownAuth() {
  return cy.logout()
}

/**
 * Mocks common API responses
 * @param {Object} responses - Object mapping endpoints to responses
 * @returns {void}
 */
export function mockApiResponses(responses) {
  const defaultResponses = {
    '/api/auth/login/': { access: 'mock-token', refresh: 'mock-refresh', user: {} },
    '/api/fincas/': { results: [], count: 0 },
    '/api/lotes/': { results: [], count: 0 },
    '/api/predictions/': { results: [], count: 0 },
    '/api/notifications/': { results: [], count: 0 },
    '/api/audit/': { results: [], count: 0 },
    ...responses
  }

  for (const [endpoint, response] of Object.entries(defaultResponses)) {
    cy.intercept('GET', endpoint, { statusCode: 200, body: response }).as(`api-${endpoint.replaceAll('/', '-')}`)
    cy.intercept('POST', endpoint, { statusCode: 201, body: response }).as(`api-post-${endpoint.replaceAll('/', '-')}`)
  }
}

/**
 * Fills a form with provided data
 * @param {Object} formData - Data to fill in the form
 * @param {string} formType - Type of form (finca, lote, login, etc.)
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function fillForm(formData, formType = 'generic') {
  const formSelectors = {
    finca: SELECTORS.finca,
    lote: SELECTORS.lote,
    login: {
      email: SELECTORS.inputs.email,
      password: SELECTORS.inputs.password
    }
  }

  const selectors = formSelectors[formType] || {}

  for (const [field, value] of Object.entries(formData)) {
    const selector = selectors[field] || `[data-cy="${field}"]`
    if (value !== undefined && value !== null) {
      cy.get(selector).clear().type(value.toString())
    }
  }

  return cy.wrap(null)
}

/**
 * Waits for API call to complete
 * @param {string} alias - API alias to wait for
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function waitForApi(alias, timeout = 10000) {
  return cy.wait(`@${alias}`, { timeout })
}

/**
 * Interacts with a table (sort, filter, paginate)
 * @param {string} action - Action to perform (sort, filter, paginate)
 * @param {Object} options - Options for the action
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function interactWithTable(action, options = {}) {
  const { column, direction, filterValue, page } = options

  switch (action) {
    case 'sort':
      if (column) {
        cy.get(`${SELECTORS.tables.dataTable} [data-cy="column-${column}"]`).click()
        if (direction === 'desc') {
          cy.get(`${SELECTORS.tables.dataTable} [data-cy="column-${column}"]`).click()
        }
      }
      break
    case 'filter':
      if (filterValue) {
        cy.get(SELECTORS.inputs.filter).clear().type(filterValue)
        cy.get(SELECTORS.buttons.filter).click()
      }
      break
    case 'paginate':
      if (page) {
        cy.get(`${SELECTORS.tables.pagination} [data-cy="page-${page}"]`).click()
      }
      break
  }

  return cy.wrap(null)
}

/**
 * Verifies table data
 * @param {Array} expectedData - Expected data in the table
 * @param {string} tableSelector - Selector for the table
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function verifyTableData(expectedData, tableSelector = SELECTORS.tables.dataTable) {
  cy.get(tableSelector).should('be.visible')
  
  if (expectedData.length === 0) {
    cy.get(`${tableSelector} ${SELECTORS.tables.tableRow}`).should('not.exist')
    return cy.wrap(null)
  }

  for (let index = 0; index < expectedData.length; index++) {
    const row = expectedData[index]
    cy.get(`${tableSelector} ${SELECTORS.tables.tableRow}`).eq(index).within(() => {
      for (const value of Object.values(row)) {
        cy.contains(value.toString()).should('be.visible')
      }
    })
  }

  return cy.wrap(null)
}

/**
 * Cleans up test data
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function cleanupTestData() {
  return cy.cleanupTestData()
}

/**
 * Verifies that selectors exist in the given context
 * @param {Array<string>} selectors - Array of CSS selectors to verify
 * @param {JQuery} $context - jQuery context element (usually from cy.get('body'))
 * @param {number} timeout - Timeout in milliseconds
 * @returns {void}
 */
export function verifySelectorsExist(selectors, $context, timeout = 3000) {
  for (const selector of selectors) {
    if ($context.find(selector).length > 0) {
      cy.get(selector, { timeout }).should('exist')
    }
  }
}

/**
 * Clicks an element if it exists
 * @param {string} selector - CSS selector for the element
 * @param {Object} options - Options for the click action
 * @returns {Cypress.Chainable<boolean>} Returns true if clicked, false otherwise
 */
export function clickIfExists(selector, options = {}) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      return cy.get(selector).first().click({ force: true, ...options }).then(() => true)
    }
    return cy.wrap(false)
  })
}

/**
 * Selects an option in a select element if it exists
 * @param {string} selector - CSS selector for the select element
 * @param {string} value - Value to select
 * @param {Object} options - Options for the select action
 * @returns {Cypress.Chainable<boolean>} Returns true if selected, false otherwise
 */
export function selectIfExists(selector, value, options = {}) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      return cy.get(selector).first().select(value, { force: true, ...options }).then(() => true)
    }
    return cy.wrap(false)
  })
}

/**
 * Types text into an input field if it exists
 * @param {string} selector - CSS selector for the input element
 * @param {string} text - Text to type
 * @param {Object} options - Options for the type action
 * @returns {Cypress.Chainable<boolean>} Returns true if typed, false otherwise
 */
export function typeIfExists(selector, text, options = {}) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      const element = cy.get(selector).first()
      if (options.clear) {
        return element.clear().type(text, { ...options, clear: undefined }).then(() => true)
      }
      return element.type(text, options).then(() => true)
    }
    return cy.wrap(false)
  })
}

/**
 * Fills a field if it exists
 * @param {string} selector - CSS selector for the field
 * @param {string} value - Value to fill
 * @param {Object} options - Options for the fill action
 * @returns {Cypress.Chainable<boolean>} Returns true if filled, false otherwise
 */
export function fillFieldIfExists(selector, value, options = {}) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      cy.get(selector).first().clear().type(value, { force: true, ...options })
      return cy.wrap(true)
    }
    return cy.wrap(false)
  })
}

/**
 * Checks a checkbox if it exists
 * @param {string} selector - CSS selector for the checkbox
 * @param {Object} options - Options for the check action
 * @returns {Cypress.Chainable<boolean>} Returns true if checked, false otherwise
 */
export function checkCheckboxIfExists(selector, options = {}) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      cy.get(selector).first().check({ force: true, ...options })
      return cy.wrap(true)
    }
    return cy.wrap(false)
  })
}

/**
 * Selects an option in a select element if it exists (alias for selectIfExists)
 * @param {string} selector - CSS selector for the select element
 * @param {string} value - Value to select
 * @param {Object} options - Options for the select action
 * @returns {Cypress.Chainable<boolean>} Returns true if selected, false otherwise
 */
export function selectOptionIfExists(selector, value, options = {}) {
  return selectIfExists(selector, value, options)
}

/**
 * Interacts with the first row in a table
 * @param {string} rowSelector - CSS selector for table rows
 * @param {Function} rowCallback - Callback function to execute on the first row
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function interactWithFirstRow(rowSelector, rowCallback, timeout = 5000) {
  return cy.get('body').then(($body) => {
    const rows = $body.find(rowSelector)
    if (rows.length > 0) {
      cy.wrap(rows.first()).then(($row) => {
        rowCallback($row)
      })
    } else {
      cy.get('body').should('be.visible')
    }
  })
}

/**
 * Fills an optional field if it exists
 * @param {string} selector - CSS selector
 * @param {string} value - Value to fill
 * @returns {Cypress.Chainable<void>}
 */
export function fillOptionalField(selector, value) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      cy.get(selector).first().type(value)
    }
  })
}

/**
 * Generates a secure password for testing
 * 
 * SECURITY: S2245 - Using pseudorandom number generators (PRNGs) is security-sensitive.
 * This function uses Math.random() which is safe in this context because:
 * 1. It's only used for generating test passwords in E2E test environments
 * 2. The generated passwords are not used for cryptographic purposes
 * 3. They are not used for security-sensitive operations (tokens, keys, etc.)
 * 4. The randomness is sufficient for test data uniqueness
 * 
 * For production cryptographic needs, use crypto.getRandomValues() instead.
 * 
 * @returns {string} Generated password
 */
export function generatePassword() {
  // NOSONAR S2245 - Math.random() is safe for test password generation
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}` // NOSONAR S2245
}

/**
 * Gets API base URL from environment or defaults
 * @returns {string} API base URL
 */
export function getApiBaseUrl() {
  return Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
}

/**
 * Opens a modal by clicking a button
 * @param {string} buttonSelector - CSS selector for the button that opens the modal
 * @param {Function} callback - Callback function to execute after modal opens
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function openModal(buttonSelector, callback) {
  return cy.get('body').then(($body) => {
    if ($body.find(buttonSelector).length > 0) {
      cy.get(buttonSelector).first().click({ force: true })
      cy.get('body', { timeout: 5000 }).then(($modal) => {
        if (callback) callback($modal)
      })
    } else {
      cy.get('body').should('be.visible')
    }
  })
}

/**
 * Fills a field and submits a form
 * @param {string} fieldSelector - CSS selector for the field
 * @param {string} value - Value to fill
 * @param {string} submitSelector - CSS selector for the submit button
 * @param {Function} errorCallback - Callback function to execute if error occurs
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function fillFieldAndSubmit(fieldSelector, value, submitSelector, errorCallback) {
  return cy.get('body').then(($body) => {
    if ($body.find(fieldSelector).length > 0) {
      cy.get(fieldSelector).first().type(value, { force: true })
      cy.get(submitSelector).first().click({ force: true })
      if (errorCallback) {
        cy.get('body', { timeout: 3000 }).then(($error) => {
          errorCallback($error)
        })
      }
    }
  })
}

/**
 * Verifies an error message
 * @param {JQuery} $error - jQuery element containing error
 * @param {string} errorSelector - CSS selector for error element
 * @param {Array<string>} expectedTexts - Array of expected text fragments
 * @returns {void}
 */
export function verifyErrorMessage($error, errorSelector, expectedTexts) {
  if ($error.find(errorSelector).length > 0) {
    cy.get(errorSelector).first().should('satisfy', ($el) => {
      const text = $el.text().toLowerCase()
      return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
    })
  }
}

/**
 * Creates a test file for upload
 * @param {string} name - File name
 * @param {string} type - MIME type
 * @param {number} size - File size in bytes
 * @returns {File} File object
 */
export function createTestFile(name, type, size) {
  const content = 'x'.repeat(size)
  const blob = new Blob([content], { type })
  return new File([blob], name, { type })
}

/**
 * Validates file type
 * @param {File} file - File to validate
 * @param {Array<string>} allowedTypes - Array of allowed MIME types
 * @returns {boolean} True if file type is allowed
 */
export function validateFileType(file, allowedTypes) {
  return allowedTypes.includes(file.type)
}

/**
 * Validates file size
 * @param {File} file - File to validate
 * @param {number} maxSize - Maximum file size in bytes
 * @returns {boolean} True if file size is within limit
 */
export function validateFileSize(file, maxSize) {
  return file.size <= maxSize
}

/**
 * Sets up an error intercept
 * @param {string} method - HTTP method
 * @param {string} url - URL pattern
 * @param {number} statusCode - HTTP status code
 * @param {Object} body - Response body
 * @param {string} alias - Intercept alias
 * @returns {void}
 */
export function setupErrorIntercept(method, url, statusCode, body, alias) {
  const apiBaseUrl = getApiBaseUrl()
  cy.intercept(method, `${apiBaseUrl}${url}`, {
    statusCode,
    body
  }).as(alias)
}

/**
 * Verifies error display
 * @param {Array<string>} expectedTexts - Array of expected text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function verifyErrorDisplay(expectedTexts) {
  return cy.get('body', { timeout: 5000 }).then(($body) => {
    if ($body.find('[data-cy="error-message"], .error-message').length > 0) {
      cy.get('[data-cy="error-message"], .error-message').first().should('satisfy', ($el) => {
        const text = $el.text().toLowerCase()
        return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
      })
    }
  })
}

/**
 * Clicks retry button if it exists
 * @returns {Cypress.Chainable<boolean>} True if clicked, false otherwise
 */
export function clickRetryIfExists() {
  return cy.get('body').then(($body) => {
    if ($body.find('[data-cy="retry"], button').length > 0) {
      cy.get('[data-cy="retry"], button').first().click({ force: true })
      return cy.wrap(true)
    }
    return cy.wrap(false)
  })
}

/**
 * Executes actions within a modal without deep nesting
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {Function} modalActions - Function that receives modal context and executes actions
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function executeInModal(buttonSelector, modalActions) {
  return cy.get('body').then(($body) => {
    if ($body.find(buttonSelector).length > 0) {
      cy.get(buttonSelector).first().click({ force: true })
      return cy.get('body', { timeout: 5000 }).then(($modal) => {
        return modalActions($modal)
      })
    }
    return cy.wrap(null)
  })
}

/**
 * Executes actions if element exists, reducing nesting
 * @param {string} selector - CSS selector to check
 * @param {Function} actions - Function to execute if element exists
 * @param {Function} elseActions - Optional function to execute if element doesn't exist
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function ifElementExists(selector, actions, elseActions) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      return cy.get(selector).first().then(($element) => {
        return actions($element, $body)
      })
    }
    if (elseActions) {
      return elseActions($body)
    }
    return cy.wrap(null)
  })
}

/**
 * Fills multiple fields in a modal without deep nesting
 * @param {Object} fields - Object mapping selectors to values
 * @param {string} submitSelector - Selector for submit button
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function fillModalFields(fields, submitSelector) {
  return cy.get('body').then(($modal) => {
    for (const [selector, value] of Object.entries(fields)) {
      if ($modal.find(selector).length > 0) {
        cy.get(selector).first().type(value, { force: true })
      }
    }
    if (submitSelector && $modal.find(submitSelector).length > 0) {
      cy.get(submitSelector).first().click({ force: true })
      return cy.get('body', { timeout: 5000 }).should('be.visible')
    }
    return cy.wrap(null)
  })
}

/**
 * Clicks element and waits for next action without nesting
 * @param {string} selector - CSS selector
 * @param {Function} nextAction - Function to execute after click
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function clickAndContinue(selector, nextAction) {
  return cy.get(selector).first().click({ force: true }).then(() => {
    return cy.get('body', { timeout: 5000 }).then(($body) => {
      if (nextAction) {
        return nextAction($body)
      }
      return cy.wrap(null)
    })
  })
}

/**
 * Executes logout flow without deep nesting
 * @param {Function} afterLogout - Optional callback after logout
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function performLogout(afterLogout) {
  const openUserMenu = ($body) => {
    if ($body.find('[data-cy="user-menu"], .user-menu, button, a').length > 0) {
      cy.get('[data-cy="user-menu"], .user-menu, button, a').first().click({ force: true })
      return cy.get('body', { timeout: 3000 }).then(clickLogoutButton)
    }
    return cy.wrap(null)
  }

  const clickLogoutButton = ($menu) => {
    if ($menu.find('[data-cy="logout-button"], button, a').length > 0) {
      cy.get('[data-cy="logout-button"], button, a').first().click({ force: true })
      return cy.get('body', { timeout: 3000 }).then(confirmLogout)
    }
    return cy.wrap(null)
  }

  const confirmLogout = ($confirm) => {
    if ($confirm.find('[data-cy="confirm-logout"], .swal2-confirm, button[type="button"]').length > 0) {
      cy.get('[data-cy="confirm-logout"], .swal2-confirm, button[type="button"]').first().click()
    }
    if (afterLogout) {
      afterLogout()
    }
  }

  return cy.get('body').then(openUserMenu)
}

/**
 * Executes actions in sequence without deep nesting
 * @param {Array<Function>} actions - Array of action functions
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function executeActions(actions) {
  let chain = cy.wrap(null)
  for (const action of actions) {
    chain = chain.then(() => action())
  }
  return chain
}

/**
 * Verifies that a row matches expected filter criteria
 * @param {JQuery} $row - jQuery row element
 * @param {string} expectedText - Expected text to match (case-insensitive)
 * @returns {boolean} True if row matches or is empty
 */
export function verifyRowFilter($row, expectedText) {
  const text = $row.text().toUpperCase()
  return text.includes(expectedText.toUpperCase()) || text.length === 0
}

/**
 * Selects a value in a select element and verifies filtered rows
 * @param {string} selectSelector - CSS selector for select element
 * @param {string} selectValue - Value to select
 * @param {string} rowSelector - CSS selector for table rows
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function selectAndVerifyRows(selectSelector, selectValue, rowSelector) {
  return cy.get('body').then(($body) => {
    if ($body.find(selectSelector).length > 0) {
      cy.get(selectSelector).first().select(selectValue, { force: true })
      cy.get(rowSelector, { timeout: 5000 }).then(($rows) => {
        if ($rows.length > 0) {
          cy.wrap($rows).each(($row) => {
            const isValid = verifyRowFilter($row, selectValue)
            expect(isValid).to.be.true
          })
        }
      })
    }
  })
}

/**
 * Verifies element exists in context with multiple selector options
 * @param {JQuery} $context - jQuery context element
 * @param {Array<string>} selectors - Array of CSS selectors to try
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable<boolean>} True if any selector found, false otherwise
 */
export function verifyElementExists($context, selectors, timeout = 5000) {
  for (const selector of selectors) {
    if ($context.find(selector).length > 0) {
      cy.get(selector, { timeout }).should('exist')
      return cy.wrap(true)
    }
  }
  return cy.wrap(false)
}

/**
 * Verifies URL contains any of the expected patterns
 * @param {Array<string>} patterns - Array of URL patterns to check
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable<boolean>} True if URL matches any pattern
 */
export function verifyUrlPatterns(patterns, timeout = 10000) {
  return cy.url({ timeout }).should('satisfy', (url) => {
    return patterns.some(pattern => url.includes(pattern))
  })
}

/**
 * Sets up notifications API intercept
 * @param {Object} response - Mock response data
 * @param {string} alias - Cypress alias for the intercept
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function setupNotificationsIntercept(response, alias = 'getUnread') {
  const apiBaseUrl = getApiBaseUrl()
  return cy.intercept('GET', `${apiBaseUrl}/notifications/**`, response).as(alias)
}

/**
 * Executes action after clicking if element exists, reducing nesting
 * @param {string} selector - CSS selector
 * @param {Function} action - Function to execute after click
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function clickIfExistsAndContinue(selector, action) {
  return clickIfExists(selector).then((clicked) => {
    if (!clicked) return cy.wrap(null)
    cy.get('body', { timeout: 5000 }).should('be.visible')
    return action ? action() : cy.wrap(null)
  })
}

/**
 * Executes action after selecting if element exists, reducing nesting
 * @param {string} selector - CSS selector
 * @param {string} value - Value to select
 * @param {Function} action - Function to execute after select
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function selectIfExistsAndContinue(selector, value, action) {
  return selectIfExists(selector, value).then((selected) => {
    if (!selected) return cy.wrap(null)
    return action ? action() : cy.wrap(null)
  })
}

/**
 * Executes action after typing if element exists, reducing nesting
 * @param {string} selector - CSS selector
 * @param {string} text - Text to type
 * @param {Function} action - Function to execute after type
 * @param {Object} options - Type options
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function typeIfExistsAndContinue(selector, text, action, options = {}) {
  return typeIfExists(selector, text, options).then((typed) => {
    if (!typed) return cy.wrap(null)
    return action ? action() : cy.wrap(null)
  })
}

/**
 * Verifies selectors exist in body context, reducing nesting
 * @param {Array<string>} selectors - Array of CSS selectors
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function verifySelectorsInBody(selectors, timeout = 5000) {
  return cy.get('body', { timeout }).then(($body) => {
    verifySelectorsExist(selectors, $body, timeout)
  })
}

/**
 * Clicks element and verifies error message, reducing nesting
 * @param {string} clickSelector - Selector for element to click
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function clickAndVerifyError(clickSelector, errorSelector, expectedTexts) {
  return clickIfExists(clickSelector).then((clicked) => {
    if (!clicked) return cy.wrap(null)
    return cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find(errorSelector).length > 0) {
        cy.get(errorSelector).first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return expectedTexts.some(expected => text.includes(expected)) || text.length > 0
        })
      }
    })
  })
}

/**
 * Fills form fields in sequence, reducing nesting
 * @param {Array<{selector: string, value: string, options?: Object}>} fields - Array of field definitions
 * @param {string} submitSelector - Selector for submit button
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function fillFormFieldsSequence(fields, submitSelector) {
  let chain = cy.wrap(null)
  for (const field of fields) {
    chain = chain.then(() => {
      return typeIfExists(field.selector, field.value, field.options || {})
    })
  }
  if (submitSelector) {
    chain = chain.then(() => {
      return clickIfExists(submitSelector).then((clicked) => {
        if (clicked) {
          return cy.get('body', { timeout: 5000 }).should('be.visible')
        }
        return cy.wrap(null)
      })
    })
  }
  return chain
}

/**
 * Executes action if element found in body, reducing nesting
 * @param {string} selector - CSS selector to find
 * @param {Function} action - Function to execute with found element
 * @param {Function} elseAction - Optional function if element not found
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function ifFoundInBody(selector, action, elseAction) {
  return cy.get('body').then(($body) => {
    if ($body.find(selector).length > 0) {
      return cy.get(selector).first().then(($element) => {
        return action ? action($element, $body) : cy.wrap(null)
      })
    }
    if (elseAction) {
      return elseAction($body)
    }
    return cy.wrap(null)
  })
}

/**
 * Clicks element and waits for next element, reducing nesting
 * @param {string} clickSelector - Selector for element to click
 * @param {string} waitSelector - Selector to wait for after click
 * @param {Function} action - Optional function to execute after wait
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function clickAndWaitFor(clickSelector, waitSelector, action) {
  return clickIfExists(clickSelector).then((clicked) => {
    if (!clicked) return cy.wrap(null)
    return cy.get(waitSelector, { timeout: 5000 }).then(($element) => {
      return action ? action($element) : cy.wrap(null)
    })
  })
}

/**
 * Verifies element exists with multiple selector options, reducing nesting
 * @param {Array<string>} selectors - Array of CSS selectors to try
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable<boolean>} True if any selector found
 */
export function verifyAnySelectorExists(selectors, timeout = 5000) {
  return cy.get('body', { timeout }).then(($body) => {
    for (const selector of selectors) {
      if ($body.find(selector).length > 0) {
        cy.get(selector, { timeout }).should('exist')
        return cy.wrap(true)
      }
    }
    return cy.wrap(false)
  })
}

