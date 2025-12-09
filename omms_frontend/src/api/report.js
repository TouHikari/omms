import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function authHeaders() {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json' }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  return headers
}

export async function getDailyVisits(dateStr) {
  const date = dateStr || new Date().toISOString().slice(0, 10)
  const res = await fetch(`${API_BASE_URL}/reports/daily/visits?date=${encodeURIComponent(date)}`, { headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const list = json.data?.list || []
  return { code: 200, data: list, message: json.message || 'success' }
}

export async function getDailyDrugs(dateStr) {
  const date = dateStr || new Date().toISOString().slice(0, 10)
  const res = await fetch(`${API_BASE_URL}/reports/daily/drugs?date=${encodeURIComponent(date)}`, { headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const list = json.data?.list || []
  return { code: 200, data: list, message: json.message || 'success' }
}

export async function getMonthlyVisits(monthStr) {
  const month = monthStr || new Date().toISOString().slice(0, 7)
  const res = await fetch(`${API_BASE_URL}/reports/monthly/visits?month=${encodeURIComponent(month)}`, { headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const list = json.data?.list || []
  return { code: 200, data: list, message: json.message || 'success' }
}

export async function getMonthlyDrugs(monthStr) {
  const month = monthStr || new Date().toISOString().slice(0, 7)
  const res = await fetch(`${API_BASE_URL}/reports/monthly/drugs?month=${encodeURIComponent(month)}`, { headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const list = json.data?.list || []
  return { code: 200, data: list, message: json.message || 'success' }
}

export async function getCustomReportRows(filters) {
  const params = new URLSearchParams()
  if (filters?.deptName) params.set('deptName', filters.deptName)
  if (filters?.doctorName) params.set('doctorName', filters.doctorName)
  if (filters?.dateRange && Array.isArray(filters.dateRange) && filters.dateRange.length === 2) {
    params.set('dateStart', filters.dateRange[0])
    params.set('dateEnd', filters.dateRange[1])
  }
  const res = await fetch(`${API_BASE_URL}/reports/custom?${params.toString()}`, { headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const list = json.data?.list || []
  return { code: 200, data: list, message: json.message || 'success' }
}
