<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  departments: { type: Array, required: true },
  doctors: { type: Array, required: true },
  records: { type: Array, required: true },
  setMenu: { type: Function, required: true },
  updateStatus: { type: Function, required: true },
})

const columns = [
  { title: '病历号', dataIndex: 'id', key: 'id' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action' },
]

const modeFilter = ref('all')
const patientKeyword = ref('')
const doctorId = ref(null)
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

watch(() => props.currentMenu, (m) => {
  const key = (m || '')
  if (key.startsWith('list_')) {
    if (key === 'list_by_patient') modeFilter.value = 'by_patient'
    else if (key === 'list_by_doctor') modeFilter.value = 'by_doctor'
    else if (key === 'list_by_date') modeFilter.value = 'by_date'
    else if (key === 'list_lab_imaging') modeFilter.value = 'lab_imaging'
    else modeFilter.value = 'all'
  }
}, { immediate: true })

watch(modeFilter, (s) => {
  const map = { all: 'list_all', by_patient: 'list_by_patient', by_doctor: 'list_by_doctor', by_date: 'list_by_date', lab_imaging: 'list_lab_imaging' }
  const targetMenu = map[s] || 'list_all'
  const key = (props.currentMenu || '')
  if (key.startsWith('list_') && targetMenu !== props.currentMenu) props.setMenu(targetMenu)
  currentPage.value = 1
})

function onTableChange(pagination) {
  currentPage.value = pagination.current
  pageSize.value = pagination.pageSize
}

const doctorOptions = computed(() => (props.doctors || []).map(d => ({ label: `${d.name}（${d.title}）`, value: d.id })))

function formatDateStr(str) {
  return (str || '').slice(0, 10)
}

function inRange(dateStr) {
  if (!dateRange.value || dateRange.value.length !== 2) return true
  const d = formatDateStr(dateStr)
  const start = dateRange.value[0]?.format ? dateRange.value[0].format('YYYY-MM-DD') : formatDateStr(dateRange.value[0])
  const end = dateRange.value[1]?.format ? dateRange.value[1].format('YYYY-MM-DD') : formatDateStr(dateRange.value[1])
  return d >= start && d <= end
}

const filteredRecords = computed(() => {
  const list = props.records || []
  const mode = modeFilter.value
  if (mode === 'by_patient') {
    const kw = patientKeyword.value.trim()
    if (!kw) return list
    return list.filter(r => (r.patient || '').includes(kw))
  }
  if (mode === 'by_doctor') {
    const did = doctorId.value
    if (!did) return list
    const doc = (props.doctors || []).find(d => d.id === did)
    const name = doc?.name
    return list.filter(r => r.doctor === name)
  }
  if (mode === 'by_date') {
    return list.filter(r => inRange(r.createdAt))
  }
  if (mode === 'lab_imaging') {
    return list.filter(r => r.hasLab || r.hasImaging)
  }
  return list
})

const detailVisible = ref(false)
const detailRecord = ref(null)

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
    <a-space style="margin-bottom: 12px; width: 100%; justify-content: space-between">
      <div>
        <a-radio-group v-model:value="modeFilter" button-style="solid">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="by_patient">按患者</a-radio-button>
          <a-radio-button value="by_doctor">按医生</a-radio-button>
          <a-radio-button value="by_date">按日期</a-radio-button>
          <a-radio-button value="lab_imaging">检验/检查结果</a-radio-button>
        </a-radio-group>
        <a-input-search v-if="modeFilter === 'by_patient'" v-model:value="patientKeyword" style="margin-left: 12px; width: 240px" placeholder="输入患者姓名" />
        <a-select v-if="modeFilter === 'by_doctor'" v-model:value="doctorId" :options="doctorOptions" style="margin-left: 12px; width: 260px" placeholder="选择医生" />
        <a-range-picker v-if="modeFilter === 'by_date'" v-model:value="dateRange" style="margin-left: 12px" />
      </div>
      <a-button type="primary" @click="setMenu('create')">新建病历</a-button>
    </a-space>
    <a-table
      :columns="columns"
      :data-source="filteredRecords"
      :pagination="{ current: currentPage, pageSize: pageSize, showSizeChanger: true, pageSizeOptions: ['10', '20', '50'] }"
      rowKey="id"
      @change="onTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="{ draft: 'blue', finalized: 'green', archived: 'default' }[record.status]">
            {{ { draft: '草稿', finalized: '定稿', archived: '归档' }[record.status] }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="showDetail(record)">详情</a-button>
            <a-dropdown>
              <a-button type="link">更改状态</a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="draft" @click="onUpdateStatus(record, 'draft')">置为草稿</a-menu-item>
                  <a-menu-item key="finalized" @click="onUpdateStatus(record, 'finalized')">置为定稿</a-menu-item>
                  <a-menu-item key="archived" @click="onUpdateStatus(record, 'archived')">置为归档</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>

  <a-modal v-model:open="detailVisible" title="病历详情" :footer="null" width="780px">
    <a-descriptions :column="2" bordered size="small">
      <a-descriptions-item label="病历号">{{ detailRecord?.id }}</a-descriptions-item>
      <a-descriptions-item label="状态">{{ { draft: '草稿', finalized: '定稿', archived: '归档' }[detailRecord?.status] }}</a-descriptions-item>
      <a-descriptions-item label="患者">{{ detailRecord?.patient }}</a-descriptions-item>
      <a-descriptions-item label="创建时间">{{ detailRecord?.createdAt }}</a-descriptions-item>
      <a-descriptions-item label="科室">{{ detailRecord?.department }}</a-descriptions-item>
      <a-descriptions-item label="医生">{{ detailRecord?.doctor }}</a-descriptions-item>
    </a-descriptions>

    <a-divider />

    <a-descriptions :column="2" title="就诊信息" size="small">
      <a-descriptions-item label="主诉" :span="2">{{ detailRecord?.chiefComplaint || '-' }}</a-descriptions-item>
      <a-descriptions-item label="诊断" :span="2">{{ detailRecord?.diagnosis || '-' }}</a-descriptions-item>
      <a-descriptions-item label="处方" :span="2">{{ (detailRecord?.prescriptions || []).join('，') || '-' }}</a-descriptions-item>
      <a-descriptions-item label="检验" :span="2">{{ (detailRecord?.labs || []).join('，') || '-' }}</a-descriptions-item>
      <a-descriptions-item label="检查" :span="2">{{ (detailRecord?.imaging || []).join('，') || '-' }}</a-descriptions-item>
    </a-descriptions>

    <a-divider />

    <a-descriptions :column="2" title="患者信息" size="small">
      <a-descriptions-item label="患者ID">{{ currentPatient?.patient_id }}</a-descriptions-item>
      <a-descriptions-item label="用户ID">{{ currentPatient?.user_id }}</a-descriptions-item>
      <a-descriptions-item label="姓名">{{ currentPatient?.name }}</a-descriptions-item>
      <a-descriptions-item label="性别">{{ currentPatient?.gender === 1 ? '男' : currentPatient?.gender === 0 ? '女' : '-' }}</a-descriptions-item>
      <a-descriptions-item label="出生日期">{{ currentPatient?.birthday }}</a-descriptions-item>
      <a-descriptions-item label="身份证号">{{ currentPatient?.id_card }}</a-descriptions-item>
      <a-descriptions-item label="地址" :span="2">{{ currentPatient?.address }}</a-descriptions-item>
      <a-descriptions-item label="紧急联系人">{{ currentPatient?.emergency_contact }}</a-descriptions-item>
      <a-descriptions-item label="紧急联系电话">{{ currentPatient?.emergency_phone }}</a-descriptions-item>
    </a-descriptions>
  </a-modal>
</template>

<style scoped lang="scss"></style>
