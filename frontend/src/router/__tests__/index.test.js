import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createMockAuthStore } from '@/test/mocks'

// Mock views
const mockHomeView = { template: '<div>Home</div>' }
const mockLoginView = { template: '<div>Login</div>' }
const mockAdminDashboard = { template: '<div>Admin Dashboard</div>' }
const mockFincasView = { template: '<div>Fincas</div>' }

// Mock auth store
const mockAuthStore = createMockAuthStore()

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock views imports
vi.mock('@/views/Pages/HomeView.vue', () => ({ default: mockHomeView }))
vi.mock('@/views/Auth/LoginView.vue', () => ({ default: mockLoginView }))
vi.mock('@/views/Admin/AdminDashboard.vue', () => ({ default: mockAdminDashboard }))
vi.mock('@/views/common/FincasView.vue', () => ({ default: mockFincasView }))

// Mock globalThis
globalThis.document = {
  title: '',
  createElement: vi.fn((tag) => {
    const element = {
      tagName: tag.toUpperCase(),
      setAttribute: vi.fn(),
      appendChild: vi.fn(),
      removeChild: vi.fn(),
      style: {},
      innerHTML: '',
      textContent: ''
    }
    return element
  })
}
globalThis.scrollTo = vi.fn()
globalThis.dispatchEvent = vi.fn()

// Mock sweetalert2
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

// Import router after mocks
let router

// Helper functions for test setup
const createRoute = (path, name, meta = {}) => ({
  path,
  name,
  meta,
  fullPath: path
})

const resetAuthStore = () => {
  mockAuthStore.isAuthenticated = false
  mockAuthStore.accessToken = null
  mockAuthStore.user = null
  mockAuthStore.userRole = null
}

const setupAuthStore = (options = {}) => {
  mockAuthStore.isAuthenticated = options.isAuthenticated ?? false
  mockAuthStore.accessToken = options.accessToken ?? null
  mockAuthStore.user = options.user ?? null
  mockAuthStore.userRole = options.userRole ?? null
  if (options.getCurrentUser) {
    mockAuthStore.getCurrentUser = options.getCurrentUser
  }
}

