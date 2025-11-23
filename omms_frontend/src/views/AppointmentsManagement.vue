<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CalendarOutlined, ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import AppointmentsList from '@/components/Appointments/AppointmentsList.vue'
import AppointmentsCreate from '@/components/Appointments/AppointmentsCreate.vue'
import AppointmentsSchedules from '@/components/Appointments/AppointmentsSchedules.vue'
import AppointmentsDepartments from '@/components/Appointments/AppointmentsDepartments.vue'

const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'list')
const currentGroup = computed(() => currentMenu.value.split('_')[0])

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ['内科', '外科', '儿科', '骨科', '皮肤科']
const doctors = ['张医生', '李医生', '王医生', '赵医生']


const appointments = ref([
  { id: 'R-20250101-001', patient: '王小明', department: '内科', doctor: '张医生', time: '2025-01-01 09:00', status: 'pending' },
  { id: 'R-20250101-002', patient: '李小红', department: '外科', doctor: '李医生', time: '2025-01-01 10:00', status: 'completed' },
  { id: 'R-20250101-003', patient: '赵大海', department: '儿科', doctor: '王医生', time: '2025-01-01 11:00', status: 'cancelled' },
  { id: 'R-20250102-004', patient: '孙一', department: '骨科', doctor: '赵医生', time: '2025-01-02 14:00', status: 'pending' },
  { id: 'R-20250102-005', patient: '周二', department: '皮肤科', doctor: '张医生', time: '2025-01-02 15:00', status: 'completed' },
  { id: 'R-20250103-006', patient: '吴三', department: '内科', doctor: '李医生', time: '2025-01-03 09:30', status: 'pending' },
])

const metrics = computed(() => {
  const totalToday = appointments.value.filter(a => a.time.startsWith('2025-01-02')).length
  const pending = appointments.value.filter(a => a.status === 'pending').length
  const completed = appointments.value.filter(a => a.status === 'completed').length
  const cancelled = appointments.value.filter(a => a.status === 'cancelled').length
  return { totalToday, pending, completed, cancelled }
})

function updateStatus(id, status) {
  const a = appointments.value.find(x => x.id === id)
  if (a) a.status = status
}


</script>

<template>
  <section class="appointments-page">
    <section class="page-header">
      <div class="title">预约管理</div>
      <div class="desc">在线预约、医生排班、科室设置与状态跟踪</div>
    </section>

    <a-row :gutter="16" class="metrics">
      <a-col :span="6">
        <a-card class="metric-card metric-today" :bordered="false">
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
        <a-card class="metric-card metric-pending" :bordered="false">
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
        <a-card class="metric-card metric-completed" :bordered="false">
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
        <a-card class="metric-card metric-cancelled" :bordered="false">
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
      <template v-if="currentGroup === 'list'">
        <AppointmentsList :current-menu="currentMenu" :departments="departments" :doctors="doctors" :appointments="appointments" :set-menu="setMenu" :update-status="updateStatus" />
      </template>

      <template v-else-if="currentGroup === 'create'">
        <AppointmentsCreate :departments="departments" :doctors="doctors" />
      </template>

      <template v-else-if="currentGroup === 'schedules'">
        <AppointmentsSchedules :doctors="doctors" />
      </template>

      <template v-else-if="currentGroup === 'departments'">
        <AppointmentsDepartments :departments="departments" />
      </template>
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
