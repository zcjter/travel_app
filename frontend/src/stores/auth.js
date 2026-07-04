import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('cj_token') || '')
  const user = ref(localStorage.getItem('cj_user') || '')

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const res = await apiLogin(username, password)
    token.value = res.access_token
    user.value = username
    localStorage.setItem('cj_token', res.access_token)
    localStorage.setItem('cj_user', username)
  }

  async function register(username, password) {
    const res = await apiRegister(username, password)
    token.value = res.access_token
    user.value = username
    localStorage.setItem('cj_token', res.access_token)
    localStorage.setItem('cj_user', username)
  }

  function logout() {
    token.value = ''
    user.value = ''
    localStorage.removeItem('cj_token')
    localStorage.removeItem('cj_user')
  }

  // Listen for unauthorized events
  if (typeof window !== 'undefined') {
    window.addEventListener('auth:unauthorized', () => {
      logout()
    })
  }

  return { token, user, isAuthenticated, login, register, logout }
})
