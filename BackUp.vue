<template>
  <div class="con3">

    <!-- Input fields for thresholds -->
    <!-- <label for="upperWarningThreshold">Upper Warning Threshold: </label>
    <input type="number" v-model.number="upperWarningThreshold" id="upperWarningThreshold" />

    <label for="upperAbnormalThreshold">Upper Abnormal Threshold: </label>
    <input type="number" v-model.number="upperAbnormalThreshold" id="upperAbnormalThreshold" />
    
    <br>
    <label for="lowerWarningThreshold">Lower Warning Threshold: </label>
    <input type="number" v-model.number="lowerWarningThreshold" id="lowerWarningThreshold" />

    <label for="lowerAbnormalThreshold">Lower Abnormal Threshold: </label>
    <input type="number" v-model.number="lowerAbnormalThreshold" id="lowerAbnormalThreshold" /> -->
    

    <div ref="chart"></div>
    <select v-model="SelectedZone">
      <option v-for="zone in zones" :key="zone.zone" :value="zone.zone">{{ zone.name }}</option>
    </select>

    <select v-model="selectedMachineId">
      <option v-for="machine in machines" :key="machine.id" :value="machine.id">{{ machine.name }}</option>
    </select>

    <select v-model="selectedSensorType">
      <option v-for="sensor in sensors" :key="sensor.type" :value="sensor.type">{{ sensor.name }}</option>
    </select>

  </div>
  <button type="button" @click="updateThresholds">Update Threshold</button>
</template>

<script>
import Plotly from 'plotly.js-dist';
import axios from 'axios';

