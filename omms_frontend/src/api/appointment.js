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
      console.log('Creating appointment:', data);
      // In a real app, this would save to DB
      resolve({ code: 200, data: { id: Math.floor(Math.random() * 10000) }, message: '预约成功' });
    }, LATENCY);
  });
};
