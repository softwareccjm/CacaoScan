/**
 * Unit tests for useImageStats composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useImageStats } from '../useImageStats.js'
import { useAuthStore } from '@/stores/auth'
import axios from '@/services/api'

// Mock dependencies
const mockAuthStore = {
  isAuthenticated: true
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('useImageStats', () => {
  let imageStats

  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.isAuthenticated = true
    imageStats = useImageStats()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(imageStats.stats.value).toBe(null)
      expect(imageStats.loading.value).toBe(false)
      expect(imageStats.error.value).toBe(null)
    })
  })

  describe('fetchStats', () => {
    it('should fetch stats successfully', async () => {
      const mockStats = {
        total_images: 100,
        processed_images: 80,
        processing_rate: 0.8
      }
      axios.get.mockResolvedValue({ data: mockStats })

      await imageStats.fetchStats()

      expect(axios.get).toHaveBeenCalledWith('/api/v1/images/stats/')
      expect(imageStats.stats.value).toEqual(mockStats)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should handle 500 error gracefully', async () => {
      const error = {
        response: { status: 500 }
      }
      axios.get.mockRejectedValue(error)

      await imageStats.fetchStats()

      expect(imageStats.stats.value).toEqual({
        total_images: 0,
        processed_images: 0,
        processing_rate: 0,
        average_confidence: 0,
        average_dimensions: {},
        region_stats: [],
        top_fincas: []
      })
      expect(imageStats.error.value).toBe(null)
    })

    it('should require authentication', async () => {
      mockAuthStore.isAuthenticated = false

      await imageStats.fetchStats()

      expect(imageStats.error.value).toBe('Usuario no autenticado')
      expect(axios.get).not.toHaveBeenCalled()
    })
  })

  describe('fetchImages', () => {
    it('should fetch images successfully', async () => {
      const mockResponse = {
        data: {
          results: [{ id: 1 }],
          count: 1
        }
      }
      axios.get.mockResolvedValue(mockResponse)

      const result = await imageStats.fetchImages(1)

      expect(axios.get).toHaveBeenCalled()
      expect(result.count).toBe(1)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should return empty result if not authenticated', async () => {
      mockAuthStore.isAuthenticated = false

      const result = await imageStats.fetchImages()

      expect(result).toEqual({ results: [], count: 0, totalPages: 0 })
    })
  })
})

