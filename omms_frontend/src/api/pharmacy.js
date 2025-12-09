import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function authHeaders() {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json' }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  return headers
}

export const getMedicines = async () => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/medicines?page=1&pageSize=200`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data?.list || []
  const data = list.map(m => ({ id: m.id, name: m.name, specification: m.specification, unit: m.unit, price: m.price, warningStock: m.warningStock, currentStock: m.currentStock }))
  return { code: json.code || res.status, data, message: json.message }
}

export const getInventoryBatches = async () => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/inventory/batches`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code || res.status, data: list, message: json.message }
}

export const getInventoryLogs = async () => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/inventory/logs`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code || res.status, data: list, message: json.message }
}

export const getPrescriptions = async (status) => {
  const qs = status && status !== 'all' ? `?status=${encodeURIComponent(status)}` : ''
  const res = await fetch(`${API_BASE_URL}/pharmacy/prescriptions${qs}`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code || res.status, data: list, message: json.message }
}

export const updatePrescriptionStatus = async (id, status) => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/prescriptions/${encodeURIComponent(id)}/status`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify({ status }) })
  const json = await res.json()
  return { code: json.code || res.status, data: json.data, message: json.message }
}

export const getSuppliers = async () => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/suppliers`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code || res.status, data: list, message: json.message }
}

export const createSupplier = async (data) => {
  const payload = { name: (data?.name || '').trim(), contact: (data?.contact || '').trim(), phone: (data?.phone || '').trim(), address: (data?.address || '').trim() }
  const res = await fetch(`${API_BASE_URL}/pharmacy/suppliers`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  return { code: json.code || res.status, data: json.data, message: json.message }
}

export const getSupplierOrders = async () => {
  const res = await fetch(`${API_BASE_URL}/pharmacy/orders`, { headers: authHeaders() })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code || res.status, data: list, message: json.message }
}
