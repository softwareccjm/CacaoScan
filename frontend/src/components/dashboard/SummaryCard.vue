<template>
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div 
            class="flex-shrink-0 rounded-md p-3"
            :class="{
              'bg-blue-100 text-blue-600': color === 'blue',
              'bg-green-100 text-green-600': color === 'green',
              'bg-purple-100 text-purple-600': color === 'purple',
              'bg-yellow-100 text-yellow-600': color === 'yellow',
              'bg-gray-100 text-gray-600': !color
            }"
          >
            <span class="text-2xl">{{ icon }}</span>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                {{ title }}
              </dt>
              <dd class="flex items-baseline">
                <div class="text-2xl font-semibold text-gray-900">
                  {{ value }}
                </div>
                <div 
                  v-if="percentage" 
                  :class="{
                    'text-green-600': percentage > 0,
                    'text-red-600': percentage < 0,
                    'text-gray-500': percentage === 0
                  }"
                  class="ml-2 flex items-baseline text-sm font-semibold"
                >
                  <svg 
                    v-if="percentage !== 0"
                    :class="{
                      'text-green-500': percentage > 0,
                      'text-red-500': percentage < 0
                    }" 
                    class="self-center flex-shrink-0 h-5 w-5" 
                    fill="currentColor" 
                    viewBox="0 0 20 20" 
                    aria-hidden="true"
                  >
                    <path 
                      v-if="percentage > 0"
                      fill-rule="evenodd" 
                      d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" 
                      clip-rule="evenodd" 
                    />
                    <path 
                      v-else
                      fill-rule="evenodd" 
                      d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" 
                      clip-rule="evenodd" 
                    />
                  </svg>
                  <span class="sr-only">
                    {{ percentage > 0 ? 'Aumentó' : 'Disminuyó' }} en
                  </span>
                  {{ Math.abs(percentage) }}% desde el mes pasado
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SummaryCard',
    props: {
      title: {
        type: String,
        required: true
      },
      value: {
        type: [String, Number],
        required: true
      },
      icon: {
        type: String,
        default: '📊'
      },
      color: {
        type: String,
        default: ''
      },
      percentage: {
        type: Number,
        default: null
      }
    }
  };
  </script>
  