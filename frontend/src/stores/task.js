import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/request'
import { ElMessage } from 'element-plus'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const plans = ref([])
  const executions = ref([])
  const loading = ref(false)

  // 获取任务列表
  const fetchTasks = async (params = {}) => {
    loading.value = true
    try {
      const res = await api.get('/tasks', { params })
      tasks.value = res.items || res
      return tasks.value
    } catch (error) {
      ElMessage.error('获取任务列表失败')
      return []
    } finally {
      loading.value = false
    }
  }

  // 创建任务
  const createTask = async (data) => {
    try {
      const res = await api.post('/tasks', {
        ...data,
        repo_url: data.repo_url || import.meta.env.VITE_APP_REPO_URL
      })
      ElMessage.success('任务创建成功')
      return res
    } catch (error) {
      ElMessage.error(error.message || '创建失败')
      throw error
    }
  }

  // 获取任务下的计划
  const fetchPlans = async (taskId) => {
    try {
      const res = await api.get(`/tasks/${taskId}/plans`)
      plans.value = res
      return res
    } catch (error) {
      ElMessage.error('获取计划列表失败')
      return []
    }
  }

  // 创建计划
  const createPlan = async (taskId, data) => {
    try {
      const res = await api.post(`/tasks/${taskId}/plans`, data)
      ElMessage.success('计划创建成功')
      return res
    } catch (error) {
      ElMessage.error(error.message || '创建失败')
      throw error
    }
  }

  // 触发执行
  const runPlan = async (planId, type = 'full') => {
    try {
      const res = await api.post(`/plans/${planId}/run`, { type })
      ElMessage.success('任务已加入执行队列')
      return res
    } catch (error) {
      ElMessage.error(error.message || '触发执行失败')
      throw error
    }
  }

  // 获取执行记录
  const fetchExecutions = async (planId) => {
    try {
      const res = await api.get(`/plans/${planId}/executions`)
      executions.value = res
      return res
    } catch (error) {
      ElMessage.error('获取执行记录失败')
      return []
    }
  }

  // 获取报告
  const fetchReport = async (execId) => {
    try {
      return await api.get(`/executions/${execId}/report`)
    } catch (error) {
      ElMessage.error('获取报告失败')
      throw error
    }
  }

  return {
    tasks,
    plans,
    executions,
    loading,
    fetchTasks,
    createTask,
    fetchPlans,
    createPlan,
    runPlan,
    fetchExecutions,
    fetchReport
  }
})