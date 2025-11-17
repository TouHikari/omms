<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { CalendarOutlined, ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()

const sidebar = computed(() => route.meta?.sidebar || [])
const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'list')
const currentGroup = computed(() => currentMenu.value.split('_')[0])

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ['内科', '外科', '儿科', '骨科', '皮肤科']
const doctors = ['张医生', '李医生', '王医生', '赵医生']

const form = ref({ department: undefined, doctor: undefined, date: undefined, time: undefined })

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

const columns = [
  { title: '预约号', dataIndex: 'id', key: 'id' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action' },
]

const filteredAppointments = computed(() => {
  const m = currentMenu.value
  if (m === 'list_pending') return appointments.value.filter(a => a.status === 'pending')
  if (m === 'list_completed') return appointments.value.filter(a => a.status === 'completed')
  if (m === 'list_cancelled') return appointments.value.filter(a => a.status === 'cancelled')
  if (m === 'list_by_department' && form.value.department) return appointments.value.filter(a => a.department === form.value.department)
  if (m === 'list_by_doctor' && form.value.doctor) return appointments.value.filter(a => a.doctor === form.value.doctor)
  return appointments.value
})

const onCreateSubmit = () => {
  if (!form.value.department || !form.value.doctor || !form.value.date || !form.value.time) {
    message.warning('请填写完整信息')
    return
  }
  message.success('预约已生成')
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
        <a-card class="metric-card metric-today" :bordered="false" hoverable @click="setMenu('list_all')">
          <div class="metric">
            <div class="metric-icon-wrap"><CalendarOutlined class="metric-icon" /></div>
            <div class="metric-content">
              <div class="metric-label">今日预约</div>
              <div class="metric-value">{{ metrics.totalToday }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="metric-card metric-pending" :bordered="false" hoverable @click="setMenu('list_pending')">
          <div class="metric">
            <div class="metric-icon-wrap"><ClockCircleOutlined class="metric-icon" /></div>
            <div class="metric-content">
              <div class="metric-label">待就诊</div>
              <div class="metric-value">{{ metrics.pending }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="metric-card metric-completed" :bordered="false" hoverable @click="setMenu('list_completed')">
          <div class="metric">
            <div class="metric-icon-wrap"><CheckCircleOutlined class="metric-icon" /></div>
            <div class="metric-content">
              <div class="metric-label">已完成</div>
              <div class="metric-value">{{ metrics.completed }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="metric-card metric-cancelled" :bordered="false" hoverable @click="setMenu('list_cancelled')">
          <div class="metric">
            <div class="metric-icon-wrap"><CloseCircleOutlined class="metric-icon" /></div>
            <div class="metric-content">
              <div class="metric-label">已取消</div>
              <div class="metric-value">{{ metrics.cancelled }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <section class="quick-links">
      <div class="quick-title">快捷导航</div>
      <a-row :gutter="12">
        <a-col v-for="group in sidebar" :key="group.key" :span="6">
          <a-card :title="group.label">
            <a-space direction="vertical" style="width: 100%">
              <a-button v-for="item in group.children" :key="item.key" block
                :type="currentMenu === item.key ? 'primary' : 'default'" @click="setMenu(item.key)">
                {{ item.label }}
              </a-button>
            </a-space>
          </a-card>
        </a-col>
      </a-row>
    </section>

    <section class="content">
      <template v-if="currentGroup === 'list'">
        <a-card title="预约列表">
          <a-space style="margin-bottom: 12px">
            <a-select v-if="currentMenu === 'list_by_department'" v-model:value="form.department" style="width: 200px"
              placeholder="选择科室">
              <a-select-option v-for="d in departments" :key="d" :value="d">{{ d }}</a-select-option>
            </a-select>
            <a-select v-if="currentMenu === 'list_by_doctor'" v-model:value="form.doctor" style="width: 200px"
              placeholder="选择医生">
              <a-select-option v-for="d in doctors" :key="d" :value="d">{{ d }}</a-select-option>
            </a-select>
            <a-button type="primary" @click="setMenu('create')">新建预约</a-button>
          </a-space>
          <a-table :columns="columns" :data-source="filteredAppointments" :pagination="{ pageSize: 5 }" rowKey="id">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="{ pending: 'blue', completed: 'green', cancelled: 'red' }[record.status]">
                  {{ { pending: '待就诊', completed: '已完成', cancelled: '已取消' }[record.status] }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" @click="message.info(`查看 ${record.id}`)">详情</a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </template>

      <template v-else-if="currentGroup === 'create'">
        <a-card title="新建预约">
          <a-steps :current="0" style="margin-bottom: 16px">
            <a-step title="选择科室" />
            <a-step title="选择医生" />
            <a-step title="选择时间段" />
            <a-step title="确认生成" />
          </a-steps>
          <a-form layout="inline">
            <a-form-item label="科室">
              <a-select v-model:value="form.department" style="width: 200px" placeholder="选择科室">
                <a-select-option v-for="d in departments" :key="d" :value="d">{{ d }}</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="医生">
              <a-select v-model:value="form.doctor" style="width: 200px" placeholder="选择医生">
                <a-select-option v-for="d in doctors" :key="d" :value="d">{{ d }}</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="日期">
              <a-date-picker v-model:value="form.date" style="width: 180px" />
            </a-form-item>
            <a-form-item label="时间">
              <a-time-picker v-model:value="form.time" style="width: 140px" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="onCreateSubmit">生成预约单</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </template>

      <template v-else-if="currentGroup === 'schedules'">
        <a-card title="医生排班">
          <a-table
            :data-source="doctors.map(d => ({ doctor: d, monday: '可约', tuesday: '可约', wednesday: '休', thursday: '可约', friday: '可约' }))"
            :columns="[
              { title: '医生', dataIndex: 'doctor', key: 'doctor' },
              { title: '周一', dataIndex: 'monday', key: 'monday' },
              { title: '周二', dataIndex: 'tuesday', key: 'tuesday' },
              { title: '周三', dataIndex: 'wednesday', key: 'wednesday' },
              { title: '周四', dataIndex: 'thursday', key: 'thursday' },
              { title: '周五', dataIndex: 'friday', key: 'friday' },
            ]" :pagination="false" rowKey="doctor" />
        </a-card>
      </template>

      <template v-else-if="currentGroup === 'departments'">
        <a-card title="科室设置">
          <a-row :gutter="12">
            <a-col :span="6" v-for="d in departments" :key="d">
              <a-card :title="d" size="small">
                <a-space>
                  <a-button type="link">编辑</a-button>
                  <a-button type="link">排班配置</a-button>
                </a-space>
              </a-card>
            </a-col>
          </a-row>
          <a-space style="margin-top: 12px">
            <a-button type="primary">新建科室</a-button>
          </a-space>
        </a-card>
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

.quick-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-title {
  font-weight: 600;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
