const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function authHeaders() {
  const t = localStorage.getItem('omms_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

export const getRecords = async (params = {}) => {
  const page = params.page ?? 1
  const pageSize = params.pageSize ?? 200
  const qs = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
  const res = await fetch(`${API_BASE_URL}/records?${qs.toString()}`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const list = json.data?.list ?? []
  return { code: json.code, data: list, message: json.message }
}

export const updateRecordStatus = async (id, status) => {
  const res = await fetch(`${API_BASE_URL}/records/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ status })
  })
  const json = await res.json()
  return json
}

export const createRecord = async (data) => {
  const payload = {
    deptId: data?.deptId,
    doctorId: data?.doctorId,
    patientName: data?.patient,
    chiefComplaint: data?.chiefComplaint,
    diagnosis: data?.diagnosis,
    prescriptions: Array.isArray(data?.prescriptions) ? data.prescriptions : [],
    labs: Array.isArray(data?.labs) ? data.labs : [],
    imaging: Array.isArray(data?.imaging) ? data.imaging : [],
  }
  const res = await fetch(`${API_BASE_URL}/records`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  })
  const json = await res.json()
  return json
}

export const updateRecord = async (id, data) => {
  const payload = {
    chiefComplaint: data?.chiefComplaint,
    diagnosis: data?.diagnosis,
    prescriptions: Array.isArray(data?.prescriptions) ? data.prescriptions : [],
    labs: Array.isArray(data?.labs) ? data.labs : [],
    imaging: Array.isArray(data?.imaging) ? data.imaging : [],
  }
  const res = await fetch(`${API_BASE_URL}/records/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  })
  const json = await res.json()
  return json
}

export const getRecordTemplates = async () => {
  const res = await fetch(`${API_BASE_URL}/record-templates`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const list = json.data ?? []
  return { code: json.code, data: list, message: json.message }
}

export const getRecordTemplateById = async (id) => {
  const res = await fetch(`${API_BASE_URL}/record-templates/${id}`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  return json
}

export const createRecordTemplate = async (data) => {
  const payload = {
    name: (data?.name || '').trim(),
    scope: (data?.scope || '').trim() || '通用',
    fields: Array.isArray(data?.fields) ? data.fields.filter(Boolean) : [],
    defaults: data?.defaults ?? {},
  }
  const res = await fetch(`${API_BASE_URL}/record-templates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  })
  const json = await res.json()
  return json
}

export const updateRecordTemplate = async (id, data) => {
  const payload = {
    name: data?.name,
    scope: data?.scope,
    fields: Array.isArray(data?.fields) ? data.fields.filter(Boolean) : undefined,
    defaults: data?.defaults,
  }
  const res = await fetch(`${API_BASE_URL}/record-templates/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  })
  const json = await res.json()
  return json
}

export const deleteRecordTemplate = async (id) => {
  const res = await fetch(`${API_BASE_URL}/record-templates/${id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  })
  const json = await res.json()
  return json
}

export const getRecordDictionaries = async () => {
  const res = await fetch(`${API_BASE_URL}/records/dictionaries`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const data = json.data || { imaging: [], labs: [] }
  return { code: json.code, data, message: json.message }
}

export const getRecordDictionaryImaging = async () => {
  const res = await fetch(`${API_BASE_URL}/records/dictionaries/imaging`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code, data: list, message: json.message }
}

export const getRecordDictionaryLabs = async () => {
  const res = await fetch(`${API_BASE_URL}/records/dictionaries/labs`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const list = json.data || []
  return { code: json.code, data: list, message: json.message }
}

export const getPatients = async (name = '', page = 1, pageSize = 20) => {
  const qs = new URLSearchParams()
  if (name) qs.set('name', name)
  qs.set('page', String(page))
  qs.set('pageSize', String(pageSize))
  const res = await fetch(`${API_BASE_URL}/patients?${qs.toString()}`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  const data = json.data || { list: [], total: 0, page, pageSize }
  return { code: json.code, data, message: json.message }
}

export const getPatientById = async (pid) => {
  const res = await fetch(`${API_BASE_URL}/patients/${encodeURIComponent(pid)}`, { headers: { 'Content-Type': 'application/json', ...authHeaders() } })
  const json = await res.json()
  return json
}
