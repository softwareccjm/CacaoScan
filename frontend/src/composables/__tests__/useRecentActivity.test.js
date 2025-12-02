/**
 * Unit tests for useRecentActivity composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useRecentActivity } from '../useRecentActivity.js'

describe('useRecentActivity', () => {
  describe('initial state', () => {
    it('should have initial state', () => {
      const activity = useRecentActivity()
      
      expect(activity.activities.value).toEqual([])
      expect(activity.loading.value).toBe(false)
      expect(activity.error.value).toBe(null)
    })

    it('should accept custom limit', () => {
      const activity = useRecentActivity({ limit: 5 })
      
      expect(activity.recentActivities.value).toBeDefined()
    })
  })

  describe('fetchActivities', () => {
    it('should fetch activities successfully', async () => {
      const fetchFn = vi.fn().mockResolvedValue([
        { id: 1, action: 'upload' },
        { id: 2, action: 'delete' }
      ])
      const activity = useRecentActivity({ fetchFn })

      await activity.fetchActivities()

      expect(fetchFn).toHaveBeenCalled()
      expect(activity.activities.value).toHaveLength(2)
      expect(activity.loading.value).toBe(false)
    })

    it('should handle error', async () => {
      const fetchFn = vi.fn().mockRejectedValue(new Error('Network error'))
      const activity = useRecentActivity({ fetchFn })

      await expect(activity.fetchActivities()).rejects.toThrow()

      expect(activity.error.value).toBeTruthy()
      expect(activity.loading.value).toBe(false)
    })

    it('should throw error when fetchFn not provided', async () => {
      const activity = useRecentActivity()

      await expect(activity.fetchActivities()).rejects.toThrow('fetchFn is required')
    })
  })

  describe('addActivity', () => {
    it('should add activity to beginning', () => {
      const activity = useRecentActivity()
      const newActivity = { id: 1, action: 'test' }

      activity.addActivity(newActivity)

      expect(activity.activities.value[0]).toEqual(newActivity)
    })

    it('should limit activities to max', () => {
      const activity = useRecentActivity({ limit: 5 })
      
      // Add more than limit * 2
      for (let i = 0; i < 15; i++) {
        activity.addActivity({ id: i, action: 'test' })
      }

      expect(activity.activities.value.length).toBeLessThanOrEqual(10) // limit * 2
    })
  })

  describe('removeActivity', () => {
    it('should remove activity by id', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, action: 'test1' },
        { id: 2, action: 'test2' }
      ]

      activity.removeActivity(1)

      expect(activity.activities.value).toHaveLength(1)
      expect(activity.activities.value[0].id).toBe(2)
    })
  })

  describe('clearActivities', () => {
    it('should clear all activities', () => {
      const activity = useRecentActivity()
      activity.activities.value = [
        { id: 1, action: 'test1' },
        { id: 2, action: 'test2' }
      ]

      activity.clearActivities()

      expect(activity.activities.value).toHaveLength(0)
      expect(activity.error.value).toBe(null)
    })
  })

  describe('recentActivities computed', () => {
    it('should limit to specified limit', () => {
      const activity = useRecentActivity({ limit: 2 })
      activity.activities.value = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]

      expect(activity.recentActivities.value).toHaveLength(2)
    })
  })
})

