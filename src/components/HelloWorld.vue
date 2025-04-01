<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)

mounted() {
  // 确保图表响应容器大小变化
  nextTick(() => {
    if (chartRef.value) {
      chartRef.value.resize();
    }
  });
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
}

beforeDestroy() {
  // 移除监听器
  window.removeEventListener('resize', handleResize);
}

const handleResize = () => {
  if (chartRef.value) {
    chartRef.value.resize();
  }
}

const getChartOptions = () => {
  return {
    // ... 其他选项 ...
    grid: {
      left: '3%',    // 减少左侧边距
      right: '3%',   // 减少右侧边距
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    // ... 其他选项 ...
  };
}
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">count is {{ count }}</button>
    <p>
      Edit
      <code>components/HelloWorld.vue</code> to test HMR
    </p>
  </div>

  <p>
    Check out
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank"
      >create-vue</a
    >, the official Vue + Vite starter
  </p>
  <p>
    Learn more about IDE Support for Vue in the
    <a
      href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support"
      target="_blank"
      >Vue Docs Scaling up Guide</a
    >.
  </p>
  <p class="read-the-docs">Click on the Vite and Vue logos to learn more</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}

/* 添加或修改图表容器的样式 */
.chart-container {
  width: 100%;
  margin: 0;
  padding: 0;
}

/* 如果有图表的父容器，也需要调整 */
.card, .chart-card {
  width: 100%;
  margin: 0;
  padding: 10px;
  box-sizing: border-box;
}

/* 确保 ECharts 实例撑满容器 */
.echarts {
  width: 100% !important;
  height: 200px; /* 根据需要调整高度 */
}
</style>
