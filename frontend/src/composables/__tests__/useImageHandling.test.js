/**
 * Unit tests for useImageHandling composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useImageHandling } from '../useImageHandling.js'
import { isValidImageFile, validateImageSize, validateImageType } from '@/utils/imageValidationUtils'

// Mock dependencies
vi.mock('@/utils/imageValidationUtils', () => ({
  isValidImageFile: vi.fn(() => ({ isValid: true, error: null })),
  validateImageSize: vi.fn(() => ({ isValid: true, error: null })),
  validateImageType: vi.fn(() => ({ isValid: true, error: null }))
}))

// Mock FileReader
globalThis.FileReader = vi.fn(() => ({
  readAsDataURL: vi.fn(),
  onload: null,
  result: 'data:image/jpeg;base64,test'
}))

describe('useImageHandling', () => {
  let imageHandling

  beforeEach(() => {
    vi.clearAllMocks()
    imageHandling = useImageHandling()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(imageHandling.selectedImages.value).toEqual([])
      expect(imageHandling.imagePreviews.value).toEqual([])
      expect(imageHandling.uploadProgress.value).toBe(0)
      expect(imageHandling.isUploading.value).toBe(false)
    })

    it('should compute hasImages correctly', () => {
      expect(imageHandling.hasImages.value).toBe(false)
      
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      expect(imageHandling.hasImages.value).toBe(true)
    })
  })

  describe('validateImage', () => {
    it('should validate valid image', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const result = imageHandling.validateImage(file)
      
      expect(result.isValid).toBe(true)
    })

    it('should reject null file', () => {
      const result = imageHandling.validateImage(null)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBeTruthy()
    })
  })

  describe('addImages', () => {
    it('should add valid image', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const result = imageHandling.addImages(file)
      
      expect(result.added).toHaveLength(1)
      expect(result.errors).toHaveLength(0)
    })

    it('should handle multiple files', () => {
      const files = [
        new File([''], 'test1.jpg', { type: 'image/jpeg' }),
        new File([''], 'test2.jpg', { type: 'image/jpeg' })
      ]
      const result = imageHandling.addImages(files)
      
      expect(result.added).toHaveLength(2)
    })
  })

  describe('navigation', () => {
    it('should navigate to next image', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      
      imageHandling.navigateNext()
      
      expect(imageHandling.currentImageIndex.value).toBe(1)
    })

    it('should navigate to previous image', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      imageHandling.currentImageIndex.value = 1
      
      imageHandling.navigatePrevious()
      
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })
  })

  describe('removeImage', () => {
    it('should remove image', () => {
      const file = new File([''], 'test.jpg')
      imageHandling.selectedImages.value = [file]
      
      imageHandling.removeImage(0)
      
      expect(imageHandling.selectedImages.value).toHaveLength(0)
    })
  })

  describe('clearImages', () => {
    it('should clear all images', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      
      imageHandling.clearImages()
      
      expect(imageHandling.selectedImages.value).toHaveLength(0)
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })
  })
})

