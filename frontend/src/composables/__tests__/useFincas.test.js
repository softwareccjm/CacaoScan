/**
 * Unit tests for useFincas composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useFincas } from '../useFincas.js'
import { getFincas, getFincaById, createFinca, updateFinca, deleteFinca } from '@/services/fincasApi'
import { handleApiError } from '@/services/apiErrorHandler'

// Mock dependencies
vi.mock('@/services/fincasApi', () => ({
  getFincas: vi.fn(),
  getFincaById: vi.fn(),
  createFinca: vi.fn(),
  updateFinca: vi.fn(),
  deleteFinca: vi.fn()
}))

vi.mock('@/services/apiErrorHandler', () => ({
  handleApiError: vi.fn((error) => ({
    message: error.message || 'Error'
  }))
}))

describe('useFincas', () => {
  let fincas

  beforeEach(() => {
    vi.clearAllMocks()
    fincas = useFincas()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(fincas.fincas.value).toEqual([])
      expect(fincas.currentFinca.value).toBe(null)
      expect(fincas.isLoading.value).toBe(false)
      expect(fincas.error.value).toBe(null)
      expect(fincas.hasFincas.value).toBe(false)
    })
  })

  describe('loadFincas', () => {
    it('should load fincas successfully', async () => {
      const mockResponse = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 1
      }
      getFincas.mockResolvedValue(mockResponse)

      const result = await fincas.loadFincas()

      expect(getFincas).toHaveBeenCalled()
      expect(fincas.fincas.value).toEqual([{ id: 1, name: 'Finca 1' }])
      expect(fincas.isLoading.value).toBe(false)
    })

    it('should handle load error', async () => {
      const error = new Error('Network error')
      getFincas.mockRejectedValue(error)

      await expect(fincas.loadFincas()).rejects.toThrow()

      expect(fincas.error.value).toBeTruthy()
      expect(fincas.isLoading.value).toBe(false)
    })

    it('should append results for pagination', async () => {
      const page1Response = {
        results: [{ id: 1, name: 'Finca 1' }],
        count: 2
      }
      const page2Response = {
        results: [{ id: 2, name: 'Finca 2' }],
        count: 2
      }

      getFincas.mockResolvedValueOnce(page1Response)
      await fincas.loadFincas({}, 1, 20)

      getFincas.mockResolvedValueOnce(page2Response)
      await fincas.loadFincas({}, 2, 20)

      expect(fincas.fincas.value).toHaveLength(2)
    })
  })

  describe('loadFinca', () => {
    it('should load single finca', async () => {
      const mockFinca = { id: 1, name: 'Finca 1' }
      getFincaById.mockResolvedValue(mockFinca)

      const result = await fincas.loadFinca(1)

      expect(getFincaById).toHaveBeenCalledWith(1)
      expect(fincas.currentFinca.value).toEqual(mockFinca)
      expect(result).toEqual(mockFinca)
    })
  })

  describe('createFinca', () => {
    it('should create finca successfully', async () => {
      const fincaData = { name: 'New Finca' }
      const mockFinca = { id: 1, ...fincaData }
      createFinca.mockResolvedValue(mockFinca)
      const onFincaCreate = vi.fn()

      const fincasWithCallback = useFincas({ onFincaCreate })
      const result = await fincasWithCallback.createFinca(fincaData)

      expect(createFinca).toHaveBeenCalledWith(fincaData)
      expect(onFincaCreate).toHaveBeenCalled()
    })
  })

  describe('updateFinca', () => {
    it('should update finca successfully', async () => {
      const fincaData = { id: 1, name: 'Updated Finca' }
      updateFinca.mockResolvedValue(fincaData)
      const onFincaUpdate = vi.fn()

      const fincasWithCallback = useFincas({ onFincaUpdate })
      const result = await fincasWithCallback.updateFinca(1, fincaData)

      expect(updateFinca).toHaveBeenCalledWith(1, fincaData)
      expect(onFincaUpdate).toHaveBeenCalled()
    })
  })

  describe('deleteFinca', () => {
    it('should delete finca successfully', async () => {
      deleteFinca.mockResolvedValue()
      const onFincaDelete = vi.fn()

      const fincasWithCallback = useFincas({ onFincaDelete })
      await fincasWithCallback.deleteFinca(1)

      expect(deleteFinca).toHaveBeenCalledWith(1)
      expect(onFincaDelete).toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should compute hasFincas correctly', () => {
      fincas.fincas.value = [{ id: 1 }]
      expect(fincas.hasFincas.value).toBe(true)

      fincas.fincas.value = []
      expect(fincas.hasFincas.value).toBe(false)
    })

    it('should compute hasCurrentFinca correctly', () => {
      fincas.currentFinca.value = { id: 1 }
      expect(fincas.hasCurrentFinca.value).toBe(true)

      fincas.currentFinca.value = null
      expect(fincas.hasCurrentFinca.value).toBe(false)
    })
  })
})

