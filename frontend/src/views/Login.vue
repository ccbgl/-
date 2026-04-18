<template>
  <div class="login-wrapper">
    <div class="login-bg"></div>
    <el-card class="login-card" shadow="always">
      <div class="login-header">
        <el-icon :size="32" color="#409eff"><Monitor /></el-icon>
        <h2>🚀 自动化测试平台</h2>
        <p class="subtitle">Distributed AutoTest Platform</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            size="large"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer" v-if="auth.isAdmin">
        <el-link type="primary" @click="$router.push('/register')">
          ➕ 创建新用户 (Admin)
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock, Monitor } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    loading.value = true
    const success = await auth.login(form.username, form.password)
    if (success) {
      router.push('/')
    }
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.login-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientMove 15s ease infinite;
  z-index: -1;
}
@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.login-card {
  width: 420px;
  padding: 40px 30px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}
.login-header {
  text-align: center;
  margin-bottom: 30px;
}
.login-header h2 {
  margin: 10px 0 5px;
  color: #303133;
  font-weight: 600;
}
.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}
.login-form {
  margin-bottom: 10px;
}
.login-btn {
  width: 100%;
  font-weight: 500;
  letter-spacing: 2px;
  transition: all 0.3s;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}
.login-footer {
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}
</style>