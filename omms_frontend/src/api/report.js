export async function getDailyVisits(dateStr) {
  const date = dateStr || new Date().toISOString().slice(0, 10)
  const data = Array.from({ length: 12 }).map((_, i) => ({
    id: `${date.replace(/-/g, '')}${String(i + 1).padStart(3, '0')}`,
    patient: ['张三', '李四', '王五', '赵六'][i % 4],
    department: ['内科', '外科', '儿科', '皮肤科'][i % 4],
    doctor: ['王医生', '李医生', '赵医生', '孙医生'][i % 4],
    time: `${date} ${String(8 + (i % 9)).padStart(2, '0')}:${String((i * 7) % 60).padStart(2, '0')}`,
    status: ['completed', 'pending', 'completed', 'cancelled'][i % 4],
  }))
  return new Promise(resolve => setTimeout(() => resolve({ code: 200, data, message: 'success' }), 300))
}

export async function getDailyDrugs(dateStr) {
  const date = dateStr || new Date().toISOString().slice(0, 10)
  const data = Array.from({ length: 10 }).map((_, i) => ({
    id: `${date.replace(/-/g, '')}D${String(i + 1).padStart(3, '0')}`,
    medicine: ['阿莫西林', '布洛芬', '维生素C', '对乙酰氨基酚'][i % 4],
    specification: ['0.5g', '200mg', '100mg', '500mg'][i % 4],
    quantity: (i % 5) + 1,
    patient: ['张三', '李四', '王五', '赵六'][i % 4],
    department: ['内科', '外科', '儿科', '皮肤科'][i % 4],
    doctor: ['王医生', '李医生', '赵医生', '孙医生'][i % 4],
    date,
  }))
  return new Promise(resolve => setTimeout(() => resolve({ code: 200, data, message: 'success' }), 300))
}

export async function getMonthlyVisits(monthStr) {
  const month = monthStr || new Date().toISOString().slice(0, 7)
  const days = 30
  const data = Array.from({ length: days }).map((_, i) => ({
    date: `${month}-${String(i + 1).padStart(2, '0')}`,
    count: (i * 3) % 50 + 10,
  }))
  return new Promise(resolve => setTimeout(() => resolve({ code: 200, data, message: 'success' }), 300))
}

export async function getMonthlyDrugs(monthStr) {
  const month = monthStr || new Date().toISOString().slice(0, 7)
  const days = 30
  const data = Array.from({ length: days }).map((_, i) => ({
    date: `${month}-${String(i + 1).padStart(2, '0')}`,
    items: (i * 5) % 40 + 5,
  }))
  return new Promise(resolve => setTimeout(() => resolve({ code: 200, data, message: 'success' }), 300))
}
