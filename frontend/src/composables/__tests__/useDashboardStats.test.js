/**
 * Unit tests for useDashboardStats composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDashboardStats } from '../useDashboardStats.js'
import dashboardStatsService from '@/services/dashboardStatsService'

// Mock dashboardStatsService
vi.mock('@/services/dashboardStatsService', () => ({
  default: {
    getGeneralStats: vi.fn(),
    getActivityData: vi.fn(),
    getQualityDistribution: vi.fn(),
    getRegionStats: vi.fn(),
    getTrendsData: vi.fn(),
    getActiveUsers: vi.fn(),
    getTopFincas: vi.fn(),
    getRecentUsers: vi.fn(),
    getRecentActivities: vi.fn(),
    getSystemAlerts: vi.fn(),
    getReportStats: vi.fn()
  }
}))

describe('useDashboardStats', () => {
  let stats

  beforeEach(() => {
    vi.clearAllMocks()
    stats = useDashboardStats()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(stats.loading.value).toBe(false)
      expect(stats.error.value).toBe(null)
      expect(stats.stats.value).toEqual({})
      expect(stats.activityData.value).toEqual({ labels: [], datasets: [] })
    })
  })

  describe('loadGeneralStats', () => {
    it('should load general stats successfully', async () => {
      const mockStats = {
        data: {
          total_users: 100,
          total_fincas: 50,
          total_analyses: 200
        }
      }
      dashboardStatsService.getGeneralStats.mockResolvedValue(mockStats)

      await stats.loadGeneralStats()

      expect(dashboardStatsService.getGeneralStats).toHaveBeenCalled()
      expect(stats.stats.value).toEqual(mockStats.data)
      expect(stats.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const error = new Error('Network error')
      dashboardStatsService.getGeneralStats.mockRejectedValue(error)

      await stats.loadGeneralStats()

      expect(stats.error.value).toBe('Network error')
      expect(stats.loading.value).toBe(false)
    })
  })

  describe('mainStats computed', () => {
    it('should compute main stats correctly', () => {
      stats.stats.value = {
        total_users: 100,
        total_fincas: 50,
        total_analyses: 200,
        avg_quality: 85
      }

      const mainStats = stats.mainStats.value

      expect(mainStats).toHaveLength(4)
      expect(mainStats[0].value).toBe(100)
      expect(mainStats[1].value).toBe(50)
    })
  })
})

