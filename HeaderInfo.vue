<template>
    <div class="header-info">
      <a class="button" href="#">Machine Name: Brazing BRS</a>
      <a class="button" href="#">Machine Code: T6SMM0053900</a>
      <a class="button" href="#">Line Name: BRS Evaporator</a>
    </div>
  </template>
  
  <script>
  export default {
    name: 'HeaderInfo',
  }
  </script>
  
  <style scoped>
  .header-info {
      background-color: black;
      display: flex;
      justify-content: center;
      gap: 65px;
      border-radius: 15px;
      padding: 8px;
      width: 100%;
  }
  
  .button {
      color: rgb(247, 243, 243);
      background-color: rgb(6, 6, 6);
      font-family: serif;
      padding: 5px;
      display: inline-block;
      width: 30%;
      font-weight: bold;
      font-size: 20px;
      text-align: center;
      text-decoration: none;
      box-sizing: border-box;
      cursor: default;
      margin: 0 auto;
  }
  </style>
  