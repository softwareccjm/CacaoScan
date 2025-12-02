/**
 * Unit tests for useAudit composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAudit } from '../useAudit.js'
import { useNotificationStore } from '@/stores/notifications'
import * as auditApi from '@/services/auditApi'

// Mock dependencies
const mockNotificationStore = {
  addNotification: vi.fn()
}

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => mockNotificationStore
}))

vi.mock('@/services/auditApi', () => ({
  validateDateFilters: vi.fn(() => ({ isValid: true, errors: [] })),
  getActivityLogs: vi.fn(),
  getLoginHistory: vi.fn(),
  getAuditStats: vi.fn()
}))

vi.mock('../useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDate: vi.fn((date) => date),
    formatDateTime: vi.fn((date) => date)
  })
}))

vi.mock('../useAuditHelpers', () => ({
  useAuditHelpers: () => ({
    formatActivityLog: vi.fn((log) => log),
    formatLoginRecord: vi.fn((record) => record)
  })
}))

describe('useAudit', () => {
  let audit

  beforeEach(() => {
    vi.clearAllMocks()
    audit = useAudit()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(audit.loading.value).toBe(false)
      expect(audit.error.value).toBe(null)
      expect(audit.activityLogs.value).toEqual([])
      expect(audit.loginHistory.value).toEqual([])
    })
  })

  describe('loadActivityLogs', () => {
    it('should load activity logs successfully', async () => {
      const mockLogs = [{ id: 1, accion: 'login' }]
      auditApi.getActivityLogs.mockResolvedValue({
        results: mockLogs,
        count: 1
      })

      const result = await audit.loadActivityLogs()

      expect(auditApi.getActivityLogs).toHaveBeenCalled()
      expect(audit.activityLogs.value).toHaveLength(1)
      expect(audit.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const error = new Error('Network error')
      auditApi.getActivityLogs.mockRejectedValue(error)

      await expect(audit.loadActivityLogs()).rejects.toThrow()

      expect(audit.error.value).toBeTruthy()
      expect(audit.loading.value).toBe(false)
    })
  })

  describe('loadLoginHistory', () => {
    it('should load login history successfully', async () => {
      const mockHistory = [{ id: 1, exitoso: true }]
      auditApi.getLoginHistory.mockResolvedValue({
        results: mockHistory,
        count: 1
      })

      const result = await audit.loadLoginHistory()

      expect(auditApi.getLoginHistory).toHaveBeenCalled()
      expect(audit.loginHistory.value).toHaveLength(1)
    })
  })

  describe('loadStats', () => {
    it('should load audit stats', async () => {
      const mockStats = {
        total_activities: 100,
        total_logins: 50
      }
      auditApi.getAuditStats.mockResolvedValue(mockStats)

      await audit.loadStats()

      expect(auditApi.getAuditStats).toHaveBeenCalled()
      expect(audit.stats.value).toEqual(mockStats)
    })
  })

  describe('computed properties', () => {
    it('should compute hasActivityFilters', () => {
      audit.activityFilters.usuario = 'test'
      
      expect(audit.hasActivityFilters.value).toBe(true)
      
      audit.activityFilters.usuario = ''
      expect(audit.hasActivityFilters.value).toBe(false)
    })
  })
})

