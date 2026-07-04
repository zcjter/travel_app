<template>
  <div class="page-container">
    <h1 class="page-title">
      {{ isEdit ? '编辑记录' : '发布新记录' }}
    </h1>

    <div class="editor-main">
        <el-card>
          <el-form :model="form" label-width="80px">
            <el-form-item label="关联旅程">
              <el-select
                v-model="form.trip_id"
                placeholder="选择旅程"
                style="width: 100%"
                :disabled="!!route.params.tripId"
              >
                <el-option
                  v-for="t in tripOptions"
                  :key="t.id"
                  :label="t.title"
                  :value="t.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="文字记录">
              <el-input
                v-model="form.content"
                type="textarea"
                :rows="5"
                placeholder="此刻的感悟、见闻、心情..."
              />
            </el-form-item>

            <el-form-item label="地点名称">
              <el-input v-model="form.location_name" placeholder="例如：大理古城" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 上传区域 -->
        <el-card style="margin-top: 16px;">
          <template #header>
            <span>📷 上传照片</span>
          </template>

          <el-upload
            drag
            multiple
            :auto-upload="true"
            :http-request="handleUpload"
            :file-list="fileList"
            list-type="picture-card"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
          >
            <el-icon style="font-size: 28px;"><Plus /></el-icon>
            <div style="font-size: 14px; color: #666; margin-top: 8px;">
              拖拽照片到此处，或点击上传
            </div>
          </el-upload>

          <!-- EXIF 信息 -->
          <div v-if="uploadedExif.length" class="exif-section">
            <h4>照片信息</h4>
            <div v-for="(exif, idx) in uploadedExif" :key="idx" class="exif-item">
              <div class="exif-header">
                <span class="exif-index">#{{ idx + 1 }}</span>
                <span v-if="exif.datetime">📅 {{ exif.datetime }}</span>
                <span v-if="exif.camera_model">📷 {{ exif.camera_model }}</span>
              </div>
              <div class="exif-detail">
                <span v-if="exif.aperture">光圈 {{ exif.aperture }}</span>
                <span v-if="exif.shutter_speed">快门 {{ exif.shutter_speed }}</span>
                <span v-if="exif.iso">ISO {{ exif.iso }}</span>
                <span v-if="exif.focal_length">焦距 {{ exif.focal_length }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <div style="margin-top: 16px; text-align: right;">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '发布记录' }}
          </el-button>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { fetchTrips, uploadFile, createMoment, updateMoment, fetchMoment } from '../api/index.js'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.query.momentId)
const tripOptions = ref([])
const fileList = ref([])
const uploadedFiles = ref([])  // { id, url, thumbnail_url, exif }
const uploadedExif = ref([])
const submitting = ref(false)

const form = ref({
  trip_id: route.params.tripId ? Number(route.params.tripId) : '',
  content: '',
  location_name: '',
})

let uidCounter = Date.now()

function addFileRecord(media, exif) {
  const uid = ++uidCounter
  fileList.value.push({
    uid,
    name: `photo_${uid}.jpg`,
    url: media.thumbnail_url || media.url || media.file_path,
    status: 'done',
  })
  uploadedFiles.value.push({ ...media, _uid: uid })
  if (exif) uploadedExif.value.push(exif)
}

async function loadTrips() {
  try {
    const res = await fetchTrips()
    tripOptions.value = res.data || []
  } catch {
    tripOptions.value = []
  }
}

async function loadMoment() {
  const id = route.query.momentId
  if (!id) return
  try {
    const res = await fetchMoment(id)
    const data = res.data
    form.value = {
      trip_id: data.trip_id,
      content: data.content || '',
      location_name: data.location_name || '',
    }
    // 加载已有图片
    if (data.media_list) {
      data.media_list.forEach(m => {
        addFileRecord(m, null)
      })
    }
  } catch {
    ElMessage.error('加载记录失败')
  }
}

async function handleUpload(options) {
  const file = options.file
  try {
    const res = await uploadFile(file)
    const data = res.data
    addFileRecord(data, data.exif)
    ElMessage.success(`上传成功: ${file.name}`)
  } catch (e) {
    ElMessage.error('上传失败: ' + (e.message || ''))
  }
}

function handleRemove(file) {
  const idx = uploadedFiles.value.findIndex(f => f._uid === file.uid)
  if (idx > -1) {
    uploadedFiles.value.splice(idx, 1)
    if (uploadedExif.value.length > idx) uploadedExif.value.splice(idx, 1)
  }
}

function handlePreview(file) {
  const media = uploadedFiles.value.find(f => f._uid === file.uid)
  if (media) {
    window.open(media.file_path || media.url, '_blank')
  }
}

async function handleSubmit() {
  if (!form.value.trip_id) {
    ElMessage.warning('请选择关联旅程')
    return
  }

  submitting.value = true
  try {
    const data = {
      trip_id: form.value.trip_id,
      content: form.value.content,
      location_name: form.value.location_name,
      media_ids: uploadedFiles.value.map(f => f.id),
    }

    if (isEdit.value) {
      await updateMoment(route.query.momentId, data)
      ElMessage.success('记录已更新')
    } else {
      await createMoment(data)
      ElMessage.success('记录发布成功')
    }

    router.push(`/trips/${form.value.trip_id}`)
  } catch (e) {
    ElMessage.error('提交失败: ' + (e.message || ''))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadTrips()
  if (isEdit.value) loadMoment()
})
</script>

<style scoped>
.editor-main {
  max-width: 800px;
  margin: 0 auto;
}

.exif-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--cj-border);
}

.exif-section h4 {
  font-size: 14px;
  color: var(--cj-text-secondary);
  margin-bottom: 8px;
}

.exif-item {
  background: #f3f4f6;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #555;
}

.exif-header {
  display: flex;
  gap: 12px;
  font-weight: 600;
  margin-bottom: 4px;
}

.exif-index {
  color: var(--cj-primary);
}

.exif-detail {
  display: flex;
  gap: 12px;
  color: #888;
}

@media (max-width: 900px) {
  .editor-layout {
    flex-direction: column;
  }
  .editor-map {
    position: static;
  }
}
</style>
