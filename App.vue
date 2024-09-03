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
          <RealTimeChart v-if="isRealtime" />
          <StaticChart v-else />
          <button @click="toggleMode"> {{ isRealtime ? 'Switch to Static' : 'Switch to Real-Time' }}</button>
       
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
//import Con3Component from "./components/Con3Component.vue";
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
    StaticChart
  },
  data() {
    return {
      isRealtime: true,
      }
    },
    methods: {
      toggleMode(){
        this.isRealtime = !this.isRealtime;
      }
    }
};
</script>


<style >


header {
  background-color: #222;
}
.html {
  color: black;
}

html,
body {
  height: 100%;
  background-color: #222;
  margin: 0;
}

.header-section {
  margin-right: 20px ;
  margin-left: 10px;
  padding: 0;
  height: 65px;
  margin-bottom: 0;
}

.header-container {
  font-size: 26px;
  font-family: serif;
  color: white;
  font-weight: bold;
  background-color: rgb(6, 6, 6);
  padding: 13px;
  text-align: center;
  margin-bottom: 10px;
 
}

.machine-info {
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
  margin-left: 6px;
  
}

.machine-info div {
  font-size: 16px;
  font-weight: bold;
}

.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  margin-left: 6px;
  margin-right: 6px;
}

.grid-container > div {
  min-height: 200px;
  padding: 10px;
  margin: 0;
  box-sizing: border-box; /* Includes padding and border in height/width calculations */
}

.zone-section {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
  background-color: #222;
  padding: 10px;
}

.event-section {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  background-color: #222;
  padding: 10px;
}

.chart-section {
  grid-column: 1 / 2;
  grid-row: 2 / 3;
  background-color: #222;
  padding: 10px;
}

.health-indicator-section {
  grid-column: 2 / 3;
  grid-row: 2 / 3;
  background-color: #222;
  padding: 10px;
}

.footer {
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
  color: #ccc;
  background-color: #000000;
  padding: 15px;
  margin-bottom: 0;
}
</style>
