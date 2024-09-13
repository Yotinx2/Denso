<template>
    <div class="log-details">
      <div class="filter-controls">
        <label for="start-time">Start Time:</label>
        <input type="datetime-local" id="start-time" v-model="startTime" />
  
        <label for="end-time">End Time:</label>
        <input type="datetime-local" id="end-time" v-model="endTime" />
  
        <button @click="fetchLogs">Fetch Logs</button>
      </div>
  
      <div v-if="loading">Loading...</div>
      <div v-if="error">{{ error }}</div>
  
      <table v-if="logs.length">
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.time">
            <td>{{ new Date(log.time).toLocaleDateString() }}</td>
            <td>{{ new Date(log.time).toLocaleTimeString() }}</td>
            <td>{{ log.status }}</td>
            <td>{{ formatDetail(log.value) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>No logs available.</p>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'LogDetails',
    data() {
      return {
        startTime: '',
        endTime: '',
        logs: [],
        loading: false,
        error: null,
      };
    },
    methods: {
      async fetchLogs() {
        if (!this.startTime || !this.endTime) {
          this.error = 'Please select both start and end times.';
          return;
        }
  
        this.loading = true;
        this.error = null;
  
        try {
            let StartTimeZ = this.startTime + ":00Z";
            let EndTimeZ = this.endTime + ":00Z";
            const response = await axios.get('http://localhost:5000/api/logs', {
            params: {
              start_time: StartTimeZ,
              end_time: EndTimeZ,
            },
          });
          this.logs = response.data;
        } catch (error) {
          this.error = `Error fetching log data: ${error.message}`;
        } finally {
          this.loading = false;
        }
      },
      formatDetail(detail) {
        // Replace '_' with ' ' and capitalize the first letter
        return detail.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
      },
    },
  };
  </script>
  
  <style scoped>
  /* Add any specific styles for the log details component here */
  .filter-controls {
    margin-bottom: 10px;
  }
  
  .filter-controls label {
    margin-right: 5px;
  }
  
  .filter-controls input {
    margin-right: 10px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  table, th, td {
    border: 1px solid black;
  }
  
  th, td {
    padding: 8px;
    text-align: left;
  }
  </style>
  