

<template>
  <div class="con3">
    <!-- Dropdowns and Inputs for Filter -->
    <select v-model="SelectedZone">
      <option v-for="zone in zones" :key="zone.zone" :value="zone.zone">{{ zone.name }}</option>
    </select>

    <select v-model="selectedMachineId">
      <option v-for="machine in machines" :key="machine.id" :value="machine.id">{{ machine.name }}</option>
    </select>

    <select v-model="selectedSensorType">
      <option v-for="sensor in sensors" :key="sensor.type" :value="sensor.type">{{ sensor.name }}</option>
    </select>
    <br>

    <label for="startTime">Start Time: </label>
    <input type="datetime-local" v-model="startTime" id="startTime" />

    <label for="endTime">End Time: </label>
    <input type="datetime-local" v-model="endTime" id="endTime" />

    <button @click="fetchData">Filter Data</button>

    <label for="warningThreshold">Warning Threshold: </label>
    <input type="number" v-model.number="warningThreshold" id="warningThreshold" />

    <label for="apnormalThreshold">Apnormal Threshold: </label>
    <input type="number" v-model.number="apnormalThreshold" id="apnormalThreshold" />

    <button type="button" @click="updateThreshold">Update Threshold</button>

    <!-- LineChart Component -->
    <LineChart  :chartData="chartData" :options="options" style="background-color: black" />
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
  TimeScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import 'chartjs-adapter-moment';

// Plugin for horizontal lines
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
      if (line.yValue !== null) {
        const yPosition = yScale.getPixelForValue(line.yValue);
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(chart.chartArea.left, yPosition);
        ctx.lineTo(chart.chartArea.right, yPosition);
        ctx.strokeStyle = line.color;
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
      }
    });
  }
};

ChartJS.register(
  LineController,
  LineElement,
  PointElement,
  TimeScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  Filler,
  horizontalLinePlugin
);

export default defineComponent({
  name: "StaticChart",
  components: { LineChart },
  data() {
    return {
      selectedMachineId: 'machine_1',
      selectedSensorType: 'current',
      SelectedZone: 'zone_1',
      startTime: '',
      endTime: '',
      apnormalThreshold: '',
      warningThreshold: '',
      isStatic: true,
      machines: [
        { id: 'machine_1', name: 'Machine1' },
        { id: 'machine_2', name: 'Machine2' },
        { id: 'machine_3', name: 'Machine3' },
        { id: 'machine_4', name: 'Machine4' },
        { id: 'machine_5', name: 'Machine5' }
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
            label: 'Sensor Data',
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
            type: 'time',
            time: {
              unit: 'minute',
              displayFormats: {
                minute: 'HH:mm'
              }
            },
            ticks: {
              maxRotation: 0,
              minRotation: 0,
              autoSkip: true,
              maxTicksLimit: 10
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 30
            }
          }
        },
        maintainAspectRatio: false,
        thresholds: {
          warning: null,
          apnormal: null
        }
      }
    };
  },
  methods: {
    async fetchData() {
      try {
        let StartTimeZ = this.startTime + ":00Z";
        let EndTimeZ = this.endTime + ":00Z";
        console.log("Start: ", StartTimeZ);
        console.log("Stop: ", EndTimeZ);
        const response = await axios.get('http://localhost:5000/api/static-data', {
          params: {
            machine_id: this.selectedMachineId,
            sensor_type: this.selectedSensorType,
            zone: this.SelectedZone,
            start_time: StartTimeZ,
            end_time: EndTimeZ
          }
        });

        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        this.chartData.datasets[0].data = response.data.map(dataPoint => ({
          x: new Date(new Date(dataPoint.time).getTime() + (7 * 60 * 60 * 1000)).getTime(),  // Adjust to Bangkok timezone (UTC+7)
          y: dataPoint.value
        }));

        if (this.startTime && this.endTime) {
          this.options.scales.x.time.min = new Date(new Date(this.startTime).getTime() + (7 * 60 * 60 * 1000)).getTime();
          this.options.scales.x.time.max = new Date(new Date(this.endTime).getTime() + (7 * 60 * 60 * 1000)).getTime();
        }
      } else {
        this.chartData.datasets[0].data = [];
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

        if (thresholdResponse.data && thresholdResponse.data.length > 0) {
          const { apnormal, warning } = thresholdResponse.data[0];
          chart.options.thresholds = {
            apnormal: apnormal,
            warning: warning
          };
          chart.update();
        }
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
        console.log(response.data.message || 'Thresholds updated successfully');
      } catch (error) {
        console.error(error.response?.data?.error || 'An error occurred');
      }
    }
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
