<template>
    <div class="con4">
      <div class="rul-indicator">
        <div class="rul-value">RUL: 96 Days (Sat 27-Jul-24)</div>
        <div class="thresholds">
          <span class="warning">Warning</span>
          <span class="abnormal">Abnormal</span>
        </div>
      </div>
      <canvas id="health-chart"></canvas>
    </div>
  </template>
  
  <script>
  
  import { Chart } from 'chart.js';
  
  export default {
    name: 'Con4Component',
    methods: {
      createHealthChart() {
        const ctx = document.getElementById('health-chart').getContext('2d');
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            // Dummy data for health indicator
            labels: ['Healthy', 'Warning', 'Abnormal'],
            datasets: [{
              data: [80, 15, 5],
              backgroundColor: ['green', 'orange', 'red']
            }]
          },
          options: {
            // Your options here
          }
        });
      }
    },
    onMounted() {
      this.createHealthChart();
    }
  };
  </script>
  
  <style scoped>
  .con4 {
    background-color: black;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    color: white;
    min-height: 260px; 
  }
  
  .rul-indicator {
    text-align: center;
    margin: 20px 0;
  }
  
  .rul-value {
    font-size: 18px;
    font-weight: bold;
  }
  
  .warning {
    color: orange;
    font-weight: bold;
    margin-right: 10px;
  }
  
  .abnormal {
    color: red;
    font-weight: bold;
  }
  </style>
  