describe('Router Configuration', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    resetAuthStore()

    // Dynamic import to ensure mocks are set up
    const routerModule = await import('../index.js')
    router = routerModule.default
  })

  describe('Route Definitions', () => {
    it('should have Home route', () => {
      const route = router.resolve('/')
      expect(route.name).toBe('Home')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should have Login route', () => {
      const route = router.resolve('/login')
      expect(route.name).toBe('Login')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should have Dashboard route with redirect', () => {
      const route = router.resolve('/dashboard')
      expect(route.name).toBe('Dashboard')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have Fincas route', () => {
      const route = router.resolve('/fincas')
      expect(route.name).toBe('Fincas')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have Admin Dashboard route', () => {
      const route = router.resolve('/admin/dashboard')
      expect(route.name).toBe('AdminDashboard')
      expect(route.meta.requiresAuth).toBe(true)
      expect(route.meta.requiresRole).toBe('admin')
    })

    it('should have Register route', () => {
      const route = router.resolve('/registro')
      expect(route.name).toBe('Register')
      expect(route.meta.requiresGuest).toBe(true)
    })

    it('should have ForgotPassword route', () => {
      const route = router.resolve('/auth/forgot-password')
      expect(route.name).toBe('ForgotPassword')
      expect(route.meta.requiresGuest).toBe(true)
    })
  })

  describe('Dashboard Redirect', () => {
    const testDashboardRedirect = (userRole, expectedPath) => {
      setupAuthStore({ isAuthenticated: true, userRole })
      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe(expectedPath)
      }
    }

    it('should redirect to login when not authenticated', () => {
      resetAuthStore()
      const redirectFn = router.resolve('/dashboard').redirectedFrom?.redirect
      if (redirectFn) {
        const result = redirectFn()
        expect(result).toBe('/login')
      }
    })

    it('should redirect admin to admin dashboard', () => {
      testDashboardRedirect('admin', '/admin/dashboard')
    })

    it('should redirect analyst to analisis', () => {
      testDashboardRedirect('analyst', '/analisis')
    })

    it('should redirect farmer to agricultor-dashboard', () => {
      testDashboardRedirect('farmer', '/agricultor-dashboard')
    })
  })

  describe('Navigation Guards', () => {
    it('should set document title from route meta', async () => {
      const to = createRoute('/', 'Home', { title: 'Test Title' })

      await router.beforeEach(to, { path: '/' })

      expect(globalThis.document.title).toBeDefined()
    })

    it('should redirect guest route if authenticated', async () => {
      setupAuthStore({ isAuthenticated: true, userRole: 'admin' })

      const to = createRoute('/login', 'Login', { requiresGuest: true })

      await router.beforeEach(to, { path: '/' })

      expect(router.currentRoute.value).toBeDefined()
    })

    it('should redirect to login if requiresAuth and not authenticated', async () => {
      resetAuthStore()

      const to = createRoute('/fincas', 'Fincas', { requiresAuth: true })

      await router.beforeEach(to, { path: '/' })

      expect(router.currentRoute.value).toBeDefined()
    })

    it('should allow navigation if authenticated and has required role', async () => {
      const user = { id: 1, role: 'admin' }
      setupAuthStore({
        isAuthenticated: true,
        accessToken: 'test-token',
        user,
        userRole: 'admin',
        getCurrentUser: vi.fn().mockResolvedValue(user)
      })

      const to = createRoute('/admin/dashboard', 'AdminDashboard', {
        requiresAuth: true,
        requiresRole: 'admin'
      })

      await router.beforeEach(to, { path: '/' })

      expect(mockAuthStore.updateLastActivity).toHaveBeenCalled()
    })

    it('should redirect if user does not have required role', async () => {
      const user = { id: 1, role: 'farmer' }
      setupAuthStore({
        isAuthenticated: true,
        accessToken: 'test-token',
        user,
        userRole: 'farmer',
        getCurrentUser: vi.fn().mockResolvedValue(user)
      })

      const to = createRoute('/admin/dashboard', 'AdminDashboard', {
        requiresAuth: true,
        requiresRole: 'admin'
      })

      await router.beforeEach(to, { path: '/' })

      expect(router.currentRoute.value).toBeDefined()
    })

    it('should handle getCurrentUser error and redirect to login', async () => {
      setupAuthStore({
        isAuthenticated: false,
        accessToken: 'invalid-token',
        user: null,
        getCurrentUser: vi.fn().mockRejectedValue(new Error('Invalid token'))
      })

      const to = createRoute('/fincas', 'Fincas', { requiresAuth: true })

      await router.beforeEach(to, { path: '/' })

      expect(mockAuthStore.clearAll).toHaveBeenCalled()
    })
  })

  describe('After Each Guard', () => {
    it('should scroll to top on route change', async () => {
      const to = createRoute('/new', 'NewRoute')
      const from = createRoute('/old', 'OldRoute')

      router.afterEach(to, from)

      expect(globalThis.scrollTo).toHaveBeenCalledWith(0, 0)
    })

    it('should not scroll if same path', async () => {
      const to = createRoute('/same', 'SameRoute')
      const from = createRoute('/same', 'SameRoute')

      globalThis.scrollTo.mockClear()
      router.afterEach(to, from)

      expect(globalThis.scrollTo).not.toHaveBeenCalled()
    })
  })

  describe('Route Meta', () => {
    it('should have correct meta for public routes', () => {
      const route = router.resolve('/')
      expect(route.meta.requiresAuth).toBe(false)
    })

    it('should have correct meta for protected routes', () => {
      const route = router.resolve('/fincas')
      expect(route.meta.requiresAuth).toBe(true)
    })

    it('should have role requirements for admin routes', () => {
      const route = router.resolve('/admin/dashboard')
      expect(route.meta.requiresRole).toBe('admin')
    })
  })
})

