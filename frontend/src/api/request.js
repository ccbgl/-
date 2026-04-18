import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const auth = useAuthStore()
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const { code, message, data } = response.data
    // 假设后端统一返回 { code: 200, message: 'success', data: {...} }
    if (code === 200 || code === undefined) {
      return data !== undefined ? data : response.data
    }
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || 'Error'))
  },
  error => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      ElMessage.error('权限不足')
    } else if (error.response?.status === 404) {
      ElMessage.error('接口不存在')
    } else {
      ElMessage.error(error.message || '网络异常')
    }
    return Promise.reject(error)
  }
)

// 导出常用请求方法
export const api = {
  get: (url, params, config) => request.get(url, { params, ...config }),
  post: (url, data, config) => request.post(url, data, config),
  put: (url, data, config) => request.put(url, data, config),
  delete: (url, config) => request.delete(url, config)
}

export default request