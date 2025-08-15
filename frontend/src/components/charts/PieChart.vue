<template>
    <div class="chart-container">
      <canvas ref="chart"></canvas>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue';
  import { Chart, registerables } from 'chart.js';
  
  Chart.register(...registerables);
  
  export default {
    name: 'PieChart',
    props: {
      chartData: {
        type: Object,
        required: true
      },
      options: {
        type: Object,
        default: () => ({
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        })
      }
    },
    setup(props) {
      const chart = ref(null);
      let chartInstance = null;
  
      const renderChart = () => {
        if (chartInstance) {
          chartInstance.destroy();
        }
  
        if (chart.value) {
          const ctx = chart.value.getContext('2d');
          chartInstance = new Chart(ctx, {
            type: 'pie',
            data: props.chartData,
            options: props.options
          });
        }
      };
  
      onMounted(() => {
        renderChart();
      });
  
      watch(() => props.chartData, () => {
        renderChart();
      }, { deep: true });
  
      return {
        chart
      };
    }
  };
  </script>
  
  <style scoped>
  .chart-container {
    position: relative;
    width: 100%;
    height: 100%;
  }
  </style>
  