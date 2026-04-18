import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '', // 使用相对路径，依赖 Vite 代理
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const auth = useAuthStore()
    if (auth.token) {
      // 关键修复：确保添加 Bearer 前缀
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  },
  error => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const { status, data } = error.response

      if (status === 401) {
        // Token 过期或无效，清除本地状态并跳转登录页
        const auth = useAuthStore()
        auth.logout()
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
      } else {
        const message = data?.detail || data?.message || '请求失败'
        ElMessage.error(message)
      }
    } else {
      ElMessage.error('网络错误，请检查服务器连接')
    }
    return Promise.reject(error)
  }
)

export default request