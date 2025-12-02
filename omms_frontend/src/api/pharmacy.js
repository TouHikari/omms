import { medicines, inventoryBatches, inventoryLogs, pharmacyPrescriptions, suppliers, supplierOrders } from './mockData'

const LATENCY = 500

export const getMedicines = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: medicines, message: 'success' })
    }, LATENCY)
  })
}

export const getInventoryBatches = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const map = new Map(medicines.map(m => [m.id, m]))
      const list = inventoryBatches.map(b => ({
        ...b,
        medicine: map.get(b.medicineId)?.name || '未知药品',
        specification: map.get(b.medicineId)?.specification || '',
      }))
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const getLowStockMedicines = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const list = medicines.filter(m => (m.currentStock ?? 0) <= (m.warningStock ?? 0))
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const getExpiringBatches = (days = 30) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const now = new Date()
      const list = inventoryBatches.filter(b => {
        const exp = new Date(b.expiryDate)
        const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
        return diff >= 0 && diff <= days
      })
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const getInventoryLogs = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const map = new Map(medicines.map(m => [m.id, m]))
      const list = inventoryLogs.map(l => ({
        ...l,
        medicine: map.get(l.medicineId)?.name || '未知药品',
        specification: map.get(l.medicineId)?.specification || '',
      }))
      resolve({ code: 200, data: list, message: 'success' })
    }, LATENCY)
  })
}

export const getPrescriptions = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: pharmacyPrescriptions, message: 'success' })
    }, LATENCY)
  })
}

export const updatePrescriptionStatus = (id, status) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const idx = pharmacyPrescriptions.findIndex(p => p.id === id)
      if (idx === -1) {
        resolve({ code: 404, message: 'Prescription not found' })
        return
      }
      const prev = pharmacyPrescriptions[idx].status
      const allowed = {
        pending: ['approved'],
        approved: ['dispensed'],
        dispensed: [],
      }
      if (!allowed[prev]?.includes(status)) {
        resolve({ code: 400, message: '非法状态流转' })
        return
      }
      pharmacyPrescriptions[idx].status = status
      resolve({ code: 200, data: pharmacyPrescriptions[idx], message: 'success' })
    }, LATENCY)
  })
}

export const getSuppliers = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: suppliers, message: 'success' })
    }, LATENCY)
  })
}

export const createSupplier = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const maxId = suppliers.reduce((m, s) => s.id > m ? s.id : m, 0)
      const supplier = {
        id: maxId + 1,
        name: (data?.name || '').trim() || '未命名供应商',
        contact: (data?.contact || '').trim() || '',
        phone: (data?.phone || '').trim() || '',
        address: (data?.address || '').trim() || '',
      }
      suppliers.push(supplier)
      resolve({ code: 200, data: supplier, message: '供应商创建成功' })
    }, LATENCY)
  })
}

export const getSupplierOrders = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ code: 200, data: supplierOrders, message: 'success' })
    }, LATENCY)
  })
}
