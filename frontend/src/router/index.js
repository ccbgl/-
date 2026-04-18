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

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) next('/login')
  else next()
})

export default router