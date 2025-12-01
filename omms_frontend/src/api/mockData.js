export const departments = [
  { id: 1, name: '内科', description: '内科科室' },
  { id: 2, name: '外科', description: '外科科室' },
  { id: 3, name: '儿科', description: '儿科科室' },
  { id: 4, name: '妇产科', description: '妇产科科室' },
  { id: 5, name: '眼科', description: '眼科科室' },
  { id: 6, name: '耳鼻喉科', description: '耳鼻喉科科室' },
  { id: 7, name: '口腔科', description: '口腔科科室' },
  { id: 8, name: '皮肤科', description: '皮肤科科室' },
  { id: 9, name: '骨科', description: '骨科科室' },
];

export const doctors = [
  { id: 1, name: '张医生', deptId: 1, title: '主任医师', specialty: '心血管疾病', available: true },
  { id: 2, name: '李医生', deptId: 1, title: '副主任医师', specialty: '消化系统', available: true },
  { id: 3, name: '王医生', deptId: 2, title: '主任医师', specialty: '普外科', available: true },
  { id: 4, name: '赵医生', deptId: 3, title: '主治医师', specialty: '小儿呼吸', available: true },
  { id: 5, name: '孙医生', deptId: 9, title: '主任医师', specialty: '骨折创伤', available: true }, // 骨科
  { id: 6, name: '周医生', deptId: 8, title: '副主任医师', specialty: '皮炎湿疹', available: true }, // 皮肤科
  { id: 7, name: '吴医生', deptId: 1, title: '主治医师', specialty: '内分泌', available: true },
];

export const schedules = [
  // Mocking schedules for the next few days
  {
    id: 1,
    doctorId: 1,
    date: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0], // Tomorrow
    startTime: '08:00',
    endTime: '12:00',
    maxAppointments: 20,
    booked: 5,
  },
  {
    id: 2,
    doctorId: 1,
    date: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0], // Tomorrow
    startTime: '14:00',
    endTime: '18:00',
    maxAppointments: 20,
    booked: 2,
  },
  {
    id: 3,
    doctorId: 2,
    date: new Date(new Date().setDate(new Date().getDate() + 2)).toISOString().split('T')[0], // Day after tomorrow
    startTime: '09:00',
    endTime: '17:00',
    maxAppointments: 15,
    booked: 0,
  },
];

export const appointments = [
  { id: 'R-20250101-001', patient: '王小明', department: '内科', doctor: '张医生', time: '2025-01-01 09:00', status: 'pending' },
  { id: 'R-20250101-002', patient: '李小红', department: '外科', doctor: '李医生', time: '2025-01-01 10:00', status: 'completed' },
  { id: 'R-20250101-003', patient: '赵大海', department: '儿科', doctor: '王医生', time: '2025-01-01 11:00', status: 'cancelled' },
  { id: 'R-20250102-004', patient: '孙一', department: '骨科', doctor: '赵医生', time: '2025-01-02 14:00', status: 'pending' },
  { id: 'R-20250102-005', patient: '周二', department: '皮肤科', doctor: '张医生', time: '2025-01-02 15:00', status: 'completed' },
  { id: 'R-20250103-006', patient: '吴三', department: '内科', doctor: '李医生', time: '2025-01-03 09:30', status: 'pending' },
];
