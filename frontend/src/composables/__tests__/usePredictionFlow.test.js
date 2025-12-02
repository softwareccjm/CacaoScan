/**
 * Unit tests for usePredictionFlow composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePredictionFlow } from '../usePredictionFlow.js'
import { usePredictionStore } from '@/stores/prediction'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

// Mock dependencies
const mockStore = {
  currentPrediction: null,
  currentImage: null,
  isLoading: false,
  error: null,
  uploadError: null,
  setCurrentImage: vi.fn(),
  setCurrentPrediction: vi.fn(),
  setError: vi.fn()
}

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockStore
}))

vi.mock('@/services/predictionApi', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn()
}))

// Mock FileReader
globalThis.FileReader = vi.fn(() => ({
  readAsDataURL: vi.fn(),
  onload: null,
  result: 'data:image/jpeg;base64,test'
}))

describe('usePredictionFlow', () => {
  let flow

  beforeEach(() => {
    vi.clearAllMocks()
    flow = usePredictionFlow()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(flow.selectedMethod.value).toBe('traditional')
      expect(flow.imageFile.value).toBe(null)
      expect(flow.isExecuting.value).toBe(false)
    })
  })

  describe('selectMethod', () => {
    it('should select valid method', () => {
      flow.selectMethod('yolo')
      
      expect(flow.selectedMethod.value).toBe('yolo')
    })

    it('should throw error for invalid method', () => {
      expect(() => flow.selectMethod('invalid')).toThrow()
    })
  })

  describe('setImage', () => {
    it('should set valid image file', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const reader = globalThis.FileReader.mock.results[0].value
      
      await flow.setImage(file)

      expect(flow.imageFile.value).toEqual(file)
    })

    it('should reject invalid file type', async () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      
      await expect(flow.setImage(file)).rejects.toThrow()
    })
  })

  describe('validateBeforeExecution', () => {
    it('should validate correctly when ready', () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(true)
    })

    it('should fail validation without method', () => {
      flow.selectedMethod.value = null
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(false)
    })

    it('should fail validation without image', () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = null
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(false)
    })
  })

  describe('executePrediction', () => {
    it('should execute prediction successfully', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImage.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await flow.executePrediction()
      
      expect(predictImage).toHaveBeenCalled()
      expect(mockStore.setCurrentPrediction).toHaveBeenCalled()
    })
  })
})

