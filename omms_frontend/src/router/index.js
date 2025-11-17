import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotFoundPage from '@/views/404Page.vue'
import DashBoardPage from '@/views/DashBoardPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import SimpleLayout from '@/layouts/SimpleLayout.vue'
import AppointmentsManagement from '@/views/AppointmentsManagement.vue'
import RecordsManagement from '@/views/RecordsManagement.vue'
import PharmacyManagement from '@/views/PharmacyManagement.vue'
import InpatientManagement from '@/views/InpatientManagement.vue'
import PaymentsManagement from '@/views/PaymentsManagement.vue'
import ReportsManagement from '@/views/ReportsManagement.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashBoardPage,
      meta: { requiresAuth: true, title: '数据看板' },
    },
    {
      path: '/appointments',
      name: 'appointments',
      component: AppointmentsManagement,
      meta: { requiresAuth: true, title: '预约管理' },
    },
    {
      path: '/records',
      name: 'records',
      component: RecordsManagement,
      meta: { requiresAuth: true, title: '记录管理' },
    },
    {
      path: '/pharmacy',
      name: 'pharmacy',
      component: PharmacyManagement,
      meta: { requiresAuth: true, title: '药房管理' },
    },
    {
      path: '/inpatient',
      name: 'inpatient',
      component: InpatientManagement,
      meta: { requiresAuth: true, title: '住院管理' },
    },
    {
      path: '/payments',
      name: 'payments',
      component: PaymentsManagement,
      meta: { requiresAuth: true, title: '支付管理' },
    },
    {
      path: '/reports',
      name: 'reports',
      component: ReportsManagement,
      meta: { requiresAuth: true, title: '报告管理' },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { layout: 'blank', guestOnly: true, title: '登录' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundPage,
      meta: { layout: SimpleLayout, title: '404' },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta?.guestOnly && auth.isAuthenticated) {
    next({ path: '/' })
    return
  }

  const requiredRoles = to.meta?.roles
  if (requiredRoles && (!auth.role || !requiredRoles.includes(auth.role))) {
    next({ path: '/' })
    return
  }

  next()
})

export default router
