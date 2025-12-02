/**
 * Unit tests for useDashboardMetrics composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDashboardMetrics } from '../useDashboardMetrics.js'

// Mock useDateFormatting
vi.mock('../useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDate: vi.fn((date) => date),
    formatNumber: vi.fn((num) => num.toString())
  })
}))

describe('useDashboardMetrics', () => {
  let metrics

  beforeEach(() => {
    metrics = useDashboardMetrics()
  })

  describe('formatMetricValue', () => {
    it('should format number value', () => {
      const result = metrics.formatMetricValue(1000)
      
      expect(result).toBeTruthy()
    })

    it('should format large numbers with abbreviations', () => {
      const result = metrics.formatMetricValue(1500000)
      
      expect(result).toContain('M')
    })

    it('should format thousands with K', () => {
      const result = metrics.formatMetricValue(5000)
      
      expect(result).toContain('K')
    })

    it('should return N/A for null', () => {
      const result = metrics.formatMetricValue(null)
      
      expect(result).toBe('N/A')
    })
  })

  describe('formatPercentageChange', () => {
    it('should format positive change', () => {
      const result = metrics.formatPercentageChange(10.5)
      
      expect(result).toContain('+')
      expect(result).toContain('%')
    })

    it('should format negative change', () => {
      const result = metrics.formatPercentageChange(-5.2)
      
      expect(result).toContain('%')
    })
  })

  describe('getChangeClass', () => {
    it('should return positive for positive change', () => {
      expect(metrics.getChangeClass(10)).toBe('positive')
    })

    it('should return negative for negative change', () => {
      expect(metrics.getChangeClass(-5)).toBe('negative')
    })

    it('should return neutral for zero', () => {
      expect(metrics.getChangeClass(0)).toBe('neutral')
    })
  })

  describe('getChangeIcon', () => {
    it('should return arrow-up for positive change', () => {
      expect(metrics.getChangeIcon(10)).toContain('arrow-up')
    })

    it('should return arrow-down for negative change', () => {
      expect(metrics.getChangeIcon(-5)).toContain('arrow-down')
    })
  })

  describe('calculatePercentageChange', () => {
    it('should calculate percentage change', () => {
      const result = metrics.calculatePercentageChange(110, 100)
      
      expect(result).toBe(10)
    })

    it('should handle zero previous value', () => {
      const result = metrics.calculatePercentageChange(10, 0)
      
      expect(result).toBe(100)
    })
  })
})

