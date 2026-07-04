<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">我的旅程</h1>
        <p style="color: var(--cj-text-secondary); margin-top: -12px; font-size: 14px;">
          记录走过的每一段路
        </p>
      </div>
      <el-button type="primary" size="large" @click="showCreate = true">
        ✈️ 创建旅程
      </el-button>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <el-select v-model="yearFilter" placeholder="按年份筛选" clearable @change="loadTrips">
        <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
      </el-select>
      <span class="trip-count">共 {{ trips.length }} 段旅程</span>
    </div>

    <!-- 旅程列表 -->
    <div v-if="loading" class="loading-container">
      <el-loading />
    </div>

    <div v-else-if="trips.length === 0" class="empty-container">
      <div class="empty-icon">🧳</div>
      <div class="empty-text">还没有旅程记录</div>
      <div class="empty-hint">点击「创建旅程」开始吧</div>
    </div>

    <div v-else class="trip-grid">
      <TripCard v-for="trip in trips" :key="trip.id" :trip="trip" />
    </div>

    <!-- 创建旅程对话框 -->
    <el-dialog v-model="showCreate" title="创建旅程" width="560px">
      <el-form :model="form" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="封面">
          <div class="cover-upload">
            <img v-if="form.cover_image" :src="form.cover_image" class="cover-preview" />
            <el-upload
              :show-file-list="false"
              :http-request="handleCoverUpload"
              accept="image/*"
            >
              <el-button size="small">{{ form.cover_image ? '更换' : '上传封面' }}</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="名称" prop="title">
          <el-input v-model="form.title" placeholder="给这段旅程取个名字" />
        </el-form-item>
        <el-form-item label="目的地">
          <el-input v-model="form.destination" placeholder="例如：云南大理" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="预算">
          <el-input-number v-model="form.budget" :min="0" :step="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="计划中" value="planning" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="写一段旅程寄语..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createTrip, uploadCover } from '../api/index.js'
import { useTripsStore } from '../stores/trips'
import TripCard from '../components/TripCard.vue'

const tripsStore = useTripsStore()
const trips = ref([])
const loading = ref(true)
const showCreate = ref(false)
const submitting = ref(false)
const yearFilter = ref('')
const formRef = ref(null)

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 10 }, (_, i) => currentYear - i)

const form = ref({
  title: '',
  destination: '',
  budget: null,
  status: 'planning',
  description: '',
  cover_image: '',
})

async function handleCoverUpload(options) {
  try {
    const res = await uploadCover(options.file)
    form.value.cover_image = res.data.url
    ElMessage.success('封面上传成功')
  } catch (e) {
    ElMessage.error('封面上传失败: ' + (e.message || ''))
  }
}

const dateRange = ref(null)

const rules = {
  title: [{ required: true, message: '请输入旅程名称', trigger: 'blur' }],
}

async function loadTrips() {
  loading.value = true
  try {
    const params = {}
    if (yearFilter.value) params.year = yearFilter.value
    await tripsStore.fetchTrips(params)
    trips.value = tripsStore.trips
  } catch (e) {
    ElMessage.error('加载失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { ...form.value }
    if (dateRange.value) {
      data.start_date = dateRange.value[0]
      data.end_date = dateRange.value[1]
    }
    await createTrip(data)
    ElMessage.success('旅程创建成功')
    showCreate.value = false
    form.value = { title: '', destination: '', budget: null, status: 'planning', description: '', cover_image: '' }
    dateRange.value = null
    await loadTrips()
  } catch (e) {
    ElMessage.error('创建失败: ' + e.message)
  } finally {
    submitting.value = false
  }
}

onMounted(loadTrips)
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.trip-count {
  font-size: 14px;
  color: var(--cj-text-secondary);
}

.trip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.cover-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cover-preview {
  width: 120px;
  height: 72px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--cj-border);
}
</style>
