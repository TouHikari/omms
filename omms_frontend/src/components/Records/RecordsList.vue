<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { updateRecord, getRecordDictionaries, getRecordDictionaryImaging, getRecordDictionaryLabs, getPatients } from '@/api/record'

const props = defineProps({
  currentMenu: { type: String, required: true },
  departments: { type: Array, required: true },
  doctors: { type: Array, required: true },
  records: { type: Array, required: true },
  total: { type: Number, default: 0 },
  setMenu: { type: Function, required: true },
  updateStatus: { type: Function, required: true },
  onPagination: { type: Function, required: true },
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
const statusFilter = ref('draft')
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
    else if (key === 'list_by_status') modeFilter.value = 'by_status'
    else if (key.startsWith('list_status_')) {
      modeFilter.value = 'by_status'
      statusFilter.value = key.replace('list_status_', '')
    }
    else modeFilter.value = 'all'
  }
}, { immediate: true })

watch(modeFilter, (s) => {
  const map = {
    all: 'list_all',
    by_patient: 'list_by_patient',
    by_doctor: 'list_by_doctor',
    by_date: 'list_by_date',
    lab_imaging: 'list_lab_imaging',
    by_status: 'list_by_status',
  }
  const targetMenu = map[s] || 'list_all'
  const key = (props.currentMenu || '')
  if (key.startsWith('list_') && targetMenu !== props.currentMenu) props.setMenu(targetMenu)
  currentPage.value = 1
})

watch(statusFilter, () => {
  if (modeFilter.value === 'by_status') {
    if (props.currentMenu !== 'list_by_status') props.setMenu('list_by_status')
    currentPage.value = 1
  }
})

function onTableChange(pagination) {
  currentPage.value = pagination.current
  pageSize.value = pagination.pageSize
  props.onPagination && props.onPagination({ current: currentPage.value, pageSize: pageSize.value })
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
  if (mode === 'by_status') {
    return list.filter(r => r.status === statusFilter.value)
  }
  return list
})

const detailVisible = ref(false)
const detailRecord = ref(null)

const patientsByName = ref({})

async function ensurePatientLoaded(name) {
  const key = (name || '').trim()
  if (!key) return
  if (patientsByName.value[key]) return
  try {
    const res = await getPatients(key)
    if (res.code === 200) {
      const item = (res.data?.list || []).find(p => (p.name || '').trim() === key)
      if (item) patientsByName.value[key] = item
    }
  } catch {
    message.warning('加载患者资料失败')
  }
}

const currentPatient = computed(() => {
  const r = detailRecord.value
  if (!r) return null
  const p = patientsByName.value[r.patient]
  return p ? p : { patient_id: '-', user_id: '-', name: r.patient, gender: '-', birthday: '-', id_card: '-', address: '-', emergency_contact: '-', emergency_phone: '-' }
})

