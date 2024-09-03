<template>
  <div class="con2">
    <div class="status-table">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Zone</th>
            <th>Device</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="abnormal">Abnormal</span></td>
            <td>1. Brazing</td>
            <td>RC Fan No.1</td>
            <td>Vibration X</td>
          </tr>
          <tr>
              <td><span class="abnormal">Abnormal</span></td>
              <td>4.Brazing</td>
              <td>RC Fan No.1</td>
              <td>Vibration Y</td>
          </tr>
          <tr>
              <td><span class="warning">Warning</span></td>
              <td>6.Brazing</td>
              <td>RC Fan No.1</td>
              <td>Vibration Z</td>
          </tr>
          <tr>
              <td><span class="warning">Warning</span></td>
              <td>3.Brazing</td>
              <td>RC Fan No.1</td>
              <td>Temp</td>
          </tr>
          <tr>
              <td><span class="warning">Warning</span></td>
              <td>5.Brazing</td>
              <td>RC Fan No.1</td>
              <td>Speed</td>
          </tr>
          <tr>
              <td><span class="warning">Warning</span></td>
              <td>5.Brazing</td>
              <td>RC Fan No.2</td>
              <td>Vibration X</td>
          </tr>
          

        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Con2Component',
};
</script>

<style scoped>
.con2 {
  background-color: black;
  border-radius: 15px;
  padding: 15px;
  text-align: center;
  color: white;
  min-height: 260px; 
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
</style>
