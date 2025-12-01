<template>
  <BasePreferences
    :model-value="modelValue"
    :title="title"
    :show-header="showHeader"
    :show-actions="showActions"
    :show-save-button="showSaveButton"
    :show-reset-button="showResetButton"
    :save-button-text="saveButtonText"
    :reset-button-text="resetButtonText"
    :container-class="containerClass"
    @update:model-value="$emit('update:modelValue', $event)"
    @save="$emit('save', $event)"
    @reset="$emit('reset')"
  >
    <template #header-icon>
      <slot name="header-icon">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
        </svg>
      </slot>
    </template>
    <template #content="{ value, update }">
      <slot :name="contentSlotName" :value="value" :update="update">
        <!-- Default content can be provided via props or slots -->
      </slot>
    </template>
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BasePreferences>
</template>

<script setup>
import BasePreferences from './BasePreferences.vue'

defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  title: {
    type: String,
    required: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showSaveButton: {
    type: Boolean,
    default: true
  },
  showResetButton: {
    type: Boolean,
    default: false
  },
  saveButtonText: {
    type: String,
    default: 'Guardar'
  },
  resetButtonText: {
    type: String,
    default: 'Restablecer'
  },
  containerClass: {
    type: String,
    default: 'bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg'
  },
  iconPath: {
    type: String,
    required: true
  },
  contentSlotName: {
    type: String,
    default: 'content'
  }
})

defineEmits(['update:modelValue', 'save', 'reset'])
</script>