async function showDetail(record) {
  detailRecord.value = record
  await ensurePatientLoaded(record.patient)
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

const auth = useAuthStore()
const canEditDraft = computed(() => ['admin', 'doctor', 'nurse'].includes(auth.role))

const editVisible = ref(false)
const editRecord = ref(null)
const editForm = ref({ chiefComplaint: '', diagnosis: '', prescriptions: [], labs: [], imaging: [] })
const imagingOpts = ref([])
const labOpts = ref([])

;(async () => {
  try {
    const dict = await getRecordDictionaries()
    if (dict.code === 200) {
      const imgs = (dict.data.imaging || []).map(v => ({ label: String(v), value: String(v) }))
      const labs = (dict.data.labs || []).map(v => ({ label: String(v), value: String(v) }))
      imagingOpts.value = imgs
      labOpts.value = labs
    }
    if (!imagingOpts.value.length) {
      const r = await getRecordDictionaryImaging()
      if (r.code === 200) imagingOpts.value = (r.data || []).map(v => ({ label: String(v), value: String(v) }))
    }
    if (!labOpts.value.length) {
      const r = await getRecordDictionaryLabs()
      if (r.code === 200) labOpts.value = (r.data || []).map(v => ({ label: String(v), value: String(v) }))
    }
  } catch {
    imagingOpts.value = []
    labOpts.value = []
  }
})()

function openEdit(record) {
  editRecord.value = record
  editForm.value = {
    chiefComplaint: record.chiefComplaint || '',
    diagnosis: record.diagnosis || '',
    prescriptions: Array.isArray(record.prescriptions) ? [...record.prescriptions] : [],
    labs: Array.isArray(record.labs) ? [...record.labs] : [],
    imaging: Array.isArray(record.imaging) ? [...record.imaging] : [],
  }
  editVisible.value = true
}

function addEditItem(listKey, input) {
  const v = (input || '').trim()
  if (!v) return
  const arr = editForm.value[listKey]
  if (!arr.includes(v)) arr.push(v)
}

function removeEditItem(listKey, idx) {
  editForm.value[listKey].splice(idx, 1)
}

async function submitEdit() {
  if (!editRecord.value) return
  const payload = {
    chiefComplaint: editForm.value.chiefComplaint,
    diagnosis: editForm.value.diagnosis,
    prescriptions: editForm.value.prescriptions,
    labs: editForm.value.labs,
    imaging: editForm.value.imaging,
  }
  const res = await updateRecord(editRecord.value.id, payload)
  if (res.code === 200) {
    const r = editRecord.value
    r.chiefComplaint = res.data.chiefComplaint
    r.diagnosis = res.data.diagnosis
    r.prescriptions = res.data.prescriptions
    r.labs = res.data.labs
    r.imaging = res.data.imaging
    r.hasLab = res.data.hasLab
    r.hasImaging = res.data.hasImaging
    message.success('病历更新成功')
    editVisible.value = false
  } else {
    message.error(res.message || '更新失败')
  }
}

</script>

<template>
  <a-card>
    <a-space style="margin-bottom: 12px; width: 100%; justify-content: space-between">
      <div>
        <span style="margin-bottom: 4px">筛选方式：</span>
        <a-radio-group v-model:value="modeFilter" button-style="solid">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="by_patient" v-if="auth.role !== 'patient'">按患者</a-radio-button>
          <a-radio-button value="by_doctor" v-if="auth.role !== 'patient'">按医生</a-radio-button>
          <a-radio-button value="by_date">按日期</a-radio-button>
          <a-radio-button value="by_status">按状态</a-radio-button>
        </a-radio-group>
        <a-radio-group v-if="modeFilter === 'by_status'" v-model:value="statusFilter" style="margin-left: 12px">
          <a-radio-button value="draft">草稿</a-radio-button>
          <a-radio-button value="finalized">定稿</a-radio-button>
          <a-radio-button value="cancelled">作废</a-radio-button>
        </a-radio-group>
        <a-input-search v-if="modeFilter === 'by_patient'" v-model:value="patientKeyword" style="margin-left: 12px; width: 240px" placeholder="输入患者姓名" />
        <a-select v-if="modeFilter === 'by_doctor'" v-model:value="doctorId" :options="doctorOptions" style="margin-left: 12px; width: 260px" placeholder="选择医生" />
        <a-range-picker v-if="modeFilter === 'by_date'" v-model:value="dateRange" style="margin-left: 12px" />
      </div>
      <a-button v-if="auth.role !== 'patient'" type="primary" @click="setMenu('create')">新建病历</a-button>
    </a-space>
    <a-table
      :columns="columns"
      :data-source="filteredRecords"
      :pagination="{ current: currentPage, pageSize: pageSize, total: props.total, showSizeChanger: true, pageSizeOptions: ['10', '20', '50'] }"
      :scroll="{ x: 860 }"
      size="small"
      rowKey="id"
      @change="onTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="{ draft: 'blue', finalized: 'green', cancelled: 'default' }[record.status]">
            {{ { draft: '草稿', finalized: '定稿', cancelled: '作废' }[record.status] }}
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
                  <a-menu-item key="cancelled" @click="onUpdateStatus(record, 'cancelled')">置为作废</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
            <a-button v-if="canEditDraft && record.status === 'draft'" type="link" @click="openEdit(record)">编辑</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>

  <a-modal v-model:open="detailVisible" title="病历详情" :footer="null" width="780px">
    <a-descriptions :column="2" bordered size="small">
      <a-descriptions-item label="病历号">{{ detailRecord?.id }}</a-descriptions-item>
      <a-descriptions-item label="状态">{{ { draft: '草稿', finalized: '定稿', cancelled: '作废' }[detailRecord?.status] }}</a-descriptions-item>
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

  <a-modal v-model:open="editVisible" title="编辑病历" width="720px" @ok="submitEdit">
    <a-form layout="vertical">
      <a-form-item label="主诉">
        <a-textarea v-model:value="editForm.chiefComplaint" :rows="3" placeholder="主诉" />
      </a-form-item>
      <a-form-item label="诊断">
        <a-textarea v-model:value="editForm.diagnosis" :rows="3" placeholder="诊断" />
      </a-form-item>
      <a-form-item label="处方药品">
        <a-input-search placeholder="输入药品名称后回车加入" @search="v => addEditItem('prescriptions', v)" />
        <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap">
          <a-tag v-for="(item, idx) in editForm.prescriptions" :key="item" closable @close.prevent="removeEditItem('prescriptions', idx)" color="blue">{{ item }}</a-tag>
        </div>
      </a-form-item>
      <a-form-item label="检查申请">
        <a-checkbox-group v-model:value="editForm.imaging" :options="imagingOpts" />
      </a-form-item>
      <a-form-item label="检验申请">
        <a-checkbox-group v-model:value="editForm.labs" :options="labOpts" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<style scoped lang="scss"></style>
