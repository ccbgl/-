<template>
  <div class="plan-detail">
    <!-- 返回头部 -->
    <el-page-header @back="router.back()" content="执行状态监控" class="page-header" />

    <el-main class="main">
      <!-- 计划信息 -->
      <el-card class="plan-info">
        <template #header>
          <div class="card-header">
            <span>🎯 {{ plan?.name }}</span>
            <StatusTag :status="plan?.status === 'active' ? 'success' : 'info'" effect="plain">
              {{ plan?.status === 'active' ? '已启用' : '已禁用' }}
            </StatusTag>
          </div>
        </template>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="类型">{{ getTypeText(plan?.plan_type) }}</el-descriptions-item>
          <el-descriptions-item label="Cron表达式">{{ plan?.cron_expr || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ plan?.created_at || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 执行操作 -->
      <el-card class="action-card">
        <el-space wrap>
          <el-button
            type="success"
            @click="runPlan('full')"
            :loading="running && runType === 'full'"
          >
            <el-icon><VideoPlay /></el-icon> 执行全量
          </el-button>
          <el-button
            type="warning"
            @click="runPlan('suite')"
            :loading="running && runType === 'suite'"
          >
            <el-icon><Collection /></el-icon> 执行测试套
          </el-button>
          <el-button @click="refreshExecutions">
            <el-icon><Refresh /></el-icon> 刷新列表
          </el-button>
        </el-space>
      </el-card>

      <!-- 执行记录 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>📊 执行记录</span>
            <el-text size="small" type="info">
              共 {{ taskStore.executions.length }} 条
            </el-text>
          </div>
        </template>

        <LoadingSpinner :loading="taskStore.loading">
          <el-table :data="taskStore.executions" border stripe>
            <el-table-column type="expand">
              <template #default="{ row }">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="开始时间">{{ row.start_time || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="结束时间">{{ row.end_time || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="耗时" :span="2">
                    {{ calculateDuration(row.start_time, row.end_time) }}
                  </el-descriptions-item>
                </el-descriptions>
                <el-divider />
                <el-text v-if="row.logs" size="small" type="info">
                  <pre class="logs">{{ row.logs }}</pre>
                </el-text>
              </template>
            </el-table-column>

            <el-table-column prop="id" label="记录ID" width="90" />
            <el-table-column prop="start_time" label="开始时间" width="180" sortable />

            <el-table-column label="状态" width="120" align="center">
              <template #default="{ row }">
                <StatusTag :status="row.status" />
              </template>
            </el-table-column>

            <el-table-column label="报告" min-width="150">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'success' && row.report_url"
                  type="success"
                  size="small"
                  @click="openReport(row.report_url)"
                >
                  <el-icon><Document /></el-icon> 查看报告
                </el-button>
                <el-text v-else-if="row.status === 'failed'" size="small" type="danger">
                  执行失败
                </el-text>
                <el-text v-else size="small" type="info">
                  生成中...
                </el-text>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.logs"
                  link
                  type="info"
                  size="small"
                  @click="ElMessage.info('日志已展开')"
                >
                  查看日志
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </LoadingSpinner>

        <el-empty
          v-if="!taskStore.loading && taskStore.executions.length === 0"
          description="暂无执行记录"
          :image-size="100"
        />
      </el-card>
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { ElMessage } from 'element-plus'
import { VideoPlay, Collection, Refresh, Document } from '@element-plus/icons-vue'
import StatusTag from '@/components/StatusTag.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()

const planId = ref(route.params.id)
const plan = ref(null)
const running = ref(false)
const runType = ref(null)

onMounted(async () => {
  await taskStore.fetchPlans() // 获取所有计划用于查找当前计划
  plan.value = taskStore.plans.find(p => p.id == planId.value)
  if (!plan.value) {
    ElMessage.error('计划不存在')
    router.back()
    return
  }
  await fetchExecutions()

  // 定时刷新执行状态（仅当有运行中的任务时）
  startAutoRefresh()
})

const fetchExecutions = async () => {
  await taskStore.fetchExecutions(planId.value)
}

const startAutoRefresh = () => {
  const interval = setInterval(async () => {
    const hasRunning = taskStore.executions.some(e => e.status === 'running' || e.status === 'pending')
    if (hasRunning) {
      await fetchExecutions()
    } else {
      clearInterval(interval)
    }
  }, 10000) // 每10秒刷新一次
}

const getTypeText = (type) => {
  const map = { full: '全量执行', suite: '测试套', scheduled: '定时任务' }
  return map[type] || type
}

const runPlan = async (type) => {
  running.value = true
  runType.value = type
  try {
    await taskStore.runPlan(planId.value, type)
    ElMessage.success('任务已加入执行队列')
    await fetchExecutions()
  } catch (error) {
    console.error('Run plan error:', error)
  } finally {
    running.value = false
    runType.value = null
  }
}

const refreshExecutions = async () => {
  ElMessage.info('刷新中...')
  await fetchExecutions()
  ElMessage.success('刷新完成')
}

const openReport = (url) => {
  // 实际应为后端返回的完整报告地址
  const reportUrl = url.startsWith('http') ? url : `${window.location.origin}${url}`
  window.open(reportUrl, '_blank')
}

const calculateDuration = (start, end) => {
  if (!start || !end) return '-'
  const diff = dayjs(end).diff(dayjs(start))
  const dur = dayjs.duration(diff)
  const hours = Math.floor(dur.asHours())
  const minutes = dur.minutes()
  const seconds = dur.seconds()
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}
</script>

<style scoped>
.plan-detail {
  min-height: 100vh;
  background: var(--bg-color);
}
.page-header {
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.main {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}
.plan-info, .action-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logs {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  margin: 0;
}
.el-table__expand-icon {
  font-size: 14px;
}
</style>