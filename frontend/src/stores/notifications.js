import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const loading = ref(false)
  const websocket = ref(null)
  const settings = ref({
    email_notifications: true,
    push_notifications: true,
    report_notifications: true,
    analysis_notifications: true,
    show_toasts: true,
    sound_enabled: true
  })

  // Computed
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.leida).length
  )

  const recentNotifications = computed(() => 
    notifications.value.slice(0, 5)
  )

  // Actions
  const getNotifications = async (params = {}) => {
    loading.value = true
    try {
      const response = await api.get('/notifications/', { params })
      notifications.value = response.data.results || []
      return response.data
    } catch (error) {
      console.error('Error fetching notifications:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getNotification = async (id) => {
    try {
      const response = await api.get(`/notifications/${id}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching notification:', error)
      throw error
    }
  }

  const markAsRead = async (id) => {
    try {
      const response = await api.patch(`/notifications/${id}/mark-read/`)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notifications.value[index].leida = true
        notifications.value[index].fecha_lectura = response.data.fecha_lectura
      }
      
      return response.data
    } catch (error) {
      console.error('Error marking notification as read:', error)
      throw error
    }
  }

  const markAllAsRead = async () => {
    try {
      const response = await api.post('/notifications/mark-all-read/')
      
      // Update local state
      notifications.value.forEach(notification => {
        if (!notification.leida) {
          notification.leida = true
          notification.fecha_lectura = new Date().toISOString()
        }
      })
      
      return response.data
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
      throw error
    }
  }

  const deleteNotification = async (id) => {
    try {
      await api.delete(`/notifications/${id}/`)
      
      // Remove from local state
      notifications.value = notifications.value.filter(n => n.id !== id)
      
    } catch (error) {
      console.error('Error deleting notification:', error)
      throw error
    }
  }

  const createNotification = async (notificationData) => {
    try {
      const response = await api.post('/notifications/', notificationData)
      
      // Add to local state
      notifications.value.unshift(response.data)
      
      return response.data
    } catch (error) {
      console.error('Error creating notification:', error)
      throw error
    }
  }

  const updateSettings = async (newSettings) => {
    try {
      const response = await api.patch('/notifications/settings/', newSettings)
      settings.value = { ...settings.value, ...response.data }
      return response.data
    } catch (error) {
      console.error('Error updating notification settings:', error)
      throw error
    }
  }

  const getSettings = async () => {
    try {
      const response = await api.get('/notifications/settings/')
      settings.value = { ...settings.value, ...response.data }
      return response.data
    } catch (error) {
      console.error('Error fetching notification settings:', error)
      throw error
    }
  }

  // WebSocket connection
  const connectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`
    
    websocket.value = new WebSocket(wsUrl)

    websocket.value.onopen = () => {
      console.log('WebSocket connected for notifications')
    }

    websocket.value.onclose = () => {
      console.log('WebSocket disconnected for notifications')
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (!websocket.value || websocket.value.readyState === WebSocket.CLOSED) {
          connectWebSocket()
        }
      }, 5000)
    }

    websocket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    websocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
  }

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'notification':
        // Add new notification to the list
        notifications.value.unshift(data.notification)
        
        // Show toast if enabled
        if (settings.value.show_toasts) {
          showToast(data.notification)
        }
        
        // Play sound if enabled
        if (settings.value.sound_enabled) {
          playNotificationSound(data.notification.tipo)
        }
        break
        
      case 'notification_read':
        // Update notification read status
        const index = notifications.value.findIndex(n => n.id === data.notification_id)
        if (index !== -1) {
          notifications.value[index].leida = true
          notifications.value[index].fecha_lectura = data.fecha_lectura
        }
        break
        
      case 'notification_deleted':
        // Remove notification from list
        notifications.value = notifications.value.filter(n => n.id !== data.notification_id)
        break
        
      default:
        console.log('Unknown WebSocket message type:', data.type)
    }
  }

  const disconnectWebSocket = () => {
    if (websocket.value) {
      websocket.value.close()
      websocket.value = null
    }
  }

  // Toast notifications
  const showToast = (notification) => {
    // This will be handled by the NotificationBell component
    // We emit a custom event that the component can listen to
    window.dispatchEvent(new CustomEvent('notification-toast', {
      detail: notification
    }))
  }

  // Sound notifications
  const playNotificationSound = (type) => {
    try {
      const audio = new Audio()
      
      // Different sounds for different notification types
      const soundMap = {
        'error': '/sounds/error.mp3',
        'warning': '/sounds/warning.mp3',
        'success': '/sounds/success.mp3',
        'info': '/sounds/info.mp3',
        'defect_alert': '/sounds/alert.mp3',
        'report_ready': '/sounds/success.mp3',
        'training_complete': '/sounds/success.mp3',
        'welcome': '/sounds/info.mp3'
      }
      
      audio.src = soundMap[type] || '/sounds/notification.mp3'
      audio.volume = 0.3
      audio.play().catch(error => {
        console.log('Could not play notification sound:', error)
      })
    } catch (error) {
      console.log('Error playing notification sound:', error)
    }
  }

  // Browser notification permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  const showBrowserNotification = (notification) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      const browserNotification = new Notification(notification.titulo, {
        body: notification.mensaje,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: `notification-${notification.id}`,
        requireInteraction: notification.tipo === 'error' || notification.tipo === 'defect_alert'
      })

      browserNotification.onclick = () => {
        window.focus()
        browserNotification.close()
        // Navigate to relevant page based on notification type
        handleNotificationClick(notification)
      }

      // Auto-close after 5 seconds (except for important notifications)
      if (notification.tipo !== 'error' && notification.tipo !== 'defect_alert') {
        setTimeout(() => {
          browserNotification.close()
        }, 5000)
      }
    }
  }

  const handleNotificationClick = (notification) => {
    // This will be handled by the component that shows the notification
    window.dispatchEvent(new CustomEvent('notification-click', {
      detail: notification
    }))
  }

  // Utility functions
  const getNotificationStats = async () => {
    try {
      const response = await api.get('/notifications/stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching notification stats:', error)
      throw error
    }
  }

  const clearOldNotifications = async (daysOld = 30) => {
    try {
      const response = await api.post('/notifications/clear-old/', {
        days_old: daysOld
      })
      
      // Refresh notifications list
      await getNotifications()
      
      return response.data
    } catch (error) {
      console.error('Error clearing old notifications:', error)
      throw error
    }
  }

  const exportNotifications = async (format = 'json') => {
    try {
      const response = await api.get('/notifications/export/', {
        params: { format },
        responseType: 'blob'
      })
      
      // Create download link
      const blob = new Blob([response.data], { 
        type: format === 'json' ? 'application/json' : 'text/csv'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `notifications_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Error exporting notifications:', error)
      throw error
    }
  }

  // Initialize store
  const initialize = async () => {
    try {
      await getSettings()
      await requestNotificationPermission()
      connectWebSocket()
    } catch (error) {
      console.error('Error initializing notification store:', error)
    }
  }

  return {
    // State
    notifications,
    loading,
    websocket,
    settings,
    
    // Computed
    unreadCount,
    recentNotifications,
    
    // Actions
    getNotifications,
    getNotification,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    createNotification,
    updateSettings,
    getSettings,
    connectWebSocket,
    disconnectWebSocket,
    showToast,
    playNotificationSound,
    requestNotificationPermission,
    showBrowserNotification,
    handleNotificationClick,
    getNotificationStats,
    clearOldNotifications,
    exportNotifications,
    initialize
  }
})