export default {
  name: 'RealTime',
  data() {
    return {
      intervalId: null,
      maxDataPoints: 10,
      tickInterval: 1000,
      selectedMachineId: 'machine_1',
      selectedSensorType: 'current',
      SelectedZone: 'zone_1',
      upperWarningThreshold: null,
      lowerWarningThreshold: null,
      upperAbnormalThreshold: null,
      lowerAbnormalThreshold: null,
      lastThresholds: {
        upperAbnormal: null,
        lowerAbnormal: null,
        upperWarning: null,
        lowerWarning: null,
      },
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
    };
  },
  mounted() {
  this.initChart();
  this.intervalId = setInterval(() => {
    this.fetchDataRealtime();
    this.fetchThreshold(); // Fetch thresholds regularly to ensure they are up-to-date
  }, this.tickInterval);
},
  beforeUnmount() {
    clearInterval(this.intervalId);
  },
  methods: {
    async fetchThreshold() {
      try {
        const response = await axios.get('http://localhost:5000/get-thresholds', {
          params: {
            zone: this.SelectedZone,
            machine_id: this.selectedMachineId,
            sensor_type: this.selectedSensorType,
          }
        });

        const {
          upper_abnormal: upperAbnormal,
          lower_abnormal: lowerAbnormal,
          upper_warning: upperWarning,
          lower_warning: lowerWarning
        } = response.data;

        this.lastThresholds = {
          upperAbnormal,
          lowerAbnormal,
          upperWarning,
          lowerWarning
        };

        // Update chart layout with threshold shapes
        this.updateThresholdShapes(upperAbnormal, lowerAbnormal, upperWarning, lowerWarning);
      } catch (error) {
        console.error('Error fetching thresholds:', error);
      }
    },
    updateThresholdShapes(upperAbnormal, lowerAbnormal, upperWarning, lowerWarning) {
      const shapes = [];

      // Upper and lower abnormal thresholds
      if (upperAbnormal !== null && upperAbnormal !== undefined) {
        shapes.push({
          type: 'line',
          x0: 0,
          x1: 1,
          y0: upperAbnormal,
          y1: upperAbnormal,
          xref: 'paper',
          line: {
            color: 'red',
            width: 2,
          },
          layer: 'below'
        });
      }
      if (lowerAbnormal !== null && lowerAbnormal !== undefined) {
        shapes.push({
          type: 'line',
          x0: 0,
          x1: 1,
          y0: lowerAbnormal,
          y1: lowerAbnormal,
          xref: 'paper',
          line: {
            color: 'red',
            width: 2,
          },
          layer: 'below'
        });
      }

      // Upper and lower warning thresholds
      if (upperWarning !== null && upperWarning !== undefined) {
        shapes.push({
          type: 'line',
          x0: 0,
          x1: 1,
          y0: upperWarning,
          y1: upperWarning,
          xref: 'paper',
          line: {
            color: 'orange',
            width: 2,
          },
          layer: 'below'
        });
      }
      if (lowerWarning !== null && lowerWarning !== undefined) {
        shapes.push({
          type: 'line',
          x0: 0,
          x1: 1,
          y0: lowerWarning,
          y1: lowerWarning,
          xref: 'paper',
          line: {
            color: 'orange',
            width: 2,
          },
          layer: 'below'
        });
      }

      // Update the chart with the new threshold shapes
      Plotly.relayout(this.$refs.chart, { shapes });
    },




    // Initialize the Plotly chart
    initChart() {
      if (!this.$refs.chart) {
        console.error('Chart element not found');
        return;
      }
      const layout = {
        title: { text: 'Real-time Data', font: { color: 'white' }, y: .92},
        xaxis: {
          title: { text: 'Time', font: { color: 'white' } },
          type: 'date',
          color: 'white',
          showgrid: false,

        },
        yaxis: {
          title: { text: 'Value', font: { color: 'white' } },
          color: 'white',
          showgrid: false,
          zeroline: false
        },
        paper_bgcolor: 'black',
        plot_bgcolor: 'black',
        shapes: [],
        showlegend: true,
        autosize: true,
        legend: {
          x: 1,
          y: 1.15,
          xanchor: 'right',
          yanchor: 'top',
          orientation : 'h',
          font: {
            color: 'Gainsboro'
          },
        }
      };

      const trace = {
        x: [],
        y: [],
        mode: 'lines',
        line: { color: 'blue', width: 2 },
        marker: { size: 5, color: 'blue', symbol: 'circle' },
        name: 'Sensor Value'
      };

      const warningTrace = {
    x: [null],  // No actual points, just for the legend
    y: [null],
    mode: 'lines',
    line: { color: 'orange', width: 2 },
    name: 'Warning Threshold',
    showlegend: true,
    hoverinfo: 'skip',
  };

  // Dummy trace for abnormal threshold in the legend
  const abnormalTrace = {
    x: [null],  // No actual points, just for the legend
    y: [null],
    mode: 'lines',
    line: { color: 'red', width: 2 },
    name: 'Abnormal Threshold',
    showlegend: true,
    hoverinfo: 'skip',
  };


      Plotly.newPlot(this.$refs.chart, [trace, warningTrace, abnormalTrace], layout);

      // Fetch thresholds after chart initialization
      this.fetchThreshold();
    },

    // Function to fetch real-time data and update the chart
    async fetchDataRealtime() {
      try {
        const response = await axios.get('http://localhost:5000/api/data', {
          params: {
            machine_id: this.selectedMachineId,
            sensor_type: this.selectedSensorType,
            zone: this.SelectedZone,
          }
        });

        const data = response.data;

        if (data && Array.isArray(data) && data.length > 0) {
          const newTimes = data.map(dp => dp.time ? new Date(dp.time).toISOString() : null);
          const newValues = data.map(dp => dp.value ? dp.value : null);

          // Remove invalid (null) values from newTimes and newValues
          const validData = newTimes.every((time, index) => time !== null && newValues[index] !== null);

          if (!validData) {
            console.error("Invalid data fetched");
            return;
          }

          Plotly.extendTraces(this.$refs.chart, { x: [newTimes], y: [newValues] }, [0]);

          const currentXData = this.$refs.chart.data[0].x;
          const currentYData = this.$refs.chart.data[0].y;

          if (currentXData.length > this.maxDataPoints) {
            const excessPoints = currentXData.length - this.maxDataPoints;
            currentXData.splice(0, excessPoints);
            currentYData.splice(0, excessPoints);

            Plotly.relayout(this.$refs.chart, {
              xaxis: { range: [currentXData[0], currentXData[currentXData.length - 1]] }
            });
          }
        }

        // Fetch thresholds each time data is updated in case they have changed
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
    async updateThresholds() {
  try {
    // Create an object with only the provided thresholds
    const thresholdsData = {
      zone: this.SelectedZone,
      machine_id: this.selectedMachineId,
      sensor_type: this.selectedSensorType,
    };

       thresholdsData.upper_abnormal = this.upperAbnormalThreshold !== null ? this.upperAbnormalThreshold : this.lastThresholds.upperAbnormal;
        thresholdsData.lower_abnormal = this.lowerAbnormalThreshold !== null ? this.lowerAbnormalThreshold : this.lastThresholds.lowerAbnormal;
        thresholdsData.upper_warning = this.upperWarningThreshold !== null ? this.upperWarningThreshold : this.lastThresholds.upperWarning;
        thresholdsData.lower_warning = this.lowerWarningThreshold !== null ? this.lowerWarningThreshold : this.lastThresholds.lowerWarning;
    // Send the thresholds data to the backend
    const response = await axios.post('http://localhost:5000/update-thresholds', thresholdsData);

    console.log('Thresholds updated:', response.data);

    // Fetch and update thresholds after successful update
    this.fetchThreshold();
  } catch (error) {
    console.error('Error updating thresholds:', error);
  }
}


  }
};
</script>

<style scoped>
.con3 {
  background-color: black;
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  color: rgb(255, 255, 255);
}
</style>
