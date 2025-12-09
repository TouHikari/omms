
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function authHeaders() {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json' }
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`
  return headers
}

function pad4(n) {
  const s = String(n || '')
  return s.length >= 4 ? s.slice(-4) : s.padStart(4, '0')
}

function toDepartmentList(data) {
  const list = data?.list || []
  return list.map(d => ({ id: d.deptId, name: d.deptName, description: d.deptDesc }))
}

function toDoctorList(data) {
  const list = data?.list || []
  return list.map(d => ({ id: d.doctorId, name: d.doctorName, deptId: d.deptId, deptName: d.deptName, title: d.title, specialty: d.specialty, introduction: d.introduction, createdAt: d.createdAt, updatedAt: d.updatedAt }))
}

function toScheduleList(data) {
  const list = data?.list || []
  return list.map(s => ({ id: s.scheduleId, doctorId: s.doctorId, doctorName: s.doctorName, deptId: s.deptId, deptName: s.deptName, date: s.workDate, startTime: s.startTime, endTime: s.endTime, totalQuota: s.totalQuota, bookedCount: s.bookedCount, availableQuota: s.availableQuota, status: s.status }))
}

function toAppointmentsList(data) {
  const list = data?.list || []
  return list.map(a => {
    const dateStr = String(a.apptTime || '').slice(0, 10).replaceAll('-', '')
    const id = `R-${dateStr}-${pad4(a.apptId)}`
    const statusStr = a.status === 1 ? 'completed' : a.status === 2 ? 'cancelled' : 'pending'
    return { id, apptId: a.apptId, patient: a.patientName, department: a.deptName, doctor: a.doctorName, time: a.apptTime, status: statusStr, symptom: a.symptomDesc }
  })
}

export async function getDepartments() {
  const res = await fetch(`${API_BASE_URL}/departments?page=1&pageSize=100`, { method: 'GET', headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  return { code: 200, data: toDepartmentList(json.data), message: json.message || 'success' }
}

export async function getAllDoctors() {
  const res = await fetch(`${API_BASE_URL}/doctors?page=1&pageSize=100`, { method: 'GET', headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  return { code: 200, data: toDoctorList(json.data), message: json.message || 'success' }
}

export async function getDoctorsByDept(deptId) {
  const res = await fetch(`${API_BASE_URL}/doctors?deptId=${encodeURIComponent(deptId)}&page=1&pageSize=100`, { method: 'GET', headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  return { code: 200, data: toDoctorList(json.data), message: json.message || 'success' }
}

export async function getDoctorSchedules(doctorId) {
  const res = await fetch(`${API_BASE_URL}/schedules?doctorId=${encodeURIComponent(doctorId)}&page=1&pageSize=100`, { method: 'GET', headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  return { code: 200, data: toScheduleList(json.data), message: json.message || 'success' }
}

export async function getAppointments() {
  const res = await fetch(`${API_BASE_URL}/appointments?page=1&pageSize=100`, { method: 'GET', headers: authHeaders() })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  return { code: 200, data: toAppointmentsList(json.data), message: json.message || 'success' }
}

export async function updateAppointmentStatus(apptId, status) {
  const statusMap = { pending: 0, completed: 1, cancelled: 2 }
  const payload = { status: statusMap[status] }
  const res = await fetch(`${API_BASE_URL}/appointments/${encodeURIComponent(apptId)}/status`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || res.status || 500, message: json.message || 'failed' }
  const a = json.data
  const dateStr = String(a.apptTime || '').slice(0, 10).replaceAll('-', '')
  const id = `R-${dateStr}-${pad4(a.apptId)}`
  const statusStr = a.status === 1 ? 'completed' : a.status === 2 ? 'cancelled' : 'pending'
  return { code: 200, data: { id, apptId: a.apptId, patient: a.patientName, department: a.deptName, doctor: a.doctorName, time: a.apptTime, status: statusStr, symptom: a.symptomDesc }, message: json.message || 'success' }
}

export async function createAppointment(data) {
  const auth = useAuthStore()
  const apptTime = data.apptTime || `${data.date} ${data.startTime.length === 5 ? data.startTime + ':00' : data.startTime}`
  const payload = { patientId: data.patientId || auth.user?.id, doctorId: data.doctorId, scheduleId: data.scheduleId, apptTime, symptomDesc: data.symptom || '' }
  const res = await fetch(`${API_BASE_URL}/appointments`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || res.status || 500, message: json.message || 'failed' }
  const a = json.data
  const dateStr = String(a.apptTime || '').slice(0, 10).replaceAll('-', '')
  const id = `R-${dateStr}-${pad4(a.apptId)}`
  return { code: 200, data: { id, apptId: a.apptId, patient: a.patientName, department: a.deptName, doctor: a.doctorName, time: a.apptTime, status: a.status === 1 ? 'completed' : a.status === 2 ? 'cancelled' : 'pending', symptom: a.symptomDesc }, message: json.message || '预约成功' }
}

export async function createDepartment(data) {
  const payload = { deptName: (data?.name || '').trim(), deptDesc: (data?.description || '').trim() }
  const res = await fetch(`${API_BASE_URL}/departments`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const d = json.data
  return { code: 200, data: { id: d.deptId, name: d.deptName, description: d.deptDesc }, message: json.message || '科室创建成功' }
}

export async function updateDepartment(id, data) {
  const payload = { deptName: data?.name, deptDesc: data?.description }
  const res = await fetch(`${API_BASE_URL}/departments/${encodeURIComponent(id)}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const d = json.data
  return { code: 200, data: { id: d.deptId, name: d.deptName, description: d.deptDesc }, message: json.message || '科室更新成功' }
}

export async function deleteDepartment(id) {
  const res = await fetch(`${API_BASE_URL}/departments/${encodeURIComponent(id)}`, { method: 'DELETE', headers: authHeaders() })
  const json = await res.json()
  return { code: json.code || 200, data: json.data, message: json.message || '科室删除成功' }
}

export async function createDoctor(data) {
  const payload = {
    doctorName: (data?.name || '').trim(),
    deptId: data?.deptId,
    userId: data?.userId,
    title: data?.title,
    specialty: data?.specialty,
    introduction: data?.introduction,
  }
  const res = await fetch(`${API_BASE_URL}/doctors`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const d = json.data
  return { code: 200, data: { id: d.doctorId, name: d.doctorName, deptId: d.deptId, title: d.title, specialty: d.specialty }, message: json.message || '医生创建成功' }
}

export async function updateDoctor(id, data) {
  const payload = {
    doctorName: data?.name,
    deptId: data?.deptId,
    title: data?.title,
    specialty: data?.specialty,
    introduction: data?.introduction,
  }
  const res = await fetch(`${API_BASE_URL}/doctors/${encodeURIComponent(id)}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  const json = await res.json()
  if (json.code !== 200) return { code: json.code || 500, message: json.message || 'failed' }
  const d = json.data
  return { code: 200, data: { id: d.doctorId, name: d.doctorName, deptId: d.deptId, title: d.title, specialty: d.specialty }, message: json.message || '医生更新成功' }
}

export async function deleteDoctor(id) {
  const res = await fetch(`${API_BASE_URL}/doctors/${encodeURIComponent(id)}`, { method: 'DELETE', headers: authHeaders() })
  const json = await res.json()
  return { code: json.code || 200, data: json.data, message: json.message || '医生删除成功' }
}
