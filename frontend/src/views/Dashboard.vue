<template>
  <div class="page-container">
    <h1 class="page-title">📊 数据看板</h1>

    <div v-if="loading" class="loading-container">
      <el-loading />
    </div>

    <div v-else-if="error" class="empty-container">
      <div class="empty-icon">⚠️</div>
      <div class="empty-text">数据加载失败</div>
      <el-button type="primary" @click="loadStats">重新加载</el-button>
    </div>

    <template v-else>
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-icon">{{ card.icon }}</div>
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 年度分布 -->
      <el-card class="chart-card">
        <template #header>
          <span>📈 年度旅程分布</span>
        </template>

        <div v-if="!yearlyData.length" class="empty-container" style="padding: 40px 0;">
          <div class="empty-text" style="font-size: 14px;">暂无数据</div>
        </div>

        <div v-else class="chart-container">
          <div class="chart-bars">
            <div
              v-for="item in yearlyData"
              :key="item.year"
              class="chart-bar-group"
            >
              <div class="chart-bar-wrapper">
                <div
                  class="chart-bar"
                  :style="{ height: barHeight(item.count) + '%' }"
                >
                  <span class="chart-bar-value">{{ item.count }}</span>
                </div>
              </div>
              <div class="chart-label">{{ item.year }}年</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 最近旅程快速入口 -->
      <el-card class="recent-card" v-if="recentTrips.length">
        <template #header>
          <span>🚀 最近旅程</span>
        </template>
        <div class="recent-list">
          <div
            v-for="trip in recentTrips"
            :key="trip.id"
            class="recent-item"
            @click="$router.push(`/trips/${trip.id}`)"
          >
            <span class="recent-icon">✈️</span>
            <div class="recent-info">
              <div class="recent-title">{{ trip.title }}</div>
              <div class="recent-meta">{{ trip.destination }} · {{ trip.start_date }}</div>
            </div>
            <el-tag size="small" :type="trip.status === 'completed' ? '' : trip.status === 'ongoing' ? 'success' : 'info'">
              {{ trip.status === 'completed' ? '已完成' : trip.status === 'ongoing' ? '进行中' : '计划中' }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchStats, fetchTrips } from '../api/index.js'

const loading = ref(true)
const error = ref('')
const stats = ref(null)
const recentTrips = ref([])
const maxCount = ref(1)

const statCards = computed(() => [
  { icon: '✈️', value: stats.value?.total_trips ?? '-', label: '旅程总数' },
  { icon: '📝', value: stats.value?.total_moments ?? '-', label: '记录总数' },
  { icon: '📷', value: stats.value?.total_photos ?? '-', label: '照片总数' },
  { icon: '🏙️', value: stats.value?.total_cities ?? '-', label: '到访城市' },
])

const yearlyData = computed(() => {
  const data = stats.value?.yearly_distribution || []
  if (data.length) {
    maxCount.value = Math.max(...data.map(d => d.count), 1)
  }
  return data
})

function barHeight(count) {
  return Math.max((count / maxCount.value) * 100, 5)
}

async function loadStats() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchStats()
    stats.value = res.data
  } catch (e) {
    error.value = e.message
    ElMessage.error('统计数据加载失败')
  } finally {
    loading.value = false
  }
}

async function loadRecentTrips() {
  try {
    const res = await fetchTrips()
    recentTrips.value = (res.data || []).slice(0, 5)
  } catch {
    // ignore
  }
}

onMounted(() => {
  loadStats()
  loadRecentTrips()
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 8px 0;
  cursor: default;
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--cj-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--cj-text-secondary);
  margin-top: 4px;
}

.chart-card,
.recent-card {
  margin-bottom: 24px;
}

.chart-container {
  padding: 20px 0 0;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 200px;
  padding: 0 20px;
}

.chart-bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.chart-bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.chart-bar {
  width: 60%;
  min-width: 24px;
  max-width: 60px;
  background: linear-gradient(180deg, var(--cj-primary-light), var(--cj-primary));
  border-radius: 6px 6px 0 0;
  position: relative;
  transition: height 0.3s;
  min-height: 8px;
}

.chart-bar:hover {
  background: linear-gradient(180deg, var(--cj-accent), var(--cj-accent-hover));
}

.chart-bar-value {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 700;
  color: var(--cj-primary);
}

.chart-label {
  margin-top: 8px;
  font-size: 12px;
  color: var(--cj-text-secondary);
  text-align: center;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.recent-item:hover {
  background: #f3f4f6;
}

.recent-icon {
  font-size: 20px;
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-size: 15px;
  font-weight: 600;
}

.recent-meta {
  font-size: 12px;
  color: var(--cj-text-secondary);
}
</style>
