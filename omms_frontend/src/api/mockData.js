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
  { id: 'R-20250101-001', patient: '王小明', department: '内科', doctor: '张医生', time: '2025-01-01 09:00', status: 'pending', symptom: '发热伴咳嗽3天' },
  { id: 'R-20250101-002', patient: '李小红', department: '外科', doctor: '李医生', time: '2025-01-01 10:00', status: 'completed', symptom: '腹部疼痛1天，伴恶心' },
  { id: 'R-20250101-003', patient: '赵大海', department: '儿科', doctor: '王医生', time: '2025-01-01 11:00', status: 'cancelled', symptom: '小儿咳嗽2天，无发热' },
  { id: 'R-20250102-004', patient: '孙一', department: '骨科', doctor: '赵医生', time: '2025-01-02 14:00', status: 'pending', symptom: '右臂疼痛，活动受限' },
  { id: 'R-20250102-005', patient: '周二', department: '皮肤科', doctor: '张医生', time: '2025-01-02 15:00', status: 'completed', symptom: '皮疹瘙痒，反复发作' },
  { id: 'R-20250103-006', patient: '吴三', department: '内科', doctor: '李医生', time: '2025-01-03 09:30', status: 'pending', symptom: '头晕乏力1周' },
];

export const records = [
  { id: 'MR-20250101-001', patient: '王小明', department: '内科', doctor: '张医生', createdAt: '2025-01-01 09:20', status: 'draft', hasLab: true, hasImaging: false, chiefComplaint: '发热咳嗽3天', diagnosis: '上呼吸道感染', prescriptions: ['对乙酰氨基酚片'], labs: ['血常规'], imaging: [] },
  { id: 'MR-20250101-002', patient: '李小红', department: '外科', doctor: '李医生', createdAt: '2025-01-01 11:10', status: 'finalized', hasLab: false, hasImaging: true, chiefComplaint: '腹痛1天', diagnosis: '急性胃肠炎', prescriptions: ['蒙脱石散'], labs: [], imaging: ['腹部超声'] },
  { id: 'MR-20250101-003', patient: '赵大海', department: '儿科', doctor: '王医生', createdAt: '2025-01-01 15:00', status: 'archived', hasLab: false, hasImaging: false, chiefComplaint: '咳嗽2天', diagnosis: '上呼吸道感染', prescriptions: ['止咳糖浆'], labs: [], imaging: [] },
  { id: 'MR-20250102-004', patient: '孙一', department: '骨科', doctor: '赵医生', createdAt: '2025-01-02 16:40', status: 'draft', hasLab: false, hasImaging: true, chiefComplaint: '右臂疼痛', diagnosis: '肱骨骨折待查', prescriptions: [], labs: [], imaging: ['右臂X光'] },
  { id: 'MR-20250102-005', patient: '周二', department: '皮肤科', doctor: '张医生', createdAt: '2025-01-02 17:30', status: 'finalized', hasLab: true, hasImaging: false, chiefComplaint: '皮疹瘙痒', diagnosis: '过敏性皮炎', prescriptions: ['氯雷他定'], labs: ['过敏原筛查'], imaging: [] },
  { id: 'MR-20250103-006', patient: '吴三', department: '内科', doctor: '李医生', createdAt: '2025-01-03 10:00', status: 'draft', hasLab: false, hasImaging: false, chiefComplaint: '头晕乏力1周', diagnosis: '贫血待查', prescriptions: [], labs: ['血红蛋白'], imaging: [] },
  { id: 'MR-20250103-007', patient: '王小明', department: '内科', doctor: '张医生', createdAt: '2025-01-03 10:40', status: 'finalized', hasLab: true, hasImaging: false, chiefComplaint: '复诊', diagnosis: '上呼吸道感染恢复期', prescriptions: [], labs: ['复查血常规'], imaging: [] },
  { id: 'MR-20250104-008', patient: '李小红', department: '外科', doctor: '李医生', createdAt: '2025-01-04 09:10', status: 'archived', hasLab: false, hasImaging: true, chiefComplaint: '复诊', diagnosis: '胃肠炎恢复', prescriptions: [], labs: [], imaging: ['复查腹部超声'] },
];

export const imagingOptions = [
  { label: '胸片', value: '胸片' },
  { label: '腹部超声', value: '腹部超声' },
  { label: '头部CT', value: '头部CT' },
  { label: '右臂X光', value: '右臂X光' },
]

export const labOptions = [
  { label: '血常规', value: '血常规' },
  { label: '尿常规', value: '尿常规' },
  { label: '肝功能', value: '肝功能' },
  { label: '过敏原筛查', value: '过敏原筛查' },
]

export const patientProfiles = {
  '王小明': { patient_id: 1001, user_id: 5001, name: '王小明', gender: 1, birthday: '1990-04-12', id_card: '110101199004120011', address: '北京市朝阳区和平里', emergency_contact: '王女士', emergency_phone: '13800000001' },
  '李小红': { patient_id: 1002, user_id: 5002, name: '李小红', gender: 0, birthday: '1992-08-22', id_card: '110101199208220022', address: '北京市海淀区西北旺', emergency_contact: '李先生', emergency_phone: '13800000002' },
  '赵大海': { patient_id: 1003, user_id: 5003, name: '赵大海', gender: 1, birthday: '1985-01-10', id_card: '110101198501100033', address: '北京市丰台区丽泽', emergency_contact: '赵女士', emergency_phone: '13800000003' },
  '孙一': { patient_id: 1004, user_id: 5004, name: '孙一', gender: 1, birthday: '1995-05-05', id_card: '110101199505050044', address: '北京市通州区梨园', emergency_contact: '孙先生', emergency_phone: '13800000004' },
  '周二': { patient_id: 1005, user_id: 5005, name: '周二', gender: 0, birthday: '1998-12-12', id_card: '110101199812120055', address: '北京市石景山区古城', emergency_contact: '周女士', emergency_phone: '13800000005' },
  '吴三': { patient_id: 1006, user_id: 5006, name: '吴三', gender: 1, birthday: '1991-03-18', id_card: '110101199103180066', address: '北京市昌平区北七家', emergency_contact: '吴先生', emergency_phone: '13800000006' },
}

export const recordTemplates = [
  { id: 1, name: '内科通用病历模板', scope: '科室', fields: ['主诉', '现病史', '既往史', '诊断', '处方'], defaults: { chiefComplaint: '发热伴咳嗽3天', diagnosis: '上呼吸道感染待查', prescriptions: ['对乙酰氨基酚片'], labs: ['血常规'], imaging: [] } },
  { id: 2, name: '外科术后随访模板', scope: '科室', fields: ['术后天数', '伤口情况', '复查项目', '诊断', '处方'], defaults: { chiefComplaint: '术后复诊随访', diagnosis: '术后恢复期', prescriptions: ['布洛芬缓释胶囊'], labs: [], imaging: ['腹部超声'] } },
  { id: 3, name: '通用简易模板', scope: '通用', fields: ['主诉', '诊断'], defaults: { chiefComplaint: '主诉待填写', diagnosis: '待诊断', prescriptions: [], labs: [], imaging: [] } },
]
