import { records, departments, doctors, recordTemplates } from './mockData'

const LATENCY = 500

export const getRecords = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const list = records.map(r => ({
        id: r.id,
        patient: r.patient,
        department: r.department,
        doctor: r.doctor,
        createdAt: r.createdAt,
        status: r.status,
        hasLab: !!r.hasLab,
        hasImaging: !!r.hasImaging,
        chiefComplaint: r.chiefComplaint || '',
        diagnosis: r.diagnosis || '',
        prescriptions: Array.isArray(r.prescriptions) ? [...r.prescriptions] : [],
        labs: Array.isArray(r.labs) ? [...r.labs] : [],
        imaging: Array.isArray(r.imaging) ? [...r.imaging] : [],
      }))
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const updateRecordStatus = (id, status) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = records.findIndex(r => r.id === id)
      if (idx !== -1) {
        records[idx].status = status
        resolve({ code: 200, data: records[idx], message: 'success' })
      } else {
        resolve({ code: 404, message: 'Record not found' })
      }
    }, LATENCY)
  })
}

export const createRecord = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const dept = departments.find(d => d.id === data.deptId)
      const doc = doctors.find(d => d.id === data.doctorId)
      const dateStr = new Date().toISOString().split('T')[0]
      const rand = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
      const id = `MR-${dateStr.replaceAll('-', '')}-${rand}`
      const record = {
        id,
        patient: (data?.patient || '').trim() || '测试患者',
        department: dept?.name || '未知科室',
        doctor: doc?.name || '未知医生',
        createdAt: `${dateStr} ${data?.time || '10:00'}`,
        status: 'draft',
        hasLab: Array.isArray(data?.labs) && data.labs.length > 0,
        hasImaging: Array.isArray(data?.imaging) && data.imaging.length > 0,
        chiefComplaint: data?.chiefComplaint || '',
        diagnosis: data?.diagnosis || '',
        prescriptions: Array.isArray(data?.prescriptions) ? data.prescriptions : [],
        labs: Array.isArray(data?.labs) ? data.labs : [],
        imaging: Array.isArray(data?.imaging) ? data.imaging : [],
      }
      records.unshift(record)
      resolve({ code: 200, data: record, message: '病历创建成功' })
    }, LATENCY)
  })
}

export const updateRecord = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = records.findIndex(r => r.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: 'Record not found' })
        return
      }
      const updated = { ...records[idx], ...data }
      updated.hasLab = Array.isArray(updated.labs) && updated.labs.length > 0
      updated.hasImaging = Array.isArray(updated.imaging) && updated.imaging.length > 0
      records[idx] = updated
      resolve({ code: 200, data: updated, message: 'success' })
    }, LATENCY)
  })
}

export const getRecordTemplates = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const seen = new Set()
      const list = recordTemplates
        .filter(t => {
          if (seen.has(t.id)) return false
          seen.add(t.id)
          return true
        })
        .map(t => ({
          id: t.id,
          name: t.name,
          scope: t.scope,
          fields: Array.isArray(t.fields) ? [...t.fields] : [],
          defaults: {
            chiefComplaint: t.defaults?.chiefComplaint || '',
            diagnosis: t.defaults?.diagnosis || '',
            prescriptions: Array.isArray(t.defaults?.prescriptions) ? [...t.defaults.prescriptions] : [],
            labs: Array.isArray(t.defaults?.labs) ? [...t.defaults.labs] : [],
            imaging: Array.isArray(t.defaults?.imaging) ? [...t.defaults.imaging] : [],
          },
        }))
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const getRecordTemplateById = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const tpl = recordTemplates.find(t => t.id === Number(id))
      if (!tpl) {
        resolve({ code: 404, message: 'Template not found' })
      } else {
        resolve({ code: 200, data: tpl, message: 'success' })
      }
    }, LATENCY)
  })
}

export const createRecordTemplate = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const maxId = recordTemplates.reduce((m, t) => t.id > m ? t.id : m, 0)
      const tpl = {
        id: maxId + 1,
        name: (data?.name || '').trim() || '未命名模板',
        scope: (data?.scope || '').trim() || '通用',
        fields: Array.isArray(data?.fields) ? data.fields.filter(Boolean) : [],
        defaults: {
          chiefComplaint: data?.defaults?.chiefComplaint || '',
          diagnosis: data?.defaults?.diagnosis || '',
          prescriptions: Array.isArray(data?.defaults?.prescriptions) ? data.defaults.prescriptions.filter(Boolean) : [],
          labs: Array.isArray(data?.defaults?.labs) ? data.defaults.labs.filter(Boolean) : [],
          imaging: Array.isArray(data?.defaults?.imaging) ? data.defaults.imaging.filter(Boolean) : [],
        },
      }
      recordTemplates.push(tpl)
      resolve({ code: 200, data: tpl, message: '模板创建成功' })
    }, LATENCY)
  })
}

export const updateRecordTemplate = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = recordTemplates.findIndex(t => t.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: 'Template not found' })
        return
      }
      const updated = {
        ...recordTemplates[idx],
        name: data?.name ?? recordTemplates[idx].name,
        scope: data?.scope ?? recordTemplates[idx].scope,
        fields: Array.isArray(data?.fields) ? data.fields.filter(Boolean) : recordTemplates[idx].fields,
        defaults: {
          chiefComplaint: data?.defaults?.chiefComplaint ?? recordTemplates[idx].defaults?.chiefComplaint ?? '',
          diagnosis: data?.defaults?.diagnosis ?? recordTemplates[idx].defaults?.diagnosis ?? '',
          prescriptions: Array.isArray(data?.defaults?.prescriptions) ? data.defaults.prescriptions.filter(Boolean) : (recordTemplates[idx].defaults?.prescriptions || []),
          labs: Array.isArray(data?.defaults?.labs) ? data.defaults.labs.filter(Boolean) : (recordTemplates[idx].defaults?.labs || []),
          imaging: Array.isArray(data?.defaults?.imaging) ? data.defaults.imaging.filter(Boolean) : (recordTemplates[idx].defaults?.imaging || []),
        },
      }
      recordTemplates[idx] = updated
      resolve({ code: 200, data: updated, message: '模板更新成功' })
    }, LATENCY)
  })
}

export const deleteRecordTemplate = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = recordTemplates.findIndex(t => t.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: 'Template not found' })
        return
      }
      const removed = recordTemplates.splice(idx, 1)[0]
      resolve({ code: 200, data: removed, message: '模板删除成功' })
    }, LATENCY)
  })
}
