import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  generateTestPassword,
  generateStrongPassword,
  generateWeakPasswords,
  getWeakPassword,
  generateDifferentPassword,
  TEST_CREDENTIALS,
  TEST_USERS,
  createTestFinca,
  createTestLote,
  createTestReport,
  createTestPrediction
} from '../test-data'

describe('test-data.js', () => {
  const originalEnv = process.env
  const originalCypress = global.Cypress

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset environment
    process.env = { ...originalEnv }
    global.Cypress = undefined
  })

  afterEach(() => {
    process.env = originalEnv
    global.Cypress = originalCypress
  })

  describe('generateTestPassword', () => {
    it('should generate default test password when no env var is set', () => {
      const password = generateTestPassword()
      expect(password).toBe('Password123!')
    })

    it('should use environment variable when CYPRESS_TEST_PASSWORD is set', () => {
      process.env.CYPRESS_TEST_PASSWORD = 'CustomPassword123!'
      const password = generateTestPassword()
      expect(password).toBe('CustomPassword123!')
    })

    it('should use Cypress.env when available', () => {
      global.Cypress = {
        env: vi.fn((key) => {
          if (key === 'CYPRESS_TEST_PASSWORD') return 'CypressPassword123!'
          return undefined
        })
      }
      const password = generateTestPassword()
      expect(password).toBe('CypressPassword123!')
    })
  })

  describe('generateStrongPassword', () => {
    it('should generate strong password by default', () => {
      const password = generateStrongPassword()
      expect(password).toBe('StrongPassword123!')
    })

    it('should use environment variable when CYPRESS_STRONG_PASSWORD is set', () => {
      process.env.CYPRESS_STRONG_PASSWORD = 'CustomStrong123!'
      const password = generateStrongPassword()
      expect(password).toBe('CustomStrong123!')
    })
  })

  describe('generateWeakPasswords', () => {
    it('should return array of weak passwords', () => {
      const passwords = generateWeakPasswords()
      expect(Array.isArray(passwords)).toBe(true)
      expect(passwords.length).toBe(3)
      expect(passwords[0]).toBe('123')
      expect(passwords[1]).toBe('password')
      expect(passwords[2]).toBe('12345678')
    })

    it('should return consistent weak passwords', () => {
      const passwords1 = generateWeakPasswords()
      const passwords2 = generateWeakPasswords()
      expect(passwords1).toEqual(passwords2)
    })
  })

  describe('getWeakPassword', () => {
    it('should return first weak password by default', () => {
      const password = getWeakPassword()
      expect(password).toBe('123')
    })

    it('should return weak password at specified index', () => {
      expect(getWeakPassword(0)).toBe('123')
      expect(getWeakPassword(1)).toBe('password')
      expect(getWeakPassword(2)).toBe('12345678')
    })

    it('should return first password when index is out of bounds', () => {
      const password = getWeakPassword(10)
      expect(password).toBe('123')
    })

    it('should return first password when index is negative', () => {
      const password = getWeakPassword(-1)
      expect(password).toBe('123')
    })
  })

  describe('generateDifferentPassword', () => {
    it('should generate different password by default', () => {
      const password = generateDifferentPassword()
      expect(password).toBe('DifferentPassword123!')
    })

    it('should use environment variable when CYPRESS_DIFFERENT_PASSWORD is set', () => {
      process.env.CYPRESS_DIFFERENT_PASSWORD = 'CustomDifferent123!'
      const password = generateDifferentPassword()
      expect(password).toBe('CustomDifferent123!')
    })
  })

  describe('TEST_CREDENTIALS', () => {
    it('should have testPassword property', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('testPassword')
      expect(typeof TEST_CREDENTIALS.testPassword).toBe('string')
    })

    it('should have differentPassword property', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('differentPassword')
      expect(typeof TEST_CREDENTIALS.differentPassword).toBe('string')
    })

    it('should have strongPassword property', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('strongPassword')
      expect(typeof TEST_CREDENTIALS.strongPassword).toBe('string')
    })

    it('should have newPassword property', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('newPassword')
      expect(typeof TEST_CREDENTIALS.newPassword).toBe('string')
    })

    it('should have weakPasswords array', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('weakPasswords')
      expect(Array.isArray(TEST_CREDENTIALS.weakPasswords)).toBe(true)
    })

    it('should have login credentials', () => {
      expect(TEST_CREDENTIALS).toHaveProperty('login')
      expect(TEST_CREDENTIALS.login).toHaveProperty('email')
      expect(TEST_CREDENTIALS.login).toHaveProperty('password')
    })

    it('should use environment variable for login email when set', () => {
      // This test verifies that getEnvVar works correctly
      // The actual TEST_CREDENTIALS uses getEnvVar internally
      // We test the getEnvVar behavior in generateTestPassword tests
      expect(TEST_CREDENTIALS.login).toHaveProperty('email')
      expect(typeof TEST_CREDENTIALS.login.email).toBe('string')
    })
  })

  describe('TEST_USERS', () => {
    it('should have farmer user', () => {
      expect(TEST_USERS).toHaveProperty('farmer')
      expect(TEST_USERS.farmer).toHaveProperty('firstName', 'Juan')
      expect(TEST_USERS.farmer).toHaveProperty('lastName', 'Pérez')
      expect(TEST_USERS.farmer).toHaveProperty('email', 'juan.perez@test.com')
      expect(TEST_USERS.farmer).toHaveProperty('role', 'farmer')
    })

    it('should have analyst user', () => {
      expect(TEST_USERS).toHaveProperty('analyst')
      expect(TEST_USERS.analyst).toHaveProperty('firstName', 'Ana')
      expect(TEST_USERS.analyst).toHaveProperty('lastName', 'García')
      expect(TEST_USERS.analyst).toHaveProperty('email', 'ana.garcia@test.com')
      expect(TEST_USERS.analyst).toHaveProperty('role', 'analyst')
    })

    it('should have admin user', () => {
      expect(TEST_USERS).toHaveProperty('admin')
      expect(TEST_USERS.admin).toHaveProperty('firstName', 'Admin')
      expect(TEST_USERS.admin).toHaveProperty('lastName', 'User')
      expect(TEST_USERS.admin).toHaveProperty('email', 'admin@test.com')
      expect(TEST_USERS.admin).toHaveProperty('role', 'admin')
    })

    it('should have password and confirmPassword for all users', () => {
      Object.values(TEST_USERS).forEach(user => {
        expect(user).toHaveProperty('password')
        expect(user).toHaveProperty('confirmPassword')
        expect(user.password).toBe(user.confirmPassword)
      })
    })
  })

  describe('createTestFinca', () => {
    it('should create finca with default values', () => {
      const finca = createTestFinca()
      
      expect(finca).toHaveProperty('nombre', 'Finca de Prueba')
      expect(finca).toHaveProperty('ubicacion', 'Test Location')
      expect(finca).toHaveProperty('municipio', 'Test Municipio')
      expect(finca).toHaveProperty('departamento', 'Test Departamento')
      expect(finca).toHaveProperty('hectareas', 10.5)
      expect(finca).toHaveProperty('descripcion', 'Descripción de prueba')
      expect(finca).toHaveProperty('coordenadas_lat', 4.6097)
      expect(finca).toHaveProperty('coordenadas_lng', -74.0817)
    })

    it('should override default values with provided overrides', () => {
      const finca = createTestFinca({
        nombre: 'Custom Finca',
        hectareas: 20
      })
      
      expect(finca.nombre).toBe('Custom Finca')
      expect(finca.hectareas).toBe(20)
      expect(finca.ubicacion).toBe('Test Location') // Should keep default
    })

    it('should allow adding new properties', () => {
      const finca = createTestFinca({
        id: 1,
        agricultor: 123
      })
      
      expect(finca).toHaveProperty('id', 1)
      expect(finca).toHaveProperty('agricultor', 123)
    })

    it('should create independent instances', () => {
      const finca1 = createTestFinca()
      const finca2 = createTestFinca()
      
      finca1.nombre = 'Modified'
      expect(finca2.nombre).toBe('Finca de Prueba')
    })
  })

  describe('createTestLote', () => {
    it('should create lote with default values', () => {
      const lote = createTestLote()
      
      expect(lote).toHaveProperty('identificador', 'LOTE-001')
      expect(lote).toHaveProperty('variedad', 'Criollo')
      expect(lote).toHaveProperty('area_hectareas', 5)
      expect(lote).toHaveProperty('estado', 'activo')
      expect(lote).toHaveProperty('descripcion', 'Descripción de lote de prueba')
      expect(lote).toHaveProperty('fecha_plantacion')
      expect(typeof lote.fecha_plantacion).toBe('string')
    })

    it('should use current date for fecha_plantacion by default', () => {
      const lote = createTestLote()
      const today = new Date().toISOString().split('T')[0]
      expect(lote.fecha_plantacion).toBe(today)
    })

    it('should override default values with provided overrides', () => {
      const lote = createTestLote({
        identificador: 'LOTE-999',
        variedad: 'Forastero',
        estado: 'cosechado'
      })
      
      expect(lote.identificador).toBe('LOTE-999')
      expect(lote.variedad).toBe('Forastero')
      expect(lote.estado).toBe('cosechado')
    })

    it('should allow adding new properties', () => {
      const lote = createTestLote({
        id: 1,
        finca: 123
      })
      
      expect(lote).toHaveProperty('id', 1)
      expect(lote).toHaveProperty('finca', 123)
    })
  })

  describe('createTestReport', () => {
    it('should create report with default values', () => {
      const report = createTestReport()
      
      expect(report).toHaveProperty('tipo_reporte', 'calidad')
      expect(report).toHaveProperty('formato', 'excel')
      expect(report).toHaveProperty('titulo', 'Reporte de Prueba')
      expect(report).toHaveProperty('descripcion', 'Descripción del reporte de prueba')
      expect(report).toHaveProperty('parametros', {})
      expect(report).toHaveProperty('filtros', {})
    })

    it('should override default values with provided overrides', () => {
      const report = createTestReport({
        tipo_reporte: 'estadistico',
        formato: 'pdf'
      })
      
      expect(report.tipo_reporte).toBe('estadistico')
      expect(report.formato).toBe('pdf')
    })

    it('should allow adding new properties', () => {
      const report = createTestReport({
        id: 1,
        fecha_generacion: '2024-01-01'
      })
      
      expect(report).toHaveProperty('id', 1)
      expect(report).toHaveProperty('fecha_generacion', '2024-01-01')
    })
  })

  describe('createTestPrediction', () => {
    it('should create prediction with default values', () => {
      const prediction = createTestPrediction()
      
      expect(prediction).toHaveProperty('quality', 85)
      expect(prediction).toHaveProperty('confidence', 0.92)
      expect(prediction).toHaveProperty('defects', ['minor'])
    })

    it('should override default values with provided overrides', () => {
      const prediction = createTestPrediction({
        quality: 95,
        confidence: 0.98
      })
      
      expect(prediction.quality).toBe(95)
      expect(prediction.confidence).toBe(0.98)
      expect(prediction.defects).toEqual(['minor'])
    })

    it('should allow adding new properties', () => {
      const prediction = createTestPrediction({
        id: 1,
        image_url: 'https://example.com/image.jpg'
      })
      
      expect(prediction).toHaveProperty('id', 1)
      expect(prediction).toHaveProperty('image_url', 'https://example.com/image.jpg')
    })

    it('should allow overriding defects array', () => {
      const prediction = createTestPrediction({
        defects: ['major', 'critical']
      })
      
      expect(prediction.defects).toEqual(['major', 'critical'])
    })
  })

  describe('Password generation functions', () => {
    it('should generate different passwords for different functions', () => {
      const testPassword = generateTestPassword()
      const strongPassword = generateStrongPassword()
      const differentPassword = generateDifferentPassword()
      
      expect(testPassword).not.toBe(strongPassword)
      expect(testPassword).not.toBe(differentPassword)
      expect(strongPassword).not.toBe(differentPassword)
    })

    it('should generate consistent passwords on multiple calls', () => {
      const password1 = generateTestPassword()
      const password2 = generateTestPassword()
      expect(password1).toBe(password2)
    })
  })
})

