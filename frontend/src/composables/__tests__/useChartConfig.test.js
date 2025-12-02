/**
 * Unit tests for useChartConfig composable
 */

import { describe, it, expect, vi } from 'vitest'
import { useChartConfig, DEFAULT_CHART_COLORS, CHART_THEMES } from '../useChartConfig.js'

describe('useChartConfig', () => {
  describe('constants', () => {
    it('should export DEFAULT_CHART_COLORS', () => {
      expect(DEFAULT_CHART_COLORS).toBeDefined()
      expect(Array.isArray(DEFAULT_CHART_COLORS)).toBe(true)
      expect(DEFAULT_CHART_COLORS.length).toBeGreaterThan(0)
    })

    it('should export CHART_THEMES', () => {
      expect(CHART_THEMES).toBeDefined()
      expect(CHART_THEMES.light).toBeDefined()
      expect(CHART_THEMES.dark).toBeDefined()
    })
  })

  describe('useChartConfig', () => {
    it('should create chart config with default options', () => {
      const config = useChartConfig()
      
      expect(config.getDefaultOptions.value).toBeDefined()
      expect(config.colors).toBeDefined()
    })

    it('should use light theme by default', () => {
      const config = useChartConfig()
      
      expect(config.themeColors.value).toEqual(CHART_THEMES.light)
    })

    it('should use dark theme when specified', () => {
      const config = useChartConfig({ theme: 'dark' })
      
      expect(config.themeColors.value).toEqual(CHART_THEMES.dark)
    })

    it('should accept custom colors', () => {
      const customColors = ['#ff0000', '#00ff00']
      const config = useChartConfig({ colors: customColors })
      
      expect(config.colors).toEqual(customColors)
    })

    it('should create default options for line chart', () => {
      const config = useChartConfig({ type: 'line' })
      const options = config.getDefaultOptions.value
      
      expect(options.responsive).toBe(true)
      expect(options.plugins).toBeDefined()
      expect(options.scales).toBeDefined()
    })

    it('should process chart data correctly', () => {
      const config = useChartConfig()
      const chartData = {
        labels: ['A', 'B'],
        datasets: [{
          label: 'Dataset 1',
          data: [1, 2]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(processed.datasets[0].backgroundColor).toBeDefined()
    })

    it('should apply colors to pie chart', () => {
      const config = useChartConfig({ type: 'pie' })
      const chartData = {
        labels: ['A', 'B', 'C'],
        datasets: [{
          data: [1, 2, 3]
        }]
      }
      
      const processed = config.processChartData(chartData)
      
      expect(Array.isArray(processed.datasets[0].backgroundColor)).toBe(true)
    })

    it('should create gradient', () => {
      const config = useChartConfig()
      const mockAddColorStop = vi.fn()
      const mockGradient = {
        addColorStop: mockAddColorStop
      }
      const mockCtx = {
        createLinearGradient: vi.fn(() => mockGradient)
      }
      
      const gradient = config.createGradient(mockCtx, '#3498db', 400)
      
      expect(mockCtx.createLinearGradient).toHaveBeenCalled()
      expect(gradient).toBeDefined()
      expect(mockAddColorStop).toHaveBeenCalledTimes(2)
    })
  })
})

