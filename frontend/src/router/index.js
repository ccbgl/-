import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/plan/:id',
    name: 'PlanDetail',
    component: () => import('@/views/PlanDetail.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({ history: createWebHistory(), routes })

// 在路由守卫外部获取 store 实例，确保使用同一个单例
const auth = useAuthStore()

router.beforeEach((to, from, next) => {
  // 如果路由需要认证且当前没有 token，则跳转到登录页
  if (to.meta.requiresAuth && !auth.token) {
    next('/login')
  }
  // 如果已登录且访问的是登录页，则重定向到首页
  else if (to.path === '/login' && auth.token) {
    next('/')
  }
  // 其他情况正常放行
  else {
    next()
  }
})

export default router