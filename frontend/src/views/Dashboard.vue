<template>
  <div class="dashboard">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-left">
        <el-icon :size="24" color="#409eff"><Monitor /></el-icon>
        <span class="title">自动化测试平台</span>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <el-avatar :size="32" :icon="UserFilled" />
            <span>{{ auth.user?.username }}</span>
            <el-tag v-if="auth.isAdmin" size="small" type="warning" effect="plain">Admin</el-tag>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="auth.logout(); $router.push('/login')">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main">
      <div class="page-header">
        <h2>📦 测试任务管理</h2>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon> 新建任务
        </el-button>
      </div>

      <!-- 任务列表 -->
      <LoadingSpinner :loading="taskStore.loading">
        <el-table
          :data="taskStore.tasks"
          style="width: 100%"
          @row-click="goToTask"
          row-key="id"
          border
          stripe
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="name" label="任务名称" min-width="180">
            <template #default="{ row }">
              <el-link type="primary" :underline="false">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="repo_url" label="仓库地址" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <el-link :href="row.repo_url" target="_blank" type="info" :underline="false">
                <el-icon><Link /></el-icon> {{ row.repo_url?.split('/').pop() }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" sortable />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click.stop="goToTask(row)">
                管理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </LoadingSpinner>

      <!-- 空状态 -->
      <el-empty
        v-if="!taskStore.loading && taskStore.tasks.length === 0"
        description="暂无测试任务，点击新建开始吧~"
        :image-size="120"
      >
        <el-button type="primary" @click="showCreateDialog">新建任务</el-button>
      </el-empty>
    </el-main>

    <!-- 新建任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建测试任务"
      width="500px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-position="top"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入任务名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入任务描述（可选）"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="代码仓库" prop="repo_url">
          <el-input
            v-model="createForm.repo_url"
            placeholder="默认使用平台配置仓库"
            :disabled="true"
          />
          <el-text size="small" type="info">
            📦 {{ import.meta.env.VITE_APP_REPO_URL }}
          </el-text>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          确 定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/task'
import {
  Monitor, UserFilled, SwitchButton, Plus, Link
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const router = useRouter()
const auth = useAuthStore()
const taskStore = useTaskStore()

const dialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref()

const createForm = reactive({
  name: '',
  description: '',
  repo_url: import.meta.env.VITE_APP_REPO_URL
})

const createRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度2-50位', trigger: 'blur' }
  ]
}

onMounted(() => {
  taskStore.fetchTasks()
})

const goToTask = (row) => {
  router.push(`/task/${row.id}`)
}

const showCreateDialog = () => {
  dialogVisible.value = true
}

const resetForm = () => {
  createForm.name = ''
  createForm.description = ''
  createFormRef.value?.resetFields()
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  try {
    await createFormRef.value.validate()
    creating.value = true
    await taskStore.createTask(createForm)
    dialogVisible.value = false
    taskStore.fetchTasks()
  } catch (error) {
    console.error('Create task error:', error)
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: var(--bg-color);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}
.user-info:hover {
  background: #f5f7fa;
}
.main {
  padding: 24px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}
.el-table {
  cursor: pointer;
}
.el-table__row:hover {
  background-color: #f5f7fa !important;
}
</style>