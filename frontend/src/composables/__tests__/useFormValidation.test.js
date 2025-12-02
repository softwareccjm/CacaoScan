/**
 * Unit tests for useFormValidation composable
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useFormValidation } from '../useFormValidation.js'

describe('useFormValidation', () => {
  let validation

  beforeEach(() => {
    validation = useFormValidation()
  })

  describe('validation functions', () => {
    it('should validate email correctly', () => {
      expect(validation.isValidEmail('test@example.com')).toBe(true)
      expect(validation.isValidEmail('invalid')).toBe(false)
      expect(validation.isValidEmail('invalid@')).toBe(false)
      expect(validation.isValidEmail('@example.com')).toBe(false)
    })

    it('should validate phone correctly', () => {
      expect(validation.isValidPhone('+573001234567')).toBe(true)
      expect(validation.isValidPhone('3001234567')).toBe(true)
      expect(validation.isValidPhone('300')).toBe(false)
      expect(validation.isValidPhone('')).toBe(true) // Optional
    })

    it('should validate document correctly', () => {
      expect(validation.isValidDocument('1234567890')).toBe(true)
      expect(validation.isValidDocument('12345')).toBe(false) // Too short
      expect(validation.isValidDocument('123456789012345')).toBe(false) // Too long
      expect(validation.isValidDocument('abc123')).toBe(false) // Not numeric
    })

    it('should validate birthdate correctly', () => {
      const today = new Date()
      const validBirthdate = new Date(today.getFullYear() - 25, today.getMonth(), today.getDate())
      
      expect(validation.isValidBirthdate(validBirthdate.toISOString().split('T')[0])).toBe(true)
      
      const tooYoung = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate())
      expect(validation.isValidBirthdate(tooYoung.toISOString().split('T')[0])).toBe(false)
      
      expect(validation.isValidBirthdate('')).toBe(true) // Optional
    })

    it('should validate password correctly', () => {
      const result = validation.validatePassword('Password123')
      
      expect(result.isValid).toBe(true)
      expect(result.length).toBe(true)
      expect(result.uppercase).toBe(true)
      expect(result.lowercase).toBe(true)
      expect(result.number).toBe(true)
    })

    it('should reject weak password', () => {
      const result = validation.validatePassword('weak')
      
      expect(result.isValid).toBe(false)
      expect(result.length).toBe(false)
    })
  })

  describe('error management', () => {
    it('should set error for field', () => {
      validation.setError('email', 'Email inválido')
      
      expect(validation.errors.email).toBe('Email inválido')
    })

    it('should remove error for field', () => {
      validation.setError('email', 'Error')
      validation.removeError('email')
      
      expect(validation.errors.email).toBeUndefined()
    })

    it('should clear all errors', () => {
      validation.setError('email', 'Error 1')
      validation.setError('password', 'Error 2')
      validation.clearErrors()
      
      expect(Object.keys(validation.errors).length).toBe(0)
    })

    it('should check if has errors', () => {
      expect(validation.hasErrors()).toBe(false)
      
      validation.setError('email', 'Error')
      expect(validation.hasErrors()).toBe(true)
    })
  })

  describe('form state', () => {
    it('should have initial form state', () => {
      expect(validation.formState.dirty).toBe(false)
      expect(validation.formState.valid).toBe(true)
      expect(validation.formState.touched).toEqual({})
    })

    it('should mark field as touched', () => {
      validation.markFieldTouched('email')
      
      expect(validation.formState.touched.email).toBe(true)
    })

    it('should mark form as dirty', () => {
      validation.markFormDirty()
      
      expect(validation.formState.dirty).toBe(true)
    })
  })

  describe('mapServerErrors', () => {
    it('should map server errors to form fields', () => {
      const serverErrors = {
        email: 'Email inválido',
        password: ['Contraseña muy débil']
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.email).toBe('Email inválido')
      expect(validation.errors.password).toBe('Contraseña muy débil')
    })

    it('should skip non-field errors', () => {
      const serverErrors = {
        error: 'General error',
        status: 400,
        email: 'Email error'
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.error).toBeUndefined()
      expect(validation.errors.status).toBeUndefined()
      expect(validation.errors.email).toBe('Email error')
    })

    it('should use field mapping', () => {
      const serverErrors = {
        email_address: 'Email error'
      }
      const fieldMapping = {
        email_address: 'email'
      }
      
      validation.mapServerErrors(serverErrors, fieldMapping)
      
      expect(validation.errors.email).toBe('Email error')
    })

    it('should handle empty server errors', () => {
      validation.mapServerErrors({})
      expect(Object.keys(validation.errors).length).toBe(0)
    })
  })
})

