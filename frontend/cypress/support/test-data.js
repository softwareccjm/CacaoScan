/**
 * Test Data Constants for Cypress E2E Tests
 * This file centralizes test credentials and data to avoid hard-coded
 * passwords in test files, addressing security concerns from static analysis tools.
 * 
 * NOTE: These are test-only credentials and should NEVER be used in production.
 */

// Test user credentials
export const TEST_CREDENTIALS = {
  // Standard test password for most tests
  testPassword: 'Password123!',
  
  // Password for password confirmation tests (different from testPassword)
  differentPassword: 'DifferentPassword123!',
  
  // Strong password for validation tests
  strongPassword: 'StrongPassword123!',
  
  // New password for password change tests
  newPassword: 'NewPassword123!',
  
  // Weak passwords for validation tests
  weakPasswords: ['123', 'password', '12345678'],
  
  // Login credentials
  login: {
    email: 'test@example.com',
    password: 'password123'
  }
}

// Test user data
export const TEST_USERS = {
  farmer: {
    firstName: 'Juan',
    lastName: 'Pérez',
    email: 'juan.perez@test.com',
    password: TEST_CREDENTIALS.testPassword,
    confirmPassword: TEST_CREDENTIALS.testPassword,
    role: 'farmer'
  },
  
  analyst: {
    firstName: 'Ana',
    lastName: 'García',
    email: 'ana.garcia@test.com',
    password: TEST_CREDENTIALS.testPassword,
    confirmPassword: TEST_CREDENTIALS.testPassword,
    role: 'analyst'
  }
}

// Export for convenience
export default {
  TEST_CREDENTIALS,
  TEST_USERS
}
