<template>
  <el-menu
    :default-active="activeRoute"
    mode="horizontal"
    class="cj-navbar"
    router
  >
    <div class="nav-brand">
      <el-menu-item index="/" class="brand-item">
        <span class="brand-icon">🗺️</span>
        <span class="brand-text">云途</span>
        <span class="brand-sub">CloudJourney</span>
      </el-menu-item>
    </div>

    <div class="nav-menu">
      <el-menu-item index="/">
        <span>🏠</span>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/trips">
        <span>📋</span>
        <span>旅程</span>
      </el-menu-item>
      <el-menu-item index="/editor">
        <span>✏️</span>
        <span>发布</span>
      </el-menu-item>
      <el-menu-item index="/dashboard">
        <span>📊</span>
        <span>数据</span>
      </el-menu-item>
    </div>

    <div class="nav-right">
      <template v-if="authStore.isAuthenticated">
        <el-dropdown trigger="click">
          <span class="user-info">
            <el-avatar :size="32" shape="circle">{{ authStore.user?.charAt(0) || 'U' }}</el-avatar>
            <span class="username">{{ authStore.user }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button size="small" type="primary" @click="$emit('showLogin')">
          登录
        </el-button>
      </template>
    </div>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineEmits(['showLogin'])

const route = useRoute()
const authStore = useAuthStore()

const activeRoute = computed(() => route.path)

function handleLogout() {
  authStore.logout()
}
</script>

<style scoped>
.cj-navbar {
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: linear-gradient(135deg, var(--cj-primary-dark), var(--cj-primary)) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  height: 60px;
}

.nav-brand {
  margin-right: 32px;
}

.brand-item {
  font-size: 18px !important;
  padding: 0 16px !important;
}

.brand-icon {
  font-size: 22px;
  margin-right: 6px;
}

.brand-text {
  font-weight: 700;
  color: #fff;
  margin-right: 6px;
}

.brand-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 300;
}

.nav-menu {
  flex: 1;
  display: flex;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 14px;
  gap: 4px;
}

.nav-menu .el-menu-item.is-active {
  color: #fff !important;
  border-bottom-color: var(--cj-accent) !important;
}

.nav-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #fff;
}

.username {
  font-size: 14px;
  color: #fff;
}
</style>
