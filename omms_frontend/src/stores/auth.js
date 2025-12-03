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
    { username: 'admin@omms', password: 'admin123', role: 'admin', user: { name: '系统管理员', id: 1 } },
    { username: 'doctor001', password: 'omms123', role: 'doctor', user: { name: '李医生', id: 2 } },
    { username: 'nurse001', password: 'omms123', role: 'nurse', user: { name: '王护士', id: 3 } },
    { username: 'patient001', password: 'omms123', role: 'patient', user: { name: '张患者', id: 4 } },
  ]

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

  function roleFromId(id) {
    const map = { 1: 'admin', 2: 'doctor', 3: 'patient', 4: 'nurse' }
    return map[id] || 'patient'
  }

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

  async function loginWithApi({ username, password }) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    const json = await res.json()
    if (json.code !== 200) throw new Error(json.message || '登录失败')
    const data = json.data
    const u = data.user
    login({ token: data.accessToken, role: roleFromId(u.roleId), user: { name: u.realName || u.username, id: u.userId } })
    return true
  }

  async function registerWithApi({ username, password, email, phone, realName }) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, email, phone, realName })
    })
    const json = await res.json()
    if (json.code !== 200) throw new Error(json.message || '注册失败')
    return json.data
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

  return { token, role, user, isAuthenticated, login, loginWithPassword, loginWithApi, registerWithApi, logout }
})
