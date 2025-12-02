<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  departments: { type: Array, required: true },
  doctors: { type: Array, required: true },
  appointments: { type: Array, required: true },
  setMenu: { type: Function, required: true },
  updateStatus: { type: Function, required: true },
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

const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

watch(() => props.currentMenu, (m) => {
  const key = (m || '')
  if (key.startsWith('list_')) {
    if (key === 'list_pending') statusFilter.value = 'pending'
    else if (key === 'list_completed') statusFilter.value = 'completed'
    else if (key === 'list_cancelled') statusFilter.value = 'cancelled'
    else statusFilter.value = 'all'
  }
}, { immediate: true })

watch(statusFilter, (s) => {
  const targetMenu = s === 'all' ? 'list_all' : `list_${s}`
  const key = (props.currentMenu || '')
  if (key.startsWith('list_') && targetMenu !== props.currentMenu) props.setMenu(targetMenu)
  currentPage.value = 1
})

function onTableChange(pagination) {
  currentPage.value = pagination.current
  pageSize.value = pagination.pageSize
}

const filteredAppointments = computed(() => {
  const s = statusFilter.value
  if (s === 'pending') return props.appointments.filter(a => a.status === 'pending')
  if (s === 'completed') return props.appointments.filter(a => a.status === 'completed')
  if (s === 'cancelled') return props.appointments.filter(a => a.status === 'cancelled')
  return props.appointments
})

const detailVisible = ref(false)
const detailRecord = ref(null)

const viewportWidth = ref(window.innerWidth)
function onResize() { viewportWidth.value = window.innerWidth }
onMounted(() => { window.addEventListener('resize', onResize) })
onUnmounted(() => { window.removeEventListener('resize', onResize) })
const modalWidth = computed(() => viewportWidth.value <= 768 ? '90%' : '720px')

const patientsByName = {
  '王小明': { patient_id: 1001, user_id: 5001, name: '王小明', gender: 1, birthday: '1990-04-12', id_card: '110101199004120011', address: '北京市朝阳区和平里', emergency_contact: '王女士', emergency_phone: '13800000001' },
  '李小红': { patient_id: 1002, user_id: 5002, name: '李小红', gender: 0, birthday: '1992-08-22', id_card: '110101199208220022', address: '北京市海淀区西北旺', emergency_contact: '李先生', emergency_phone: '13800000002' },
  '赵大海': { patient_id: 1003, user_id: 5003, name: '赵大海', gender: 1, birthday: '1985-01-10', id_card: '110101198501100033', address: '北京市丰台区丽泽', emergency_contact: '赵女士', emergency_phone: '13800000003' },
  '孙一': { patient_id: 1004, user_id: 5004, name: '孙一', gender: 1, birthday: '1995-05-05', id_card: '110101199505050044', address: '北京市通州区梨园', emergency_contact: '孙先生', emergency_phone: '13800000004' },
  '周二': { patient_id: 1005, user_id: 5005, name: '周二', gender: 0, birthday: '1998-12-12', id_card: '110101199812120055', address: '北京市石景山区古城', emergency_contact: '周女士', emergency_phone: '13800000005' },
  '吴三': { patient_id: 1006, user_id: 5006, name: '吴三', gender: 1, birthday: '1991-03-18', id_card: '110101199103180066', address: '北京市昌平区北七家', emergency_contact: '吴先生', emergency_phone: '13800000006' },
}

const currentPatient = computed(() => {
  const r = detailRecord.value
  if (!r) return null
  const p = patientsByName[r.patient]
  return p ? p : { patient_id: '-', user_id: '-', name: r.patient, gender: '-', birthday: '-', id_card: '-', address: '-', emergency_contact: '-', emergency_phone: '-' }
})

function showDetail(record) {
  detailRecord.value = record
  detailVisible.value = true
}

async function onUpdateStatus(record, status) {
  const prev = record.status
  record.status = status
  const result = await props.updateStatus(record.id, status)
  if (result === false) {
    record.status = prev
  }
}
</script>

