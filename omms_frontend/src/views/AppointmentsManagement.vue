<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CalendarOutlined, ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import AppointmentsList from '@/components/Appointments/AppointmentsList.vue'
import AppointmentsCreate from '@/components/Appointments/AppointmentsCreate.vue'
import AppointmentsSchedules from '@/components/Appointments/AppointmentsSchedules.vue'
import PageLayout from '@/layouts/PageLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { getDepartments, getAllDoctors, getAppointments, updateAppointmentStatus } from '@/api/appointment'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'list_all')

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ref([])
const doctors = ref([])
const appointments = ref([])
const loading = ref(false)
const apptTotal = ref(0)
const apptPage = ref(1)
const apptPageSize = ref(10)

function statusFromMenu(menuKey) {
  const m = String(menuKey || '')
  if (m === 'list_pending') return 'pending'
  if (m === 'list_completed') return 'completed'
  if (m === 'list_cancelled') return 'cancelled'
  return 'all'
}

const loadData = async () => {
  loading.value = true
  try {
    const [deptRes, docRes, apptRes] = await Promise.all([
      getDepartments(),
      getAllDoctors(),
      getAppointments({ page: apptPage.value, pageSize: apptPageSize.value, status: statusFromMenu(currentMenu.value) })
    ])

    if (deptRes.code === 200) departments.value = deptRes.data
    if (docRes.code === 200) doctors.value = docRes.data
    if (apptRes.code === 200) {
      appointments.value = apptRes.data.list || []
      apptTotal.value = apptRes.data.total || 0
      apptPage.value = apptRes.data.page || apptPage.value
      apptPageSize.value = apptRes.data.pageSize || apptPageSize.value
    }
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

const refreshAppointments = async () => {
  try {
    const apptRes = await getAppointments({ page: apptPage.value, pageSize: apptPageSize.value, status: statusFromMenu(currentMenu.value) })
    if (apptRes.code === 200) {
      appointments.value = apptRes.data.list || []
      apptTotal.value = apptRes.data.total || 0
      apptPage.value = apptRes.data.page || apptPage.value
      apptPageSize.value = apptRes.data.pageSize || apptPageSize.value
    }
  } catch {
    // ignore
  }
}

watch(currentMenu, (m) => {
  if ((m || '').startsWith('list')) {
    refreshAppointments()
  }
})

function onAppointmentsPagination(pagination) {
  apptPage.value = pagination?.current || 1
  apptPageSize.value = pagination?.pageSize || apptPageSize.value
  refreshAppointments()
}

const metrics = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  const totalToday = appointments.value.filter(a => (a.time || '').slice(0, 10) === todayStr).length
  const pending = appointments.value.filter(a => a.status === 'pending').length
  const completed = appointments.value.filter(a => a.status === 'completed').length
  const cancelled = appointments.value.filter(a => a.status === 'cancelled').length
  return { totalToday, pending, completed, cancelled }
})

async function updateStatus(id, status) {
  try {
    const target = appointments.value.find(x => x.id === id)
    const apptId = target?.apptId
    const res = apptId ? await updateAppointmentStatus(apptId, status) : { code: 400, message: 'invalid id' }
    if (res.code === 200) {
      message.success('状态更新成功')
      const a = appointments.value.find(x => x.id === id)
      if (a) a.status = status
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


const pagePanels = computed(() => {
  const panels = [{ key: 'list', header: '预约列表' }]
  if (['admin', 'nurse', 'patient'].includes(auth.role)) {
    panels.push({ key: 'create', header: '新建预约' })
  }
  if (['admin', 'doctor'].includes(auth.role)) {
    panels.push({ key: 'schedules', header: '医生排班' })
  }
  return panels
})

const panelMenuMap = { list: 'list_all', create: 'create', schedules: 'schedules_roster' }

</script>

<template>
  <PageLayout title="预约管理" desc="在线预约、医生排班与状态跟踪" :panels="pagePanels" :menu-map="panelMenuMap">
    <template #metrics>
      <div class="metrics-grid">
        <a-card class="metric-card metric-today" :bordered="false" @click="setMenu('list_all')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <CalendarOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">今日预约</div>
              <div class="metric-value">{{ metrics.totalToday }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-pending" :bordered="false" @click="setMenu('list_pending')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <ClockCircleOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">待就诊</div>
              <div class="metric-value">{{ metrics.pending }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-completed" :bordered="false" @click="setMenu('list_completed')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <CheckCircleOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">已完成</div>
              <div class="metric-value">{{ metrics.completed }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-cancelled" :bordered="false" @click="setMenu('list_cancelled')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <CloseCircleOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">已取消</div>
              <div class="metric-value">{{ metrics.cancelled }}</div>
            </div>
          </div>
        </a-card>
      </div>
    </template>

    <template #panel-list>
      <AppointmentsList :current-menu="currentMenu" :departments="departments" :doctors="doctors"
        :appointments="appointments" :total="apptTotal" :set-menu="setMenu" :update-status="updateStatus" :on-pagination="onAppointmentsPagination" />
    </template>

    <template #panel-create>
      <AppointmentsCreate :departments="departments" :doctors="doctors" />
    </template>

    <template #panel-schedules>
      <AppointmentsSchedules :doctors="doctors" />
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

.metric-today {
  background-color: $flat-warm-bg;
  border: 1px solid $flat-warm-border;
  color: $flat-warm-text;
}

.metric-pending {
  background-color: $flat-info-bg;
  border: 1px solid $flat-info-border;
  color: $flat-info-text;
}

.metric-completed {
  background-color: $flat-success-bg;
  border: 1px solid $flat-success-border;
  color: $flat-success-text;
}

.metric-cancelled {
  background-color: $flat-danger-bg;
  border: 1px solid $flat-danger-border;
  color: $flat-danger-text;
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
</style>
