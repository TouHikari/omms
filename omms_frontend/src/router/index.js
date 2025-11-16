import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import LoginPage from '@/views/LoginPage.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { requiresAuth: true, title: '首页' },
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
      redirect: '/',
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
