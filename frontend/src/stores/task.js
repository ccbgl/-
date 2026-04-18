import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/api/request'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 获取任务列表
  const fetchTasks = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await request.get('/api/v1/tasks/')
      tasks.value = response.data || []
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch tasks:', err)
      tasks.value = []
    } finally {
      loading.value = false
    }
  }

  // 创建任务
  const createTask = async (formData) => {
    loading.value = true
    error.value = null
    try {
      const response = await request.post('/api/v1/tasks/', formData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to create task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取单个任务
  const fetchTask = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await request.get(`/api/v1/tasks/${id}/`)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除任务
  const deleteTask = async (id) => {
    loading.value = true
    error.value = null
    try {
      await request.delete(`/api/v1/tasks/${id}/`)
    } catch (err) {
      error.value = err.message
      console.error('Failed to delete task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    fetchTask,
    deleteTask
  }
})