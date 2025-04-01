<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import axios from 'axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// 注册 ECharts 组件
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent])

const chartRef = ref(null)
const totalPoints = ref(0)
const pointsRecords = ref([])
const currentUser = ref('辛巴')
const users = ref(['辛巴', '泡芙'])

// 弹窗相关状态
const showDialog = ref(false)
const dialogType = ref('add') // 'add' 或 'reduce'
const dialogPoints = ref(10)
const dialogDescription = ref('')

// 积分规则浮层状态
const showRulesPanel = ref(false)

// 积分兑换规则
const pointsRules = [
  { title: '完成家庭作业', points: 10, description: '按时完成当天布置的家庭作业' },
  { title: '帮助做家务', points: 5, description: '帮忙整理房间、洗碗等家务' },
  { title: '阅读30分钟', points: 5, description: '专注阅读课外书籍30分钟' },
  { title: '运动锻炼', points: 5, description: '进行30分钟以上的体育锻炼' },
  { title: '考试成绩优秀', points: 20, description: '考试成绩达到90分以上' }
]

// 积分兑换奖励
const pointsRewards = [
  { title: '额外的游戏时间', points: 30, description: '获得30分钟额外的游戏时间' },
  { title: '选择晚餐', points: 50, description: '可以选择一顿喜欢的晚餐' },
  { title: '小玩具', points: 100, description: '可以兑换一个小玩具' },
  { title: '周末活动', points: 200, description: '可以选择一个周末活动，如去游乐园' },
  { title: '大型礼物', points: 500, description: '可以兑换一个大型礼物' }
]

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/users')
    if (response.data && response.data.length > 0) {
      users.value = response.data
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

// 获取积分数据
const fetchPointsData = async () => {
  try {
    const response = await axios.get(`/api/points?user=${currentUser.value}`)
    totalPoints.value = response.data.total_points
    pointsRecords.value = response.data.records
  } catch (error) {
    console.error('获取积分数据失败:', error)
  }
}

// 获取积分历史数据
const fetchPointsHistory = async () => {
  try {
    const response = await axios.get(`/api/points/history?user=${currentUser.value}`)
    updateChart(response.data)
  } catch (error) {
    console.error('获取积分历史数据失败:', error)
  }
}

// 切换用户
const switchUser = (user) => {
  currentUser.value = user
  fetchPointsData()
  fetchPointsHistory()
}

// 更新图表
const updateChart = (data) => {
  if (!chartRef.value) return
  
  const dates = data.map(item => item.date)
  const points = data.map(item => item.points)
  
  chartRef.value.setOption({
    grid: {
      left: '3%',
      right: '3%',
      top: '10%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: points,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: {
        color: '#4080ff'
      },
      lineStyle: {
        width: 3
      }
    }]
  })
}

// 打开添加积分弹窗
const openAddDialog = () => {
  dialogType.value = 'add'
  dialogPoints.value = ''
  dialogDescription.value = ''
  showDialog.value = true
}

// 打开减少积分弹窗
const openReduceDialog = () => {
  dialogType.value = 'reduce'
  dialogPoints.value = ''
  dialogDescription.value = ''
  showDialog.value = true
}

// 关闭弹窗
const closeDialog = () => {
  showDialog.value = false
}

// 切换积分规则面板
const toggleRulesPanel = () => {
  showRulesPanel.value = !showRulesPanel.value
}

// 提交积分变更
const submitPointsChange = async () => {
  // 确保积分是数字类型
  const pointsValue = parseInt(dialogPoints.value) || 0
  
  if (pointsValue <= 0) {
    alert('积分必须为正数')
    return
  }
  
  try {
    if (dialogType.value === 'add') {
      await axios.post('/api/points/add', { 
        points: pointsValue, 
        description: dialogDescription.value || '增加积分',
        user: currentUser.value
      })
    } else {
      await axios.post('/api/points/reduce', { 
        points: pointsValue, 
        description: dialogDescription.value || '减少积分',
        user: currentUser.value
      })
    }
    
    await fetchPointsData()
    await fetchPointsHistory()
    closeDialog()
  } catch (error) {
    console.error('积分操作失败:', error)
    alert('操作失败: ' + (error.response?.data?.error || error.message))
  }
}

onMounted(() => {
  fetchUsers()
  fetchPointsData()
  fetchPointsHistory()
  
  // 确保图表响应容器大小变化
  nextTick(() => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  })
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  // 移除监听器
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (chartRef.value) {
    chartRef.value.resize()
  }
}
</script>

