<template>
  <div class="detail-page">
    <div v-if="loading" class="loading-container">
      <el-loading />
    </div>

    <div v-else-if="!trip" class="empty-container">
      <div class="empty-icon">🔍</div>
      <div class="empty-text">旅程不存在</div>
      <el-button type="primary" @click="$router.push('/trips')">返回列表</el-button>
    </div>

    <template v-else>
      <!-- 头部 -->
      <div class="detail-header">
        <img
          v-if="trip.cover_image"
          :src="trip.cover_image"
          :alt="trip.title"
          class="header-cover"
        />
        <div v-else class="header-cover placeholder">
          <span>🗺️</span>
        </div>
        <div class="header-info">
          <div class="header-meta">
            <el-tag :type="statusType" size="small" effect="dark">
              {{ statusText }}
            </el-tag>
            <el-button text size="small" @click="showEdit = true">✏️ 编辑</el-button>
            <el-popconfirm title="确定删除这个旅程？" @confirm="handleDelete">
              <template #reference>
                <el-button text size="small" type="danger">🗑️ 删除</el-button>
              </template>
            </el-popconfirm>
          </div>
          <h1 class="header-title">{{ trip.title }}</h1>
          <p v-if="trip.destination" class="header-location">📍 {{ trip.destination }}</p>
          <p class="header-date">📅 {{ trip.start_date }} ~ {{ trip.end_date }}</p>
          <p v-if="trip.description" class="header-desc">{{ trip.description }}</p>
        </div>
      </div>

      <!-- 主体: 时间轴 + 照片墙 -->
      <div class="detail-body">
        <div class="timeline-section">
          <div class="section-bar">
            <h2>📖 旅程记录</h2>
            <el-button type="primary" size="small" @click="$router.push(`/editor/${trip.id}`)">
              ✏️ 发布记录
            </el-button>
          </div>

          <div v-if="!moments.length" class="empty-container" style="padding: 40px 0;">
            <div class="empty-icon">📝</div>
            <div class="empty-text">还没有记录</div>
            <div class="empty-hint">点击「发布记录」添加第一条</div>
          </div>

          <el-timeline v-else>
            <el-timeline-item
              v-for="m in moments"
              :key="m.id"
              :timestamp="formatTime(m.created_at)"
              placement="top"
              :color="m.media_list?.length ? '#f59e0b' : '#2d5a87'"
            >
              <div class="moment-card">
                <div v-if="m.content" class="moment-content">{{ m.content }}</div>

                <!-- 图片预览（支持灯箱） -->
                <div v-if="m.media_list?.length" class="moment-media" v-viewer>
                  <img
                    v-for="media in m.media_list"
                    :key="media.id"
                    :src="media.thumbnail_path || media.file_path"
                    :data-src="media.file_path"
                    class="moment-thumb"
                  />
                </div>

                <div class="moment-footer">
                  <span v-if="m.location_name" class="moment-location">
                    📍 {{ m.location_name }}
                  </span>
                  <div class="moment-actions">
                    <el-button text size="small" @click="$router.push(`/editor/${trip.id}?momentId=${m.id}`)">
                      ✏️
                    </el-button>
                    <el-popconfirm title="删除这条记录？" @confirm="handleDeleteMoment(m.id)">
                      <template #reference>
                        <el-button text size="small" type="danger">
                          🗑️
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>

        </div>
      </div>
    </template>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEdit" title="编辑旅程" width="560px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="封面">
          <div class="cover-upload">
            <img v-if="editForm.cover_image" :src="editForm.cover_image" class="cover-preview" />
            <el-upload
              :show-file-list="false"
              :http-request="handleCoverUpload"
              accept="image/*"
            >
              <el-button size="small">{{ editForm.cover_image ? '更换' : '上传封面' }}</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="目的地">
          <el-input v-model="editForm.destination" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="计划中" value="planning" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleUpdate">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useTripsStore } from '../stores/trips'
import { fetchMoments as apiFetchMoments, deleteMoment, uploadCover } from '../api/index.js'

const route = useRoute()
const router = useRouter()
const tripsStore = useTripsStore()

const trip = ref(null)
const moments = ref([])
const loading = ref(true)
const showEdit = ref(false)
const saving = ref(false)

const editForm = ref({
  title: '', destination: '', status: 'planning', description: '',
})

const statusType = computed(() => {
  const map = { planning: 'info', ongoing: 'success', completed: '' }
  return map[trip.value?.status] || 'info'
})

const statusText = computed(() => {
  const map = { planning: '计划中', ongoing: '进行中', completed: '已完成' }
  return map[trip.value?.status] || '计划中'
})

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadData() {
  loading.value = true
  try {
    await tripsStore.fetchTrip(route.params.id)
    trip.value = tripsStore.currentTrip

    if (trip.value) {
      // 获取 moments
      const res = await apiFetchMoments(route.params.id)
      moments.value = res.data || []
    }
  } catch (e) {
    ElMessage.error('加载失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function handleCoverUpload(options) {
  try {
    const res = await uploadCover(options.file)
    editForm.value.cover_image = res.data.url
    ElMessage.success('封面上传成功')
  } catch (e) {
    ElMessage.error('封面上传失败: ' + (e.message || ''))
  }
}

async function handleUpdate() {
  saving.value = true
  try {
    await tripsStore.updateTrip(trip.value.id, editForm.value)
    ElMessage.success('更新成功')
    showEdit.value = false
    Object.assign(trip.value, editForm.value)
  } catch (e) {
    ElMessage.error('更新失败: ' + e.message)
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await tripsStore.deleteTrip(trip.value.id)
    ElMessage.success('已删除')
    router.push('/trips')
  } catch (e) {
    ElMessage.error('删除失败: ' + e.message)
  }
}

async function handleDeleteMoment(id) {
  try {
    await deleteMoment(id)
    moments.value = moments.value.filter(m => m.id !== id)
    ElMessage.success('记录已删除')
  } catch (e) {
    ElMessage.error('删除失败: ' + e.message)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}

.detail-header {
  display: flex;
  gap: 24px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.header-cover {
  width: 360px;
  height: 240px;
  object-fit: cover;
  flex-shrink: 0;
}

.header-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
}

.header-info {
  flex: 1;
  padding: 20px 20px 20px 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.header-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--cj-primary-dark);
  margin-bottom: 8px;
}

.header-location,
.header-date {
  font-size: 14px;
  color: var(--cj-text-secondary);
  margin-bottom: 4px;
}

.header-desc {
  font-size: 14px;
  color: #555;
  margin-top: 8px;
  line-height: 1.6;
}

.detail-body {
  display: flex;
  gap: 24px;
}

.timeline-section {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-bar h2 {
  font-size: 20px;
  font-weight: 700;
}

.moment-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 4px;
}

.moment-content {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.moment-media {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.moment-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s;
}

.moment-thumb:hover {
  transform: scale(1.1);
}

.moment-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--cj-text-secondary);
}

.moment-location {
  color: var(--cj-primary);
}

.moment-actions {
  margin-left: auto;
  display: flex;
  gap: 4px;
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

@media (max-width: 900px) {
  .detail-header {
    flex-direction: column;
  }
  .header-cover {
    width: 100%;
    height: 200px;
  }
  .header-info {
    padding: 0 16px 16px;
  }
}
</style>
