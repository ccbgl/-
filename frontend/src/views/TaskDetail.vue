<template>
  <div class="task-detail">
    <!-- 返回头部 -->
    <el-page-header @back="router.back()" content="测试计划管理" class="page-header" />

    <el-main class="main">
      <!-- 任务信息卡片 -->
      <el-card class="task-info">
        <template #header>
          <div class="card-header">
            <span>📋 {{ task?.name }}</span>
            <el-tag size="small" effect="plain">{{ task?.repo_url?.split('/').pop() }}</el-tag>
          </div>
        </template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="描述">{{ task?.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ task?.created_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="仓库地址" :span="2">
            <el-link :href="task?.repo_url" target="_blank" :underline="false">
              {{ task?.repo_url }}
            </el-link>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 计划管理 -->
      <div class="plan-section">
        <div class="section-header">
          <h3>🎯 测试计划</h3>
          <el-button type="primary" size="small" @click="showCreatePlanDialog">
            <el-icon><Plus /></el-icon> 添加计划
          </el-button>
        </div>

        <LoadingSpinner :loading="taskStore.loading">
          <el-table :data="taskStore.plans" border stripe>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="name" label="计划名称" min-width="150" />
            <el-table-column prop="plan_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getTypeTag(row.plan_type)" size="small" effect="plain">
                  {{ getTypeText(row.plan_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cron_expr" label="Cron 表达式" width="150" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.status"
                  :active-value="'active'"
                  :inactive-value="'inactive'"
                  active-color="#13ce66"
                  inactive-color="#dcdfe6"
                  @change="handleStatusChange(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="success"
                  size="small"
                  @click="runPlan(row, 'full')"
                  :loading="runningPlanId === row.id && runningType === 'full'"
                >
                  ▶ 全量执行
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="runPlan(row, 'suite')"
                  :loading="runningPlanId === row.id && runningType === 'suite'"
                >
                  ▶ 测试套
                </el-button>
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="goToPlan(row.id)"
                >
                  监控
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </LoadingSpinner>

        <el-empty
          v-if="!taskStore.loading && taskStore.plans.length === 0"
          description="暂无测试计划"
          :image-size="100"
        />
      </div>
    </el-main>

    <!-- 创建计划对话框 -->
    <el-dialog
      v-model="planDialogVisible"
      title="添加测试计划"
      width="500px"
      @closed="resetPlanForm"
    >
      <el-form
        ref="planFormRef"
        :model="planForm"
        :rules="planRules"
        label-position="top"
      >
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="planForm.name" placeholder="请输入计划名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="执行类型" prop="plan_type">
          <el-radio-group v-model="planForm.plan_type">
            <el-radio label="full">全量执行</el-radio>
            <el-radio label="suite">测试套执行</el-radio>
            <el-radio label="scheduled">定时任务</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="planForm.plan_type === 'scheduled'"
          label="Cron 表达式"
          prop="cron_expr"
        >
          <el-input
            v-model="planForm.cron_expr"
            placeholder="例如：0 0 2 * * ? (每天 2 点执行)"
          />
          <el-text size="small" type="info">
            💡 格式：秒 分 时 日 月 周
          </el-text>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePlan" :loading="creatingPlan">
          确 定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTaskStore } from '@/stores/task'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()
const route = useRoute()
const taskStore = useTaskStore()

const taskId = ref(route.params.id)
const task = ref(null)
const planDialogVisible = ref(false)
const creatingPlan = ref(false)
const runningPlanId = ref(null)
const runningType = ref(null)
const planFormRef = ref()

const planForm = reactive({
  name: '',
  plan_type: 'full',
  cron_expr: ''
})

const planRules = {
  name: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度 2-50 位', trigger: 'blur' }
  ],
  cron_expr: [
    {
      required: true,
      message: '请输入 Cron 表达式',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (planForm.plan_type === 'scheduled' && !value) {
          callback(new Error('定时任务必须填写 Cron 表达式'))
        } else {
          callback()
        }
      }
    }
  ]
}

onMounted(async () => {
  await taskStore.fetchTasks()
  task.value = taskStore.tasks.find(t => t.id == taskId.value)
  if (!task.value) {
    ElMessage.error('任务不存在')
    router.back()
    return
  }
  await taskStore.fetchPlans(taskId.value)
})

const getTypeTag = (type) => {
  const map = { full: 'primary', suite: 'warning', scheduled: 'success' }
  return map[type] || 'info'
}
const getTypeText = (type) => {
  const map = { full: '全量执行', suite: '测试套', scheduled: '定时任务' }
  return map[type] || type
}

const showCreatePlanDialog = () => {
  planDialogVisible.value = true
}
const resetPlanForm = () => {
  planForm.name = ''
  planForm.plan_type = 'full'
  planForm.cron_expr = ''
  planFormRef.value?.resetFields()
}

const handleCreatePlan = async () => {
  if (!planFormRef.value) return
  try {
    await planFormRef.value.validate()
    creatingPlan.value = true
    await taskStore.createPlan(taskId.value, planForm)
    planDialogVisible.value = false
    taskStore.fetchPlans(taskId.value)
  } catch (error) {
    console.error('Create plan error:', error)
  } finally {
    creatingPlan.value = false
  }
}

const handleStatusChange = async (plan) => {
  try {
    ElMessage.success(`计划 "${plan.name}" 已${plan.status === 'active' ? '启用' : '禁用'}`)
  } catch (error) {
    plan.status = plan.status === 'active' ? 'inactive' : 'active'
    ElMessage.error('状态更新失败')
  }
}

const runPlan = async (plan, type) => {
  runningPlanId.value = plan.id
  runningType.value = type
  try {
    await taskStore.runPlan(plan.id, type)
    router.push(`/plan/${plan.id}`)
  } catch (error) {
    console.error('Run plan error:', error)
  } finally {
    runningPlanId.value = null
    runningType.value = null
  }
}

const goToPlan = (planId) => {
  router.push(`/plan/${planId}`)
}
</script>

<style scoped>
.task-detail {
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
.task-info {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.plan-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}
</style>