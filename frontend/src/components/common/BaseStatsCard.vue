<template>
  <div 
    class="base-stat-card"
    :class="[
      variant,
      { 
        'clickable': clickable,
        'has-trend': trend
      }
    ]"
    @click="handleClick"
  >
    <div class="stat-icon">
      <i :class="icon"></i>
    </div>
    <div class="stat-content">
      <div class="stat-value">
        <span class="stat-number">{{ formatValue(value) }}</span>
        <span v-if="suffix" class="stat-suffix">{{ suffix }}</span>
      </div>
      <div class="stat-label">{{ label }}</div>
      <div v-if="change !== undefined" class="stat-change" :class="getChangeClass(change)">
        <i :class="getChangeIcon(change)"></i>
        <span>{{ formatChange(change) }}</span>
        <span v-if="changePeriod" class="change-period">{{ changePeriod }}</span>
      </div>
      <div v-if="description" class="stat-description">
        {{ description }}
      </div>
    </div>
    <div v-if="trend" class="stat-trend">
      <TrendChart 
        :data="trend.data" 
        :color="trend.color || defaultColor"
        :height="40"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TrendChart from '@/components/charts/TrendChart.vue'

const props = defineProps({
  value: {
    type: [String, Number],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  suffix: {
    type: String,
    default: null
  },
  change: {
    type: Number,
    default: undefined
  },
  changePeriod: {
    type: String,
    default: null
  },
  description: {
    type: String,
    default: null
  },
  trend: {
    type: Object,
    default: null,
    validator: (value) => {
      if (!value) return true
      return value.data && Array.isArray(value.data)
    }
  },
  clickable: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['click'])

const defaultColor = computed(() => {
  if (props.color) return props.color
  
  const colors = {
    default: '#3498db',
    primary: '#1f4e79',
    success: '#0d5c3d',
    warning: '#8a4b00',
    danger: '#8b1f1f',
    info: '#145057'
  }
  return colors[props.variant] || colors.default
})

const formatValue = (value) => {
  if (typeof value === 'number') {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M'
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K'
    }
    return value.toLocaleString()
  }
  return value
}

const formatChange = (change) => {
  if (typeof change === 'number') {
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}%`
  }
  return change
}

const getChangeClass = (change) => {
  if (typeof change === 'number') {
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return 'neutral'
  }
  return 'neutral'
}

const getChangeIcon = (change) => {
  if (typeof change === 'number') {
    if (change > 0) return 'fas fa-arrow-up'
    if (change < 0) return 'fas fa-arrow-down'
    return 'fas fa-minus'
  }
  return 'fas fa-minus'
}

const handleClick = () => {
  if (props.clickable) {
    emit('click', {
      value: props.value,
      label: props.label,
      variant: props.variant
    })
  }
}
</script>

<style scoped>
.base-stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  animation: fadeInUp 0.6s ease-out;
}

.base-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.base-stat-card.clickable {
  cursor: pointer;
}

.base-stat-card.clickable:hover {
  border-color: #3b82f6;
}

/* Variants */
.base-stat-card.primary {
  background: linear-gradient(135deg, #1f4e79 0%, #31235d 100%);
  color: #ffffff;
  border: none;
}

.base-stat-card.success {
  background: linear-gradient(135deg, #0d5c3d 0%, #0b3f2b 100%);
  color: #ffffff;
  border: none;
}

.base-stat-card.warning {
  background: linear-gradient(135deg, #8a4b00 0%, #5c3200 100%);
  color: #ffffff;
  border: none;
}

.base-stat-card.danger {
  background: linear-gradient(135deg, #8b1f1f 0%, #5a1212 100%);
  color: #ffffff;
  border: none;
}

.base-stat-card.info {
  background: linear-gradient(135deg, #145057 0%, #0b3744 100%);
  color: #ffffff;
  border: none;
}

.stat-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #1f2937;
  background: rgba(255, 255, 255, 0.9);
}

.base-stat-card.primary .stat-icon,
.base-stat-card.success .stat-icon,
.base-stat-card.danger .stat-icon,
.base-stat-card.warning .stat-icon,
.base-stat-card.info .stat-icon {
  background: rgba(255, 255, 255, 0.85);
  color: #1f2937;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: #1f2937;
}

.base-stat-card.primary .stat-number,
.base-stat-card.success .stat-number,
.base-stat-card.danger .stat-number,
.base-stat-card.warning .stat-number,
.base-stat-card.info .stat-number {
  color: #ffffff;
}

.stat-suffix {
  font-size: 1rem;
  font-weight: 500;
  color: #6b7280;
}

.base-stat-card.primary .stat-suffix,
.base-stat-card.success .stat-suffix,
.base-stat-card.danger .stat-suffix,
.base-stat-card.warning .stat-suffix,
.base-stat-card.info .stat-suffix {
  color: rgba(255, 255, 255, 0.95);
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.base-stat-card.primary .stat-label,
.base-stat-card.success .stat-label,
.base-stat-card.danger .stat-label,
.base-stat-card.warning .stat-label,
.base-stat-card.info .stat-label {
  color: rgba(255, 255, 255, 0.95);
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #dc2626;
}

.stat-change.neutral {
  color: #6b7280;
}

.base-stat-card.primary .stat-change,
.base-stat-card.success .stat-change,
.base-stat-card.danger .stat-change,
.base-stat-card.warning .stat-change,
.base-stat-card.info .stat-change {
  color: rgba(255, 255, 255, 0.95);
}

.change-period {
  font-weight: 400;
  opacity: 0.8;
}

.stat-description {
  font-size: 0.75rem;
  color: #9ca3af;
  line-height: 1.4;
}

.base-stat-card.primary .stat-description,
.base-stat-card.success .stat-description,
.base-stat-card.danger .stat-description,
.base-stat-card.warning .stat-description,
.base-stat-card.info .stat-description {
  color: rgba(255, 255, 255, 0.9);
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 60px;
  height: 40px;
  opacity: 0.7;
}

/* Responsive */
@media (max-width: 768px) {
  .base-stat-card {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 1.75rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .base-stat-card {
    padding: 16px;
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    align-self: center;
  }
  
  .stat-trend {
    position: static;
    margin-top: 12px;
    align-self: center;
  }
}

/* Animation */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

