/**
 * Test utilities shared between unit tests and E2E tests
 */

/**
 * Generates a secure password for testing
 * @returns {string} Generated password
 */
export function generatePassword() {
  return `Pass!${Date.now()}-${Math.random().toString(36).slice(2)}`
}

