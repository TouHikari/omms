<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MedicineBoxOutlined, InboxOutlined, WarningOutlined, FileTextOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import PageLayout from '@/layouts/PageLayout.vue'
import InventoryPanel from '@/components/Pharmacy/InventoryPanel.vue'
import PrescriptionsPanel from '@/components/Pharmacy/PrescriptionsPanel.vue'
import SuppliersPanel from '@/components/Pharmacy/SuppliersPanel.vue'
import { useAuthStore } from '@/stores/auth'
import { getMedicines, getInventoryBatches, getInventoryLogs, getPrescriptions, updatePrescriptionStatus, getSuppliers, getSupplierOrders } from '@/api/pharmacy'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'inventory_drugs')

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const medicines = ref([])
const batches = ref([])
const inventoryLogs = ref([])
const prescriptions = ref([])
const suppliers = ref([])
const supplierOrders = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const [medRes, batRes, logRes, preRes, supRes, ordRes] = await Promise.all([
      getMedicines(),
      getInventoryBatches(),
      getInventoryLogs(),
      getPrescriptions(),
      getSuppliers(),
      getSupplierOrders(),
    ])

    if (medRes.code === 200) medicines.value = medRes.data
    if (batRes.code === 200) batches.value = batRes.data
    if (logRes.code === 200) inventoryLogs.value = logRes.data
    if (preRes.code === 200) prescriptions.value = preRes.data
    if (supRes.code === 200) suppliers.value = supRes.data
    if (ordRes.code === 200) supplierOrders.value = ordRes.data
  } catch (error) {
    console.error(error)
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const refreshInventory = async () => {
  try {
    const [medRes, batRes, logRes] = await Promise.all([
      getMedicines(),
      getInventoryBatches(),
      getInventoryLogs(),
    ])
    if (medRes.code === 200) medicines.value = medRes.data
    if (batRes.code === 200) batches.value = batRes.data
    if (logRes.code === 200) inventoryLogs.value = logRes.data
  } catch { /* ignore */ }
}

const refreshPrescriptions = async () => {
  try {
    const m = currentMenu.value || ''
    const s = m === 'prescriptions_pending'
      ? 'pending'
      : m === 'prescriptions_approved'
      ? 'approved'
      : m === 'prescriptions_dispensed'
      ? 'dispensed'
      : 'all'
    const res = await getPrescriptions(s)
    if (res.code === 200) {
      const all = res.data
      if (auth.role === 'patient') {
        const myName = auth.user?.name || auth.user?.username
        prescriptions.value = all.filter(p => p.patientName === myName)
      } else {
        prescriptions.value = all
      }
    }
  } catch { /* ignore */ }
}

const refreshSuppliers = async () => {
  try {
    const [supRes, ordRes] = await Promise.all([
      getSuppliers(),
      getSupplierOrders(),
    ])
    if (supRes.code === 200) suppliers.value = supRes.data
    if (ordRes.code === 200) supplierOrders.value = ordRes.data
  } catch { /* ignore */ }
}

watch(currentMenu, (m) => {
  if ((m || '').startsWith('inventory')) {
    refreshInventory()
  } else if ((m || '').startsWith('prescriptions')) {
    refreshPrescriptions()
  } else if ((m || '').startsWith('suppliers')) {
    refreshSuppliers()
  }
})

const metrics = computed(() => {
  const lowStock = medicines.value.filter(m => (m.currentStock ?? 0) <= (m.warningStock ?? 0)).length
  const now = new Date()
  const expiring = batches.value.filter(b => {
    const exp = new Date(b.expiryDate)
    const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    return diff >= 0 && diff <= 30
  }).length
  const totalDrugs = medicines.value.length
  const pendingRx = prescriptions.value.filter(p => p.status === 'pending').length
  return { totalDrugs, lowStock, expiring, pendingRx }
})

async function onUpdatePrescriptionStatus(id, status) {
  try {
    const res = await updatePrescriptionStatus(id, status)
    if (res.code === 200) {
      prescriptions.value = prescriptions.value.map(x => x.id === id ? { ...x, status } : x)
      message.success('处方状态已更新')
      refreshPrescriptions()
      return true
    } else {
      message.error(res.message || '更新失败')
      return false
    }
  } catch {
    message.error('更新失败')
    return false
  }
}

function onSupplierCreated() {
  refreshSuppliers()
}

const pagePanels = computed(() => {
  const panels = []
  if (['admin', 'nurse'].includes(auth.role)) {
    panels.push({ key: 'inventory', header: '库存' })
  }
  panels.push({ key: 'prescriptions', header: '处方' })
  if (['admin'].includes(auth.role)) {
    panels.push({ key: 'suppliers', header: '供应商' })
  }
  return panels
})

const panelMenuMap = { inventory: 'inventory_drugs', prescriptions: 'prescriptions_list', suppliers: 'suppliers_list' }

</script>

<template>
  <PageLayout title="药品与库存" desc="药品列表、库存批次、处方与供应商" :panels="pagePanels" :menu-map="panelMenuMap">
    <template #metrics>
      <div class="metrics-grid" v-if="auth.role !== 'patient'">
        <a-card class="metric-card metric-inventory" :bordered="false" @click="setMenu('inventory_drugs')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <MedicineBoxOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">药品总数</div>
              <div class="metric-value">{{ metrics.totalDrugs }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-warning" :bordered="false" @click="setMenu('inventory_low_stock')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <WarningOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">低库存预警</div>
              <div class="metric-value">{{ metrics.lowStock }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-expiring" :bordered="false" @click="setMenu('inventory_expiry')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <InboxOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">近效期批次</div>
              <div class="metric-value">{{ metrics.expiring }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-pending" :bordered="false" @click="setMenu('prescriptions_pending')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <FileTextOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">待审核处方</div>
              <div class="metric-value">{{ metrics.pendingRx }}</div>
            </div>
          </div>
        </a-card>
      </div>
    </template>

    <template #panel-inventory>
      <InventoryPanel :current-menu="currentMenu" :medicines="medicines" :batches="batches" :logs="inventoryLogs" :set-menu="setMenu" />
    </template>

    <template #panel-prescriptions>
      <PrescriptionsPanel :current-menu="currentMenu" :prescriptions="prescriptions" :update-status="onUpdatePrescriptionStatus" :set-menu="setMenu" />
    </template>

    <template #panel-suppliers>
      <SuppliersPanel :current-menu="currentMenu" :suppliers="suppliers" :orders="supplierOrders" :on-created="onSupplierCreated" :set-menu="setMenu" />
    </template>
  </PageLayout>
</template>

<style scoped lang="scss">
.metric-card {
  border-radius: 12px;
  cursor: pointer;
}

.metric-card:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
}

.metric-inventory {
  background-color: $flat-warm-bg;
  border: 1px solid $flat-warm-border;
  color: $flat-warm-text;
}

.metric-warning {
  background-color: $flat-danger-bg;
  border: 1px solid $flat-danger-border;
  color: $flat-danger-text;
}

.metric-expiring {
  background-color: $flat-info-bg;
  border: 1px solid $flat-info-border;
  color: $flat-info-text;
}

.metric-pending {
  background-color: $flat-success-bg;
  border: 1px solid $flat-success-border;
  color: $flat-success-text;
}

.metric {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 100px;
  background-color: rgba(255, 255, 255, 0.25);
}

.metric-icon {
  font-size: 24px;
  color: inherit;
}

.metric-content {
  display: flex;
  flex-direction: column;
}

.metric-label {
  opacity: 0.85;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  align-items: stretch;
}

@media (min-width: 1600px) {
  .metrics-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
