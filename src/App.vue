<template>
  <div class="app-container">
    <header>
      <h2>积分奖励系统</h2>
    </header>
    <main>
      <PointsChart />
    </main>
  </div>
</template>

<script setup>
import PointsChart from './components/PointsChart.vue'
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

.app-container {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
}
</style>