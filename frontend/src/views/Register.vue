<template>
  <div class="register-wrapper">
    <el-card class="register-card" shadow="always">
      <div class="register-header">
        <h2>👤 创建新用户</h2>
        <p class="subtitle">仅管理员可操作</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="register-form"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名 (4-20位)"
            :prefix-icon="User"
            maxlength="20"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码 (6-20位)"
            :prefix-icon="Lock"
            show-password
            maxlength="20"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Checked"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading">
            创建用户
          </el-button>
          <el-button @click="$router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock, Checked } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (form.confirmPassword !== '') {
      formRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}
const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '长度4-20位', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ]
}

onMounted(() => {
  if (!auth.isAdmin) {
    ElMessage.error('仅管理员可创建用户')
    router.push('/')
  }
})

const handleRegister = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    loading.value = true
    await auth.register(form.username, form.password)
    form.username = ''
    form.password = ''
    form.confirmPassword = ''
  } catch (error) {
    console.error('Register error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}
.register-card {
  width: 480px;
  padding: 30px;
  border-radius: 12px;
}
.register-header {
  text-align: center;
  margin-bottom: 25px;
}
.register-header h2 {
  margin: 0 0 8px;
  color: #303133;
}
.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}
.register-form {
  margin-top: 10px;
}
</style>