
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

export const createDepartment = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const maxId = departments.reduce((max, d) => d.id > max ? d.id : max, 0)
      const newDept = {
        id: maxId + 1,
        name: data?.name?.trim() || '未命名科室',
        description: data?.description?.trim() || ''
      }
      departments.push(newDept)
      resolve({ code: 200, data: newDept, message: '科室创建成功' })
    }, LATENCY)
  })
}

export const updateDepartment = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = departments.findIndex(d => d.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: '科室不存在' })
        return
      }
      const updated = { ...departments[idx], ...data }
      departments[idx] = updated
      resolve({ code: 200, data: updated, message: '科室更新成功' })
    }, LATENCY)
  })
}

export const deleteDepartment = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = departments.findIndex(d => d.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: '科室不存在' })
        return
      }
      const removed = departments.splice(idx, 1)[0]
      resolve({ code: 200, data: removed, message: '科室删除成功' })
    }, LATENCY)
  })
}

export const createDoctor = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const maxId = doctors.reduce((max, d) => d.id > max ? d.id : max, 0)
      const newDoc = {
        id: maxId + 1,
        name: (data?.name || '').trim() || '未命名医生',
        deptId: data?.deptId,
        title: (data?.title || '').trim() || '主治医师',
        specialty: (data?.specialty || '').trim() || '',
        available: data?.available ?? true,
      }
      if (!newDoc.deptId) {
        resolve({ code: 400, message: '缺少科室ID' })
        return
      }
      doctors.push(newDoc)
      resolve({ code: 200, data: newDoc, message: '医生创建成功' })
    }, LATENCY)
  })
}

export const updateDoctor = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = doctors.findIndex(d => d.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: '医生不存在' })
        return
      }
      const updated = { ...doctors[idx], ...data }
      doctors[idx] = updated
      resolve({ code: 200, data: updated, message: '医生更新成功' })
    }, LATENCY)
  })
}

export const deleteDoctor = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = doctors.findIndex(d => d.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: '医生不存在' })
        return
      }
      const removed = doctors.splice(idx, 1)[0]
      resolve({ code: 200, data: removed, message: '医生删除成功' })
    }, LATENCY)
  })
}