<template>
  <div class="points-container">
    <!-- 用户切换 -->
    <div class="user-switcher">
      <button 
        v-for="user in users" 
        :key="user"
        :class="['user-button', user === currentUser ? 'active' : '']"
        @click="switchUser(user)"
      >
        {{ user }}
      </button>
    </div>
    
    <div class="card points-card">
      <div class="points-header">
        <span>{{ currentUser }}的积分</span>
        <span class="trophy-emoji">🏆</span>
      </div>
      <div class="points-value">{{ totalPoints }}</div>
    </div>
    
    <div class="card chart-card">
      <div class="chart-container">
        <v-chart ref="chartRef" class="echarts" />
      </div>
    </div>
    
    <div class="buttons-container">
      <button class="add-button" @click="openAddDialog">+ 增加积分</button>
      <button class="reduce-button" @click="openReduceDialog">- 减少积分</button>
    </div>
    
    <div class="card records-card">
      <h3>积分记录</h3>
      <div class="records-list">
        <div v-for="record in pointsRecords" :key="record.id" class="record-item">
          <div class="record-info">
            <span>{{ record.description }}</span>
            <span class="record-date">{{ record.created_at }}</span>
          </div>
          <span :class="['record-points', record.points > 0 ? 'positive' : 'negative']">
            {{ record.points > 0 ? '+' : '' }}{{ record.points }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 积分操作弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <h3>{{ dialogType === 'add' ? '增加积分' : '减少积分' }}</h3>
        
        <div class="dialog-form">
          <div class="form-group">
            <label for="points">积分数量:</label>
            <input 
              type="number" 
              id="points" 
              v-model="dialogPoints" 
              min="1"
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="description">描述:</label>
            <input 
              type="text" 
              id="description" 
              v-model="dialogDescription"
              class="form-control"
            />
          </div>
        </div>
        
        <div class="dialog-buttons">
          <button class="cancel-button" @click="closeDialog">取消</button>
          <button 
            :class="['submit-button', dialogType === 'add' ? 'add-button' : 'reduce-button']"
            @click="submitPointsChange"
          >
            确定
          </button>
        </div>
      </div>
    </div>
    
    <!-- 悬浮按钮 -->
    <button class="floating-button" @click="toggleRulesPanel">
      <span class="rules-icon">📋</span>
    </button>
    
    <!-- 积分规则浮层 -->
    <div v-if="showRulesPanel" class="rules-overlay" @click="toggleRulesPanel">
      <div class="rules-panel" @click.stop>
        <div class="rules-header">
          <h3>积分规则</h3>
          <!--<button class="close-button" @click="toggleRulesPanel">×</button>-->
        </div>
        
        <div class="rules-content">
          <div class="rules-section">
            <h4>如何获得积分</h4>
            <div class="rule-item" v-for="(rule, index) in pointsRules" :key="'earn-'+index">
              <div class="rule-title">
                <span>{{ rule.title }}</span>
                <span class="rule-points positive">+{{ rule.points }}</span>
              </div>
              <div class="rule-description">{{ rule.description }}</div>
            </div>
          </div>
          
          <div class="rules-section">
            <h4>积分兑换奖励</h4>
            <div class="rule-item" v-for="(reward, index) in pointsRewards" :key="'reward-'+index">
              <div class="rule-title">
                <span>{{ reward.title }}</span>
                <span class="rule-points negative">-{{ reward.points }}</span>
              </div>
              <div class="rule-description">{{ reward.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.points-container {
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 60px; /* 为悬浮按钮留出空间 */
}

/* 用户切换样式 */
.user-switcher {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
  gap: 10px;
}

.user-button {
  padding: 8px 16px;
  border: 2px solid #ddd;
  background-color: white;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.user-button.active {
  background-color: #4080ff;
  color: white;
  border-color: #4080ff;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  width: 100%;
  box-sizing: border-box;
}

.points-card {
  padding: 16px;
}

.points-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.trophy-emoji {
  font-size: 24px;
}

.points-value {
  font-size: 36px;
  font-weight: bold;
}

.chart-card {
  padding: 0;
}

.chart-container {
  width: 100%;
  margin: 0;
  padding: 0;
}

.echarts {
  width: 100% !important;
  height: 200px;
}

.buttons-container {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.add-button {
  background-color: #4caf50;
  color: white;
}

.reduce-button {
  background-color: #f44336;
  color: white;
}

.records-card {
  padding: 16px;
}

.records-list {
  max-height: 300px;
  overflow-y: auto;
}

.record-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.record-info {
  display: flex;
  flex-direction: column;
}

.record-date {
  font-size: 12px;
  color: #888;
}

.record-points {
  font-weight: bold;
}

.positive {
  color: #4caf50;
}

.negative {
  color: #f44336;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

h3 {
  text-align: center;
}

.dialog-form {
  margin: 20px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
}

.dialog-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.cancel-button {
  background-color: #f5f5f5;
  color: #333;
}

.submit-button {
  /*flex: 0 0 auto;*/
}

/* 悬浮按钮样式 */
.floating-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: #4080ff;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 100;
  flex: none;
  padding: 0;
  transition: transform 0.3s, background-color 0.3s;
}

.floating-button:hover {
  transform: scale(1.1);
  background-color: #3060dd;
}

.rules-icon {
  font-size: 24px;
}

/* 积分规则浮层样式 */
.rules-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.rules-panel {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.rules-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rules-header h3 {
  margin: auto;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #888;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
}

.close-button:hover {
  background-color: #f5f5f5;
}

.rules-content {
  padding: 16px;
  overflow-y: auto;
}

.rules-section {
  margin-bottom: 24px;
}

.rules-section h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

h4 {
  text-align: center;
}

.rule-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}

.rule-title {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  margin-bottom: 4px;
}

.rule-points {
  font-weight: bold;
}

.rule-description {
  color: #666;
  font-size: 14px;
}
</style> 