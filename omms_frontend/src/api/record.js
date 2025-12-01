import { records, departments, doctors } from './mockData'

const LATENCY = 500

export const getRecords = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: records, message: 'success' })
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

