<template>
  <div class="home-page">
    <!-- 首页横幅 -->
    <section class="hero-section">
      <svg class="china-map-bg" viewBox="0 0 500 500" preserveAspectRatio="xMidYMid meet">
        <path d="M320,30 L340,35 L350,55 L345,75 L335,85 L340,100 L335,115
                 L345,125 L350,140 L335,145 L340,155 L330,165 L320,175
                 L335,185 L345,195 L335,205 L325,215 L340,225 L350,240
                 L335,250 L320,260 L310,270 L295,275 L285,285 L270,290
                 L255,285 L240,290 L225,285 L210,290 L195,285
                 L180,290 L165,285 L150,280 L140,270 L130,275
                 L115,270 L105,260 L95,245 L85,235 L75,225
                 L65,210 L55,200 L45,190 L40,175 L50,165
                 L60,155 L70,145 L80,135 L90,125 L100,115
                 L120,110 L140,100 L160,90 L180,80 L200,70
                 L220,60 L240,50 L260,45 L280,40 L300,35 Z
                 M345,75 L350,85 L345,95 L335,90 Z
                 M290,145 L300,150 L295,160 L285,155 Z
                 M310,270 L320,280 L315,290 L305,285 Z"
              fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="3" />
        <!-- 简化省界线 -->
        <path d="M200,70 L180,140 L150,180 L120,200 L95,245
                 M180,80 L220,130 L260,140 L300,150
                 M240,50 L250,100 L280,130
                 M140,100 L165,150 L195,200 L210,290"
              fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="4,4" />
      </svg>
      <div class="hero-overlay">
        <h1 class="hero-title">云途</h1>
        <p class="hero-subtitle">记录每一段旅程，珍藏每一刻回忆</p>
      </div>
    </section>

    <!-- 最近的旅行 -->
    <section class="page-container">
      <div class="page-header">
        <h2 class="section-title">最近的旅行</h2>
        <el-button type="primary" @click="$router.push('/trips')">
          查看全部
        </el-button>
      </div>

      <div v-if="loading" class="loading-container">
        <el-loading text="加载中..." />
      </div>

      <div v-else-if="recentTrips.length === 0" class="empty-container">
        <div class="empty-icon">🗺️</div>
        <div class="empty-text">还没有旅程记录</div>
        <div class="empty-hint">点击右上角「发布」开始记录你的第一段旅程</div>
        <el-button type="primary" style="margin-top: 16px;" @click="$router.push('/editor')">
          开始记录
        </el-button>
      </div>

      <div v-else class="trip-grid">
        <TripCard v-for="trip in recentTrips" :key="trip.id" :trip="trip" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchTrips } from '../api/index.js'
import TripCard from '../components/TripCard.vue'

const trips = ref([])
const loading = ref(true)

const recentTrips = computed(() => trips.value.slice(0, 3))

onMounted(async () => {
  try {
    const res = await fetchTrips()
    trips.value = res.data || []
  } catch (e) {
    console.error('加载失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hero-section {
  position: relative;
  width: 100%;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a365d 0%, #2d5a87 50%, #4a7fb5 100%);
  overflow: hidden;
}

.china-map-bg {
  position: absolute;
  width: 70%;
  height: 70%;
  opacity: 0.6;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.hero-overlay {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 32px 48px;
  color: #fff;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: 4px;
  margin-bottom: 8px;
}

.hero-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--cj-primary-dark);
}

.trip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}
</style>
