<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CalendarOutlined, ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import AppointmentsList from '@/components/Appointments/AppointmentsList.vue'
import AppointmentsCreate from '@/components/Appointments/AppointmentsCreate.vue'
import AppointmentsSchedules from '@/components/Appointments/AppointmentsSchedules.vue'
import AppointmentsDepartments from '@/components/Appointments/AppointmentsDepartments.vue'
import { getDepartments, getAllDoctors, getAppointments, updateAppointmentStatus } from '@/api/appointment'

const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'list_all')
const currentGroup = computed(() => currentMenu.value.split('_')[0])

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ref([])
const doctors = ref([])
const appointments = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const [deptRes, docRes, apptRes] = await Promise.all([
      getDepartments(),
      getAllDoctors(),
      getAppointments()
    ])

    if (deptRes.code === 200) departments.value = deptRes.data
    if (docRes.code === 200) doctors.value = docRes.data
    if (apptRes.code === 200) appointments.value = apptRes.data
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
    const res = await updateAppointmentStatus(id, status)
    if (res.code === 200) {
      message.success('状态更新成功')
      const a = appointments.value.find(x => x.id === id)
      if (a) a.status = status
    } else {
      message.error(res.message || '更新失败')
    }
  } catch {
    message.error('更新失败')
  }
}

const activePanel = ref(currentGroup.value)
const onCollapseChange = (key) => {
  const k = Array.isArray(key) ? key[0] : key
  const groupToMenu = { list: 'list_all', create: 'create', schedules: 'schedules_roster', departments: 'departments_list' }
  const menuKey = groupToMenu[k] || k
  if (menuKey && menuKey !== currentMenu.value) setMenu(menuKey)
}

watch(currentGroup, (g) => {
  activePanel.value = g
}, { immediate: true })

</script>

<template>
  <section class="appointments-page">
    <section class="page-header">
      <div class="title">预约管理</div>
      <div class="desc">在线预约、医生排班、科室设置与状态跟踪</div>
    </section>

    <a-row :gutter="16" class="metrics">
      <a-col :span="6">
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
      </a-col>
      <a-col :span="6">
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
      </a-col>
      <a-col :span="6">
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
      </a-col>
      <a-col :span="6">
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
      </a-col>
    </a-row>

    <section class="content">
      <a-collapse v-model:activeKey="activePanel" accordion @change="onCollapseChange">
        <a-collapse-panel key="list" header="预约列表">
          <AppointmentsList :current-menu="currentMenu" :departments="departments" :doctors="doctors" :appointments="appointments" :set-menu="setMenu" :update-status="updateStatus" />
        </a-collapse-panel>
        <a-collapse-panel key="create" header="新建预约">
          <AppointmentsCreate :departments="departments" :doctors="doctors" />
        </a-collapse-panel>
        <a-collapse-panel key="schedules" header="医生排班">
          <AppointmentsSchedules :doctors="doctors" />
        </a-collapse-panel>
        <a-collapse-panel key="departments" header="科室设置">
          <AppointmentsDepartments :departments="departments" />
        </a-collapse-panel>
      </a-collapse>
    </section>
  </section>
</template>

<style scoped lang="scss">
.appointments-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 20px;
  font-weight: 600;
}

.desc {
  color: #666;
  font-size: 14px;
}

.metrics {
  margin-top: 8px;
}


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

.content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
