<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <el-header class="dashboard-header">
      <div class="header-left">
        <h2>🚀 FastAPI 自动化测试平台</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" icon="User" />
            <span class="username">{{ authStore.username || '用户' }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="dashboard-main">
      <div class="content-wrapper">
        <!-- 操作栏 -->
        <div class="action-bar">
          <el-button type="primary" @click="dialogVisible = true">
            <el-icon><Plus /></el-icon> 新建任务
          </el-button>
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务名称..."
            style="width: 240px"
            clearable
            prefix-icon="Search"
          />
        </div>

        <!-- 任务列表 -->
        <el-table :data="filteredTasks" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="任务名称" min-width="200" />
          <el-table-column prop="repo_url" label="仓库地址" min-width="250" show-overflow-tooltip />
          <el-table-column prop="branch" label="分支" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="viewTask(scope.row)">
                查看详情
              </el-button>
              <el-button link type="danger" @click="deleteTask(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态提示 -->
        <el-empty v-if="!loading && tasks.length === 0" description="暂无任务，请新建一个测试任务" />
      </div>
    </el-main>

    <!-- 新建任务对话框 -->
    <el-dialog v-model="dialogVisible" title="新建测试任务" width="500px">
      <el-form :model="newTask" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="newTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="仓库地址" required>
          <el-input v-model="newTask.repo_url" placeholder="https://github.com/..." />
        </el-form-item>
        <el-form-item label="分支" required>
          <el-input v-model="newTask.branch" placeholder="main" />
        </el-form-item>
        <!-- 使用变量替代 import.meta.env -->
        <el-form-item label="默认仓库">
          <el-text size="small" type="info">
            📦 {{ repoUrl }}
          </el-text>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, User } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// 从环境变量获取仓库地址，避免在模板中直接使用 import.meta
const repoUrl = import.meta.env.VITE_APP_REPO_URL || '未配置'

const loading = ref(false)
const submitting = ref(false)
const tasks = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)

const newTask = ref({
  name: '',
  repo_url: '',
  branch: 'main'
})

const filteredTasks = computed(() => {
  if (!searchQuery.value) return tasks.value
  return tasks.value.filter(task =>
    task.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await api.getTasks()
    tasks.value = res.data || []
  } catch (error) {
    ElMessage.error('获取任务列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const createTask = async () => {
  if (!newTask.value.name || !newTask.value.repo_url) {
    ElMessage.warning('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    await api.createTask(newTask.value)
    ElMessage.success('任务创建成功')
    dialogVisible.value = false
    newTask.value = { name: '', repo_url: '', branch: 'main' }
    fetchTasks()
  } catch (error) {
    ElMessage.error('创建任务失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const viewTask = (task) => {
  router.push(`/task/${task.id}`)
}

const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteTask(id)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.dashboard-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 10;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.username {
  margin-left: 8px;
  font-size: 14px;
  color: #606266;
}

.dashboard-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>