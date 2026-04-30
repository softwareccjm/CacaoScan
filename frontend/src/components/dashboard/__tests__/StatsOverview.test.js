import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StatsOverview from '../StatsOverview.vue'

vi.mock('@/components/common/BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: '<div class="base-stats-card"></div>',
    props: ['title', 'value', 'icon', 'trend', 'format', 'color']
  }
}))

vi.mock('@/utils/formatters', () => ({
  parseChange: vi.fn((change) => {
    if (!change || typeof change !== 'string') return 0
    const trimmed = change.trim()
    const regex = /^([+-]?)(\d+\.?\d*)/
    const match = regex.exec(trimmed)
    if (!match) return 0
    const sign = match[1] === '-' ? -1 : 1
    const value = Number.parseFloat(match[2])
    return Number.isNaN(value) ? 0 : sign * value
  })
}))

describe('StatsOverview', () => {
  let wrapper

  const defaultStats = {
    totalBatches: 24,
    batchesChange: '+5%',
    avgQuality: 87,
    qualityChange: '+2%',
    defectRate: 5.2,
    defectChange: '-1.2%'
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render stats overview section', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      expect(wrapper.find('.stats-overview').exists()).toBe(true)
    })

    it('should render the total batches card', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards.length).toBe(1)
    })
  })

  describe('Total Batches Card', () => {
    it('should render total batches card with correct props', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const batchesCard = cards[0]
      
      expect(batchesCard.props('title')).toBe('Total de lotes')
      expect(batchesCard.props('value')).toBe(24)
      expect(batchesCard.props('icon')).toBe('fas fa-seedling')
      expect(batchesCard.props('color')).toBe('success')
    })

    it('should show zero when totalBatches is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {}
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[0].props('value')).toBe(0)
    })

    it('should render trend when batchesChange is provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: defaultStats
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend).toBeTruthy()
      expect(trend.label).toContain('+5%')
      expect(trend.value).toBe(5)
    })

    it('should not render trend when batchesChange is not provided', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 24
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      expect(cards[0].props('trend')).toBeNull()
    })
  })

  describe('Change Values', () => {
    it('should handle positive changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 10,
            batchesChange: '+10%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend.value).toBe(10)
      expect(trend.label).toContain('+10%')
    })

    it('should handle negative changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 10,
            batchesChange: '-5%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')
      
      expect(trend.value).toBe(-5)
      expect(trend.label).toContain('-5%')
    })

    it('should handle decimal changes', () => {
      wrapper = mount(StatsOverview, {
        props: {
          stats: {
            totalBatches: 10,
            batchesChange: '+2.5%'
          }
        }
      })

      const cards = wrapper.findAllComponents({ name: 'BaseStatsCard' })
      const trend = cards[0].props('trend')

      expect(trend.value).toBe(2.5)
    })
  })
})




