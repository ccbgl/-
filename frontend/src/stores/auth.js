import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 安全地获取本地存储中的数据
  const getStoredToken = () => {
    try {
      const tokenStr = localStorage.getItem('token')
      return tokenStr ? JSON.parse(tokenStr) : null
    } catch (e) {
      console.error('Failed to parse token from localStorage:', e)
      localStorage.removeItem('token') // 清除损坏的数据
      return null
    }
  }

  const getStoredUser = () => {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
      localStorage.removeItem('user') // 清除损坏的数据
      return null
    }
  }

  const token = ref(getStoredToken())
  const user = ref(getStoredUser())

  const isLoggedIn = computed(() => !!token.value)

  function login(newToken, newUser) {
    token.value = newToken
    user.value = newUser

    // 安全地存储到本地
    try {
      localStorage.setItem('token', JSON.stringify(newToken))
      localStorage.setItem('user', JSON.stringify(newUser))
    } catch (e) {
      console.error('Failed to save auth data to localStorage:', e)
    }
  }

  function logout() {
    token.value = null
    user.value = null

    try {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    } catch (e) {
      console.error('Failed to clear auth data from localStorage:', e)
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout
  }
})