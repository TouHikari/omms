import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('omms_token'))
  const role = ref(localStorage.getItem('omms_role'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  function login(payload) {
    token.value = payload.token
    role.value = payload.role || null
    user.value = payload.user || null
  }

  function logout() {
    token.value = null
    role.value = null
    user.value = null
  }

  watch(token, (t) => {
    if (t) localStorage.setItem('omms_token', t)
    else localStorage.removeItem('omms_token')
  })

  watch(role, (r) => {
    if (r) localStorage.setItem('omms_role', r)
    else localStorage.removeItem('omms_role')
  })

  return { token, role, user, isAuthenticated, login, logout }
})