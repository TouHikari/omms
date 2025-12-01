import { departments, doctors, schedules, appointments } from './mockData';

const LATENCY = 500;

export const getDepartments = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: departments, message: 'success' });
    }, LATENCY);
  });
};

export const getAllDoctors = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: doctors, message: 'success' });
    }, LATENCY);
  });
};

export const getDoctorsByDept = (deptId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const filtered = doctors.filter(d => d.deptId === deptId);
      resolve({ code: 200, data: filtered, message: 'success' });
    }, LATENCY);
  });
};

export const getDoctorSchedules = (doctorId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const filtered = schedules.filter(s => s.doctorId === doctorId);
      resolve({ code: 200, data: filtered, message: 'success' });
    }, LATENCY);
  });
};

export const getAppointments = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: appointments, message: 'success' });
    }, LATENCY);
  });
};

export const updateAppointmentStatus = (id, status) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = appointments.findIndex(a => a.id === id);
      if (idx !== -1) {
        appointments[idx].status = status;
        resolve({ code: 200, data: appointments[idx], message: 'success' });
      } else {
        resolve({ code: 404, message: 'Appointment not found' });
      }
    }, LATENCY);
  });
};

export const createAppointment = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const dept = departments.find(d => d.id === data.deptId)
      const doc = doctors.find(d => d.id === data.doctorId)
      const sche = schedules.find(s => s.id === data.scheduleId)
      const dateStr = sche?.date || new Date().toISOString().split('T')[0]
      const rand = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
      const id = `R-${dateStr.replaceAll('-', '')}-${rand}`
      const record = {
        id,
        patient: '测试患者',
        department: dept?.name || '未知科室',
        doctor: doc?.name || '未知医生',
        time: `${dateStr} ${sche?.startTime || '09:00'}`,
        status: 'pending',
        symptom: data?.symptom || ''
      }
      appointments.unshift(record)
      resolve({ code: 200, data: record, message: '预约成功' })
    }, LATENCY);
  });
};

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
