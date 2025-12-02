/**
 * Unit tests for useBirthdateRange composable
 */

import { describe, it, expect, vi } from 'vitest'
import { useBirthdateRange } from '../useBirthdateRange.js'
import { getMaxBirthdate, getMinBirthdate } from '../useDateFormatting'

// Mock useDateFormatting
vi.mock('../useDateFormatting', () => ({
  getMaxBirthdate: vi.fn(() => '2010-01-01'),
  getMinBirthdate: vi.fn(() => '1900-01-01')
}))

describe('useBirthdateRange', () => {
  it('should return computed maxBirthdate', () => {
    const { maxBirthdate } = useBirthdateRange()
    
    expect(maxBirthdate.value).toBe('2010-01-01')
    expect(getMaxBirthdate).toHaveBeenCalled()
  })

  it('should return computed minBirthdate', () => {
    const { minBirthdate } = useBirthdateRange()
    
    expect(minBirthdate.value).toBe('1900-01-01')
    expect(getMinBirthdate).toHaveBeenCalled()
  })
})