<template>
  <a-card>
    <a-space class="list-toolbar">
      <div>
        <span style="margin-bottom: 4px">筛选方式：</span>
        <a-radio-group v-model:value="statusFilter" button-style="solid">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="pending">待就诊</a-radio-button>
          <a-radio-button value="completed">已完成</a-radio-button>
          <a-radio-button value="cancelled">已取消</a-radio-button>
        </a-radio-group>
      </div>
      <a-button type="primary" @click="setMenu('create')">新建预约</a-button>
    </a-space>
    <a-table
      :columns="columns"
      :data-source="filteredAppointments"
      :pagination="{ current: currentPage, pageSize: pageSize, showSizeChanger: true, pageSizeOptions: ['10', '20', '50'] }"
      :scroll="{ x: 860 }"
      size="small"
      rowKey="id"
      @change="onTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="{ pending: 'blue', completed: 'green', cancelled: 'red' }[record.status]">
            {{ { pending: '待就诊', completed: '已完成', cancelled: '已取消' }[record.status] }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="showDetail(record)">详情</a-button>
            <a-dropdown>
              <a-button type="link">更改状态</a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="pending" @click="onUpdateStatus(record, 'pending')">置为待就诊</a-menu-item>
                  <a-menu-item key="completed" @click="onUpdateStatus(record, 'completed')">置为已完成</a-menu-item>
                  <a-menu-item key="cancelled">
                    <a-popconfirm title="确认取消该预约？" ok-text="确认" cancel-text="取消" @confirm="onUpdateStatus(record, 'cancelled')">
                      <span>置为已取消</span>
                    </a-popconfirm>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>

  <a-modal v-model:open="detailVisible" title="患者详情" :footer="null" :width="modalWidth">
    <a-descriptions :column="2" bordered size="small">
      <a-descriptions-item label="患者ID">{{ currentPatient?.patient_id }}</a-descriptions-item>
      <a-descriptions-item label="用户ID">{{ currentPatient?.user_id }}</a-descriptions-item>
      <a-descriptions-item label="姓名">{{ currentPatient?.name }}</a-descriptions-item>
      <a-descriptions-item label="性别">{{ currentPatient?.gender === 1 ? '男' : currentPatient?.gender === 0 ? '女' : '-'
        }}</a-descriptions-item>
      <a-descriptions-item label="出生日期">{{ currentPatient?.birthday }}</a-descriptions-item>
      <a-descriptions-item label="身份证号">{{ currentPatient?.id_card }}</a-descriptions-item>
      <a-descriptions-item label="地址" :span="2">{{ currentPatient?.address }}</a-descriptions-item>
      <a-descriptions-item label="紧急联系人">{{ currentPatient?.emergency_contact }}</a-descriptions-item>
      <a-descriptions-item label="紧急联系电话">{{ currentPatient?.emergency_phone }}</a-descriptions-item>
    </a-descriptions>

    <a-divider />

    <a-descriptions :column="2" title="预约信息" size="small">
      <a-descriptions-item label="预约号">{{ detailRecord?.id }}</a-descriptions-item>
      <a-descriptions-item label="状态">{{ { pending: '待就诊', completed: '已完成', cancelled: '已取消' }[detailRecord?.status]
        }}</a-descriptions-item>
      <a-descriptions-item label="科室">{{ detailRecord?.department }}</a-descriptions-item>
      <a-descriptions-item label="医生">{{ detailRecord?.doctor }}</a-descriptions-item>
      <a-descriptions-item label="时间" :span="2">{{ detailRecord?.time }}</a-descriptions-item>
      <a-descriptions-item label="症状描述" :span="2">{{ detailRecord?.symptom || '-' }}</a-descriptions-item>
    </a-descriptions>
  </a-modal>
</template>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.list-toolbar {
  margin-bottom: 12px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

:deep(.ant-card) {
  container-type: inline-size;
}

@container (max-width: $breakpoint_md) {
  .list-toolbar {
    flex-wrap: wrap;
    gap: 12px;
  }
  .list-toolbar > :first-child {
    flex: 1 1 100%;
  }
  .list-toolbar > :last-child {
    flex: 0 0 auto;
    align-self: flex-start;
    margin-left: auto;
  }
}

@container (max-width: $breakpoint_sm) {
  :deep(.ant-radio-group) {
    width: 100%;
  }
}
</style>
