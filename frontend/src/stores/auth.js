import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  // 尝试从本地存储恢复用户信息
  try {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  } catch (e) {
    console.error('Failed to parse user from localStorage', e)
    localStorage.removeItem('user')
  }

  const isAdmin = computed(() => user.value?.is_admin === true)
  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    try {
      const res = await request.post('/api/v1/auth/login', credentials)
      // 假设后端返回格式为 { access_token: "...", user: {...} }
      token.value = res.data.access_token
      user.value = res.data.user

      // 保存到本地存储
      localStorage.setItem('token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))

      return res.data
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAdmin,
    isAuthenticated,
    login,
    logout
  }
})