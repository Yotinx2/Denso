<template>
  <div class="con3">
    <select v-model="SelectedZone">
      <option v-for="zone in zones" :key="zone.zone" :value="zone.zone">{{ zone.name }}</option>
    </select>

    <select v-model="selectedMachineId">
      <option v-for="machine in machines" :key="machine.id" :value="machine.id">{{ machine.name }}</option>
    </select>

    <select v-model="selectedSensorType">
      <option v-for="sensor in sensors" :key="sensor.type" :value="sensor.type">{{ sensor.name }}</option>
    </select>
    <br />


    <label for="warningThreshold">Warning Threshold: </label>
    <input type="number" v-model.number="warningThreshold" id="warningThreshold" />

    <label for="apnormalThreshold">Apnormal Threshold: </label>
    <input type="number" v-model.number="apnormalThreshold" id="apnormalThreshold" />

    <button type="button" @click="updateThreshold">Update Threshold</button>
    <LineChart :chartData="chartData" :options="options" style="background-color: black" />
  </div>
</template>

<script>
import { defineComponent } from "vue";
import { LineChart } from "vue-chart-3";
import axios from "axios";
import {
  Chart as ChartJS,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import 'chartjs-adapter-moment';
import StreamingPlugin from 'chartjs-plugin-streaming';

const horizontalLinePlugin = {
  id: 'horizontalLine',
  afterDraw: (chart) => {
    const yScale = chart.scales.y;
    const ctx = chart.ctx;

    const lines = [
      { yValue: chart.options.thresholds.apnormal, color: 'red' },
      { yValue: chart.options.thresholds.warning, color: 'orange' }
    ];

    lines.forEach(line => {
      const yPosition = yScale.getPixelForValue(line.yValue);
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(chart.chartArea.left, yPosition);
      ctx.lineTo(chart.chartArea.right, yPosition);
      ctx.strokeStyle = line.color;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();
    });
  }
};

ChartJS.register(
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler,
  StreamingPlugin,
  horizontalLinePlugin,
);

export default defineComponent({
  name: "RealTimeChart",
  components: { LineChart },
  data() {
    return {
      selectedMachineId: 'machine_1',
      selectedSensorType: 'current',
      SelectedZone: 'zone_1',
      startTime: '',
      endTime: '',
      staticData: [],
      realtimeData: [],
      isRealTime: true,
      apnormalThreshold: '',
      warningThreshold: '',
      machines: [
        { id: 'machine_1', name: 'Machine1' },
        { id: 'machine_2', name: 'Machine2' },
        { id: 'machine_3', name: 'Machine3' },
        { id: 'machine_4', name: 'Machine4' },
        { id: 'machine_5', name: 'Machine5' },
      ],
      sensors: [
        { type: 'vibration_velocity', name: 'vibration_velocity' },
        { type: 'vibration_acceleration', name: 'vibration_acceleration' },
        { type: 'temperature', name: 'Temperature' },
        { type: 'flow_rate_in', name: 'Flow Rate In' },
        { type: 'flow_rate_out', name: 'Flow Rate Out' },
        { type: 'water_temp_in', name: 'Water Temp In' },
        { type: 'water_temp_out', name: 'Water Temp Out' },
        { type: 'current', name: 'current' },
        { type: 'speed', name: 'speed' }
      ],
      zones: [
        { zone: 'zone_1', name: 'Zone 1' },
        { zone: 'zone_2', name: 'Zone 2' },
        { zone: 'zone_3', name: 'Zone 3' },
        { zone: 'zone_4', name: 'Zone 4' },
        { zone: 'zone_5', name: 'Zone 5' }
      ],
      chartData: {
        datasets: [
          {
            label: 'Real-Time Data',
            pointBackgroundColor: "rgba(54, 162, 235, 1)",
            backgroundColor: "rgba(15, 10, 222, 1)",
            borderColor: "rgba(15, 10, 222, 1)",
            data: [],
            fill: false,
            pointRadius: 1,
            borderWidth: 2,
            pointHoverRadius: 7,
            tension: .1
          },
          {
            label: 'Warning',
            backgroundColor: "rgba(255, 165, 0, 1)",
            borderColor: "rgba(255, 165, 0, 1)",
          },
          {
            label: 'Appnormal',
            backgroundColor: "rgba(255, 0, 0, 1)",
            borderColor: "rgba(255, 0, 0, 1)",
          },
        ]
      },
      options: {
        scales: {
          x: {
            type: 'realtime',
            realtime: {
              duration: 10000,  // Display data for the last 10 seconds
              refresh: 1000,    // Fetch data every second
              delay: 0,         // Set to 0 for real-time display without delay
              onRefresh: async (chart) => {
                try {
                  if (this.isRealTime) {
                    await this.fetchDataRealtime(chart); // Use method to fetch real-time data
                  }
                  await this.fetchThreshold(chart); // Fetch thresholds regardless of mode
                } catch (error) {
                  console.error('Error during onRefresh:', error);
                }
              }
            },
            time: {
              unit: 'second',   // Display time in seconds
              displayFormats: {
                second: 'HH:mm:ss'
              }
            },
            ticks: {
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,   // Automatically skip labels to avoid overlap
              maxTicksLimit: 10
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 30,
              min: () => Math.min(...this.chartData.datasets[0].data.map(d => d.y)), // Set dynamically
              max: () => Math.max(...this.chartData.datasets[0].data.map(d => d.y))  // Set dynamically
            }
          },
        },
        maintainAspectRatio: false,
        thresholds: {
          warning: null,
          apnormal: null
        }
      }
    }
  },
  methods: {
    async fetchDataRealtime(chart) {
      try {
        const dataResponse = await axios.get('http://localhost:5000/api/data', {
          params: {
            machine_id: this.selectedMachineId,
            sensor_type: this.selectedSensorType,
            zone: this.SelectedZone
          }
        });
        const data = dataResponse.data;
        if (data && Array.isArray(data) && data.length > 0) {
          chart.data.datasets[0].data = chart.data.datasets[0].data || [];

          data.forEach((dataPoint) => {
            chart.data.datasets[0].data.push({
              x: new Date(dataPoint.time).getTime(),
              y: dataPoint.value
            });
          });

          if (chart.data.datasets[0].data.length > 60) {
            chart.data.datasets[0].data.splice(0, chart.data.datasets[0].data.length - 60);
          }
        } else {
          console.warn('No data received or data is empty for this zone.');
          chart.data.datasets[0].data = [];
          chart.update('quiet');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    async fetchThreshold(chart) {
      try {
        const thresholdResponse = await axios.get('http://localhost:5000/get-thresholds', {
          params: {
            zone: this.SelectedZone,
            machine_id: this.selectedMachineId,
            sensor_type: this.selectedSensorType,
          }
        });

        const [apnormalValue, warningValue] = thresholdResponse.data[0] || [];
        // console.log('Apnormal Threshold:', apnormalValue);
        // console.log('Warning Threshold:', warningValue);

        chart.options.thresholds = {
          apnormal: apnormalValue,
          warning: warningValue
        };
      } catch (error) {
        console.error('Error fetching thresholds:', error);
      }
    },
    async updateThreshold() {
      try {
        const response = await axios.post('http://localhost:5000/update-thresholds', {
          zone: this.SelectedZone,
          machine_id: this.selectedMachineId,
          sensor_type: this.selectedSensorType,
          warning_value: this.warningThreshold,
          apnormal_value: this.apnormalThreshold
        });
        this.responseMessage = response.data.message || 'Thresholds updated successfully';
      } catch (error) {
        this.responseMessage = error.response?.data?.error || 'An error occurred';
      }
    },
  }
});
</script>

<style scoped>
.con3 {
  background-color: black;
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  color: white;
  min-height: 260px;
}
</style>