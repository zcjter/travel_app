<template>
  <div id="cloudjourney-app">
    <NavBar @show-login="loginVisible = true" />
    <main>
      <router-view />
    </main>

    <!-- 登录对话框 -->
    <el-dialog
      v-model="loginVisible"
      title="登录云途"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        size="large"
        @keyup.enter="handleSubmit"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <div style="display: flex; gap: 12px; width: 100%;">
            <el-button type="primary" :loading="loading" style="flex: 1" @click="handleSubmit">
              登录
            </el-button>
            <el-button :loading="loading" style="flex: 1" @click="handleRegister">
              注册
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <div v-if="error" style="color: var(--cj-danger); text-align: center; font-size: 14px;">
        {{ error }}
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const loginVisible = ref(false)
const loading = ref(false)
const error = ref('')
const form = ref({ username: '', password: '' })
const formRef = ref(null)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    loginVisible.value = false
    form.value = { username: '', password: '' }
    ElMessage.success('登录成功')
  } catch (e) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(form.value.username, form.value.password)
    loginVisible.value = false
    form.value = { username: '', password: '' }
    ElMessage.success('注册成功')
  } catch (e) {
    error.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 自动显示登录对话框（首次使用且未登录时）
  if (!authStore.isAuthenticated) {
    // 不强制登录，让用户自由浏览
  }
})
</script>
