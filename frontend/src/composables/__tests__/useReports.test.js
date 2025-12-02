/**
 * Unit tests for useReports composable
 */

import { describe, it, expect } from 'vitest'
import {
  formatReportType,
  formatReportStatus,
  getReportStatusClass,
  getReportStatusIcon,
  formatFileSize,
  formatDuration
} from '../useReports.js'

describe('useReports utility functions', () => {
  describe('formatReportType', () => {
    it('should format known report types', () => {
      expect(formatReportType('calidad')).toBe('Calidad')
      expect(formatReportType('finca')).toBe('Finca')
      expect(formatReportType('auditoria')).toBe('Auditoría')
    })

    it('should return original value for unknown type', () => {
      expect(formatReportType('unknown')).toBe('unknown')
    })
  })

  describe('formatReportStatus', () => {
    it('should format known report statuses', () => {
      expect(formatReportStatus('completado')).toBe('Completado')
      expect(formatReportStatus('generando')).toBe('Generando')
      expect(formatReportStatus('fallido')).toBe('Fallido')
    })

    it('should return original value for unknown status', () => {
      expect(formatReportStatus('unknown')).toBe('unknown')
    })
  })

  describe('getReportStatusClass', () => {
    it('should return CSS class for status', () => {
      expect(getReportStatusClass('completado')).toBe('status-completed')
      expect(getReportStatusClass('error')).toBe('status-error')
      expect(getReportStatusClass('pendiente')).toBe('status-pending')
    })
  })

  describe('getReportStatusIcon', () => {
    it('should return icon class for status', () => {
      expect(getReportStatusIcon('completado')).toContain('check-circle')
      expect(getReportStatusIcon('error')).toContain('exclamation-circle')
      expect(getReportStatusIcon('procesando')).toContain('spinner')
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      expect(formatFileSize(512)).toContain('B')
    })

    it('should format KB', () => {
      expect(formatFileSize(1024)).toContain('KB')
    })

    it('should format MB', () => {
      expect(formatFileSize(1024 * 1024)).toContain('MB')
    })

    it('should return N/A for zero', () => {
      expect(formatFileSize(0)).toBe('N/A')
    })

    it('should return N/A for null/undefined', () => {
      expect(formatFileSize(null)).toBe('N/A')
      expect(formatFileSize(undefined)).toBe('N/A')
    })
  })

  describe('formatDuration', () => {
    it('should format seconds correctly', () => {
      expect(formatDuration(65)).toContain('1')
      expect(formatDuration(30)).toContain('30')
    })

    it('should return N/A for zero/null', () => {
      expect(formatDuration(0)).toBe('N/A')
      expect(formatDuration(null)).toBe('N/A')
    })
  })
})

