import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('omms_token'))
  const role = ref(localStorage.getItem('omms_role'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const LOCAL_USERS = [
    { username: 'admin', password: 'admin123', role: 'admin', user: { name: '管理员', id: 1 } },
    { username: 'doctor', password: 'doc123', role: 'doctor', user: { name: '医生张', id: 2 } },
    { username: 'nurse', password: 'nurse123', role: 'nurse', user: { name: '护士李', id: 3 } },
    { username: 'patient', password: 'patient123', role: 'patient', user: { name: '患者王', id: 4 } },
  ]

  function login(payload) {
    token.value = payload.token
    role.value = payload.role || null
    user.value = payload.user || null
  }

  function loginWithPassword({ username, password }) {
    const found = LOCAL_USERS.find(u => u.username === username && u.password === password)
    if (!found) throw new Error('用户名或密码错误')
    login({ token: `dev-${found.username}-token`, role: found.role, user: found.user })
    return true
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

  return { token, role, user, isAuthenticated, login, loginWithPassword, logout }
})
