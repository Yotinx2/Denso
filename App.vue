<template>
  <div class="html">
    <div class="header-container">
      WGR PLANT: MACHINE PERFORMANCE VISUALIZATION
    </div>
    <header>
      <div class="header-section">
        <HeaderInfo />
      </div>
    </header>
    <main>
      <div class="grid-container">
        <div class="zone-section">
          <Con1Component />
        </div>

        <div class="event-section">
          <Con2Component />
        </div>

        <div class="chart-section">
          <RealTimeChart v-show="isRealtime" />
          <StaticChart v-show="!isRealtime"/>
          <button @click="toggleMode">
            {{ isRealtime ? 'Switch to Static' : 'Switch to Real-Time' }}
          </button>
        </div>

        <div class="health-indicator-section">
          <Con4Component />
        </div>
      </div>
      <div class="footer">
        <p>© DNTH-TSD, Manufacturing Engineering, TPM Department</p>
      </div>
    </main>
  </div>
</template>

<script>
import Con1Component from "./components/Con1Component.vue";
import Con2Component from "./components/Con2Component.vue";
import Con4Component from "./components/Con4Component.vue";
import HeaderInfo from "./components/HeaderInfo.vue";
import StaticChart from "./components/StaticChart.vue";
import RealTimeChart from "./components/RealTime.vue";

export default {
  name: "MainComponent",
  components: {
    Con1Component,
    Con2Component,
    RealTimeChart,
    Con4Component,
    HeaderInfo,
    StaticChart,
  },
  data() {
    return {
      isRealtime: true,
    };
  },
  methods: {
    toggleMode() {
      this.isRealtime = !this.isRealtime;
    },
  },
};
</script>

<style>
/* General Page Styles */
.html {
  color: white;
  background-color: #222;
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}

/* Header Styles */
.header-container {
  font-size: 26px;
  font-weight: bold;
  background-color: #060606;
  color: white;
  padding: 13px;
  text-align: center;
  margin-top: 10px;
  margin-bottom: 10px;
}

.header-section {
  padding: 0 20px;
  height: 65px;
  margin-bottom: 10px;
}

/* Grid Layout */
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  grid-gap: 10px;
  padding: 10px;
  margin: 10px;
}

.grid-container > div {
  padding: 10px;
  background-color: #333;
  box-sizing: border-box;
  border-radius: 4px;
}
/* Section Styles */
.zone-section,
.event-section,
.chart-section,
.health-indicator-section {
  background-color: #222;
}
.chart-section button {
  margin-top: 10px;
  padding: 5px 10px;
  font-size: 14px;
  cursor: pointer;
  background-color: #444;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}
.chart-section button:hover {
  background-color: #555;
}
/* Footer Styles */
.footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #ccc;
  background-color: #000;
  padding: 15px;
}
</style>
