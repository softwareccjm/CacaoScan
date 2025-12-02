/**
 * Unit tests for usePagination composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePagination } from '../usePagination.js'

describe('usePagination', () => {
  describe('initial state', () => {
    it('should have default initial state', () => {
      const pagination = usePagination()
      
      expect(pagination.currentPage.value).toBe(1)
      expect(pagination.itemsPerPage.value).toBe(10)
      expect(pagination.totalItems.value).toBe(0)
      expect(pagination.maxVisible.value).toBe(5)
    })

    it('should accept custom initial values', () => {
      const pagination = usePagination({
        initialPage: 2,
        initialItemsPerPage: 20,
        maxVisiblePages: 7
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.itemsPerPage.value).toBe(20)
      expect(pagination.maxVisible.value).toBe(7)
    })
  })

  describe('computed properties', () => {
    it('should compute totalPages correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 0
      expect(pagination.totalPages.value).toBe(1)
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      expect(pagination.totalPages.value).toBe(3)
    })

    it('should compute startItem correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.startItem.value).toBe(1)
      
      pagination.currentPage.value = 2
      expect(pagination.startItem.value).toBe(11)
    })

    it('should compute endItem correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.endItem.value).toBe(10)
      
      pagination.currentPage.value = 3
      expect(pagination.endItem.value).toBe(25)
    })

    it('should compute hasNextPage correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 25
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      expect(pagination.hasNextPage.value).toBe(true)
      
      pagination.currentPage.value = 3
      expect(pagination.hasNextPage.value).toBe(false)
    })

    it('should compute hasPreviousPage correctly', () => {
      const pagination = usePagination()
      
      pagination.currentPage.value = 1
      expect(pagination.hasPreviousPage.value).toBe(false)
      
      pagination.currentPage.value = 2
      expect(pagination.hasPreviousPage.value).toBe(true)
    })

    it('should compute visiblePages correctly', () => {
      const pagination = usePagination()
      
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 1
      
      const pages = pagination.visiblePages.value
      expect(pages.length).toBeGreaterThan(0)
      expect(pages).toContain(1)
    })
  })

  describe('navigation methods', () => {
    it('should go to specific page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      const result = pagination.goToPage(3)
      
      expect(result).toBe(true)
      expect(pagination.currentPage.value).toBe(3)
    })

    it('should not go to invalid page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      expect(pagination.goToPage(0)).toBe(false)
      expect(pagination.goToPage(10)).toBe(false)
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should go to next page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      pagination.nextPage()
      expect(pagination.currentPage.value).toBe(2)
    })

    it('should go to previous page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 3
      
      pagination.previousPage()
      expect(pagination.currentPage.value).toBe(2)
    })

    it('should go to first page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 3
      
      pagination.firstPage()
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should go to last page', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      
      pagination.lastPage()
      expect(pagination.currentPage.value).toBe(5)
    })
  })

  describe('setItemsPerPage', () => {
    it('should set items per page and reset to first page', () => {
      const pagination = usePagination()
      pagination.currentPage.value = 3
      
      pagination.setItemsPerPage(20)
      
      expect(pagination.itemsPerPage.value).toBe(20)
      expect(pagination.currentPage.value).toBe(1)
    })

    it('should not set invalid items per page', () => {
      const pagination = usePagination()
      const original = pagination.itemsPerPage.value
      
      pagination.setItemsPerPage(0)
      expect(pagination.itemsPerPage.value).toBe(original)
      
      pagination.setItemsPerPage(-5)
      expect(pagination.itemsPerPage.value).toBe(original)
    })
  })

  describe('setTotalItems', () => {
    it('should set total items', () => {
      const pagination = usePagination()
      
      pagination.setTotalItems(100)
      
      expect(pagination.totalItems.value).toBe(100)
    })

    it('should adjust current page if beyond total', () => {
      const pagination = usePagination()
      pagination.totalItems.value = 50
      pagination.itemsPerPage.value = 10
      pagination.currentPage.value = 5
      
      pagination.setTotalItems(20)
      
      expect(pagination.currentPage.value).toBe(2)
    })
  })

  describe('updateFromApiResponse', () => {
    it('should update from API response', () => {
      const pagination = usePagination()
      
      pagination.updateFromApiResponse({
        page: 2,
        count: 50,
        page_size: 20
      })
      
      expect(pagination.currentPage.value).toBe(2)
      expect(pagination.totalItems.value).toBe(50)
      expect(pagination.itemsPerPage.value).toBe(20)
    })
  })

  describe('reset', () => {
    it('should reset to initial values', () => {
      const pagination = usePagination({
        initialPage: 1,
        initialItemsPerPage: 10
      })
      
      pagination.currentPage.value = 5
      pagination.itemsPerPage.value = 20
      pagination.totalItems.value = 100
      
      pagination.reset()
      
      expect(pagination.currentPage.value).toBe(1)
      expect(pagination.itemsPerPage.value).toBe(10)
      expect(pagination.totalItems.value).toBe(0)
    })
  })

  describe('getPaginationParams', () => {
    it('should return pagination params', () => {
      const pagination = usePagination()
      pagination.currentPage.value = 2
      pagination.itemsPerPage.value = 20
      
      const params = pagination.getPaginationParams()
      
      expect(params).toEqual({
        page: 2,
        page_size: 20
      })
    })
  })
})

