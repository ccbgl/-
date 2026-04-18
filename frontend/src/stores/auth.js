import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/request'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 登录
  const login = async (username, password) => {
    try {
      const res = await api.post('/auth/login', { username, password })
      token.value = res.token
      user.value = res.user
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(res.user))
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
      return false
    }
  }

  // 注册（仅admin可创建普通用户）
  const register = async (username, password) => {
    try {
      const res = await api.post('/auth/register', { username, password, role: 'user' })
      ElMessage.success('用户创建成功')
      return res
    } catch (error) {
      ElMessage.error(error.message || '创建失败')
      throw error
    }
  }

  // 退出
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.info('已退出登录')
  }

  // 刷新用户信息
  const refreshUser = async () => {
    if (!token.value) return
    try {
      const res = await api.get('/auth/me')
      user.value = res
      localStorage.setItem('user', JSON.stringify(res))
    } catch (error) {
      logout()
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    refreshUser
  }
})