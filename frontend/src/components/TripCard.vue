<template>
  <el-card class="trip-card" :body-style="{ padding: '0' }" shadow="hover">
    <div class="trip-cover" @click="goToDetail">
      <img
        v-if="trip.cover_image"
        :src="trip.cover_image"
        :alt="trip.title"
        loading="lazy"
      />
      <div v-else class="cover-placeholder">
        <span>📸</span>
      </div>
      <el-tag
        :type="statusType"
        size="small"
        class="trip-status"
        effect="dark"
      >
        {{ statusText }}
      </el-tag>
    </div>
    <div class="trip-body" @click="goToDetail">
      <h3 class="trip-title">{{ trip.title }}</h3>
      <p v-if="trip.destination" class="trip-destination">
        <span>📍</span> {{ trip.destination }}
      </p>
      <p class="trip-date">
        <span>📅</span>
        {{ formatDate(trip.start_date) }} ~ {{ formatDate(trip.end_date) }}
      </p>
      <p v-if="trip.description" class="trip-desc">
        {{ trip.description.slice(0, 80) }}{{ trip.description.length > 80 ? '...' : '' }}
      </p>
    </div>
    <div v-if="trip.budget" class="trip-footer">
      <span class="trip-budget">💰 预算: ¥{{ trip.budget.toLocaleString() }}</span>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  trip: { type: Object, required: true },
})

const router = useRouter()

const statusType = computed(() => {
  const map = { planning: 'info', ongoing: 'success', completed: '' }
  return map[props.trip.status] || 'info'
})

const statusText = computed(() => {
  const map = { planning: '计划中', ongoing: '进行中', completed: '已完成' }
  return map[props.trip.status] || '计划中'
})

function formatDate(d) {
  if (!d) return '—'
  return d.slice(0, 10)
}

function goToDetail() {
  router.push(`/trips/${props.trip.id}`)
}
</script>

<style scoped>
.trip-card {
  cursor: pointer;
}

.trip-cover {
  position: relative;
  height: 180px;
  overflow: hidden;
  background: #e5e7eb;
}

.trip-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.trip-card:hover .trip-cover img {
  transform: scale(1.06);
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
}

.trip-status {
  position: absolute;
  top: 10px;
  right: 10px;
}

.trip-body {
  padding: 16px;
}

.trip-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--cj-primary-dark);
}

.trip-destination,
.trip-date {
  font-size: 13px;
  color: var(--cj-text-secondary);
  margin-bottom: 4px;
}

.trip-desc {
  font-size: 14px;
  color: #555;
  margin-top: 8px;
  line-height: 1.5;
}

.trip-footer {
  padding: 10px 16px;
  border-top: 1px solid var(--cj-border);
  font-size: 13px;
  color: var(--cj-text-secondary);
}
</style>
