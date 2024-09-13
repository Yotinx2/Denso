<template>
  <div class="con2">
    <div class="status-table">
      <table v-if="events.length">
        <thead>
          <tr>
            <th>Status</th>
            <th>Zone</th>
            <th>Device</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="event in events" :key="event.time">
            <td>
              <span :class="{'abnormal': event.status === 'Abnormal', 'warning': event.status === 'Warning'}">
                {{ event.status }}
              </span>
            </td>
            <td>Brazing</td>
            <td>{{ getDeviceName(event.device) }}</td>
            <td>{{ formatDetail(event.sensors) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-data-message">All senosors are okay.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Con2Component',
  data() {
    return {
      events: [] // This will hold the event data
    };
  },
  mounted() {
    this.fetchEventData(); // Initial data fetch
    this.timer = setInterval(this.fetchEventData, 1000); // Fetch data every 1 second
  },
  beforeUnmount() {
    clearInterval(this.timer); // Clear the interval when the component is destroyed
  },
  methods: {
    fetchEventData() {
      axios.get('http://localhost:5000/api/event-data') // Make sure the endpoint matches your Flask server route
        .then(response => {
          this.events = response.data; // Update events with data from API
        })
        .catch(error => {
          console.error('Error fetching event data:', error);
        });
    },
    getDeviceName(machine_id) {
      switch (machine_id) {
        case 'machine_1':
          return 'RC Fan No.1';
        case 'machine_2':
          return 'RC Fan No.2'; // Add mappings as needed
        case 'machine_3':
          return 'RC Fan No.3'; // Add mappings as needed
        case 'machine_4':
          return 'RC Fan No.4'; // Add mappings as needed
        case 'machine_5':
          return 'RC Fan No.5';
        default:
          return 'Unknown Device'; // Default case if needed
      }
    },
    formatDetail(detail) {
      if (typeof detail === 'string') {
        return detail.replace(/_/g, ' ').replace(/ /g, ' '); 
      } else {
        console.warn('Detail is not a string:', detail);
        return '';
      }
    }
  }
};
</script>

<style scoped>
.con2 {
  background-color: black;
  border-radius: 15px;
  padding: 15px;
  text-align: center;
  color: white;
  min-height: 320px; 
}

.status-table {
  max-height: 280px; /* Adjust this height to control the maximum height */
  overflow-y: auto;
  overflow-x: hidden;
  display: block;
}

.status-table table {
  width: 100%;
  border-collapse: collapse;
}

.status-table th, .status-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  color: white;
}

.abnormal {
  color: red;
  font-weight: bold;
}

.warning {
  color: orange;
  font-weight: bold;
}

.no-data-message {
  color: green;
  font-size: 30px; /* Adjust the font size as needed */
  font-weight: bold;
  text-align: center;
  margin-top: 130px;
}
</style>
