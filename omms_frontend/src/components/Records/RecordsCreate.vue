<script setup>
import { ref, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { FileTextOutlined, SolutionOutlined, MedicineBoxOutlined, PictureOutlined, ExperimentOutlined, LeftOutlined } from '@ant-design/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { getDepartments, getDoctorsByDept } from '@/api/appointment'
import { imagingOptions, labOptions } from '@/api/mockData'
import { createRecord, getRecordTemplateById, getRecordTemplates } from '@/api/record'

const router = useRouter()
const route = useRoute()

const props = defineProps({
  departments: { type: Array, default: () => [] },
  doctors: { type: Array, default: () => [] },
  onCreated: { type: Function, default: undefined },
})

const currentStep = ref(0)
const loading = ref(false)

const deptList = ref([])
const doctorList = ref([])
const templatesList = ref([])

const selectedDept = ref(null)
const selectedDoctorId = ref(null)
const selectedTemplateId = ref(null)
const patientName = ref('')
const chiefComplaint = ref('')
const diagnosis = ref('')
const prescriptions = ref([])
const imaging = ref([])
const labs = ref([])
const recordResult = ref(null)
const pendingTemplateDefaults = ref(null)

const steps = [
  { title: '病史采集', icon: FileTextOutlined },
  { title: '诊断信息', icon: SolutionOutlined },
  { title: '处方药品', icon: MedicineBoxOutlined },
  { title: '检查申请', icon: PictureOutlined },
  { title: '检验申请', icon: ExperimentOutlined },
]

onMounted(async () => {
  if ((props.departments || []).length > 0) {
    deptList.value = props.departments
    return
  }
  loading.value = true
  try {
    const res = await getDepartments()
    if (res.code === 200) {
      deptList.value = res.data
    }
  } catch {
    message.error('加载科室数据失败')
  } finally {
    loading.value = false
  }
})

onMounted(async () => {
  try {
    const res = await getRecordTemplates()
    if (res.code === 200) templatesList.value = res.data
  } catch {
    message.error('加载模板列表失败')
  }
})

async function applyTemplateFromRoute() {
  const tplId = route.query.tpl
  if (!tplId) return
  try {
    const res = await getRecordTemplateById(tplId)
    if (res.code === 200) {
      const d = res.data?.defaults || {}
      selectedTemplateId.value = Number(res.data.id)
      pendingTemplateDefaults.value = d
      message.success(`已选择模板：${res.data.name}`)
    }
  } catch {
    message.warning('选择模板失败')
  }
}

onMounted(() => applyTemplateFromRoute())

function applySelectedTemplateDefaults() {
  const d = pendingTemplateDefaults.value
  if (!d) return
  chiefComplaint.value = d.chiefComplaint ?? chiefComplaint.value
  diagnosis.value = d.diagnosis ?? diagnosis.value
  prescriptions.value = Array.isArray(d.prescriptions) ? [...d.prescriptions] : prescriptions.value
  imaging.value = Array.isArray(d.imaging) ? [...d.imaging] : imaging.value
  labs.value = Array.isArray(d.labs) ? [...d.labs] : labs.value
  pendingTemplateDefaults.value = null
  message.success('已应用模板信息')
}

function onSelectTemplate(id) {
  selectedTemplateId.value = id
  const tpl = templatesList.value.find(t => t.id === id)
  pendingTemplateDefaults.value = tpl?.defaults || null
  if (tpl) message.success(`已选择模板：${tpl.name}`)
}

watch(selectedTemplateId, (id) => {
  if (id && currentStep.value > 0) {
    applySelectedTemplateDefaults()
  }
})

const onSelectDept = async (dept) => {
  selectedDept.value = dept
  selectedDoctorId.value = null
  doctorList.value = []

  const allDoctors = props.doctors || []
  if (allDoctors.length > 0) {
    doctorList.value = allDoctors.filter(d => d.deptId === dept.id)
    return
  }

  loading.value = true
  try {
    const res = await getDoctorsByDept(dept.id)
    if (res.code === 200) {
      doctorList.value = res.data
    }
  } catch {
    message.error('加载医生数据失败')
  } finally {
    loading.value = false
  }
}

function nextStep() {
  if (currentStep.value === 0 && pendingTemplateDefaults.value) {
    applySelectedTemplateDefaults()
  }
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function addPrescription(input) {
  const v = (input || '').trim()
  if (!v) return
  prescriptions.value.push(v)
}

function removePrescription(idx) {
  prescriptions.value.splice(idx, 1)
}


async function onSubmit() {
  if (!selectedDept.value || !selectedDoctorId.value) {
    message.warning('请选择科室与医生')
    return
  }
  if (!patientName.value.trim()) {
    message.warning('请输入患者姓名')
    return
  }
  loading.value = true
  try {
    const payload = {
      deptId: selectedDept.value.id,
      doctorId: selectedDoctorId.value,
      patient: patientName.value,
      chiefComplaint: chiefComplaint.value,
      diagnosis: diagnosis.value,
      prescriptions: prescriptions.value,
      imaging: imaging.value,
      labs: labs.value,
    }
    const res = await createRecord(payload)
    if (res.code === 200) {
      recordResult.value = res.data
      message.success('病历创建成功')
      currentStep.value = steps.length
      props.onCreated?.(res.data)
    }
  } catch {
    message.error('病历创建失败，请重试')
  } finally {
    loading.value = false
  }
}

function goToList() {
  router.replace({ path: route.path, query: { ...route.query, menu: 'list_all' } })
}

function reset() {
  currentStep.value = 0
  selectedDept.value = null
  selectedDoctorId.value = null
  patientName.value = ''
  chiefComplaint.value = ''
  diagnosis.value = ''
  prescriptions.value = []
  imaging.value = []
  labs.value = []
  recordResult.value = null
}

</script>

<template>
  <div class="records-create">
    <a-card :bordered="false" class="main-card">
      <a-steps :current="currentStep" class="steps-bar">
        <a-step v-for="item in steps" :key="item.title" :title="item.title">
          <template #icon>
            <component :is="item.icon" />
          </template>
        </a-step>
      </a-steps>

      <div class="step-content">
      <div v-if="currentStep === 0">
        <a-spin :spinning="loading">
          <div class="grid-container">
            <a-card v-for="dept in deptList" :key="dept.id" hoverable class="selection-card" @click="onSelectDept(dept)">
              <template #cover>
                <div class="card-icon bg-blue">
                  <SolutionOutlined />
                </div>
              </template>
              <a-card-meta :title="dept.name">
                <template #description>{{ dept.description }}</template>
              </a-card-meta>
            </a-card>
          </div>
        </a-spin>

        <div class="template-select">
          <div class="label">选择模板：</div>
          <a-select v-model:value="selectedTemplateId" :options="templatesList.map(t => ({ label: t.name, value: t.id }))" style="width: 280px" placeholder="可选，选择后自动填充后续步骤" @change="onSelectTemplate" />
        </div>

        <div v-if="selectedDept" class="doctor-select">
          <div class="label">选择医生：</div>
          <a-select v-model:value="selectedDoctorId" :options="doctorList.map(d => ({ label: `${d.name}（${d.title}）`, value: d.id }))" style="width: 280px" placeholder="请选择医生" />
        </div>

        <div class="patient-input">
          <div class="label">患者姓名：</div>
          <a-input v-model:value="patientName" style="width: 280px" placeholder="请输入患者姓名" />
        </div>

          <div class="actions">
            <a-button type="primary" :disabled="!selectedDept || !selectedDoctorId || !patientName?.trim()" @click="nextStep">下一步</a-button>
          </div>
        </div>

        <div v-if="currentStep === 1">
          <div class="step-header">
            <a-button @click="prevStep" type="text"><LeftOutlined /> 返回</a-button>
            <span class="step-title">诊断信息</span>
          </div>
          <a-textarea v-model:value="chiefComplaint" :rows="3" placeholder="主诉：请描述患者主要不适症状" />
          <a-textarea v-model:value="diagnosis" :rows="3" style="margin-top: 12px" placeholder="诊断：医生的诊断意见" />
          <div class="actions">
            <a-button type="primary" @click="nextStep">下一步</a-button>
          </div>
        </div>

        <div v-if="currentStep === 2">
          <div class="step-header">
            <a-button @click="prevStep" type="text"><LeftOutlined /> 返回</a-button>
            <span class="step-title">处方药品</span>
          </div>
          <a-input-search placeholder="输入药品名称后回车加入" style="max-width: 400px" @search="addPrescription" />
          <div class="prescription-list">
            <a-tag v-for="(item, idx) in prescriptions" :key="item" closable @close.prevent="removePrescription(idx)" color="blue">{{ item }}</a-tag>
          </div>
          <div class="actions">
            <a-button type="primary" @click="nextStep">下一步</a-button>
          </div>
        </div>

        <div v-if="currentStep === 3">
          <div class="step-header">
            <a-button @click="prevStep" type="text"><LeftOutlined /> 返回</a-button>
            <span class="step-title">检查申请</span>
          </div>
          <a-checkbox-group v-model:value="imaging" :options="imagingOptions" />
          <div class="actions">
            <a-button type="primary" @click="nextStep">下一步</a-button>
          </div>
        </div>

        <div v-if="currentStep === 4">
          <div class="step-header">
            <a-button @click="prevStep" type="text"><LeftOutlined /> 返回</a-button>
            <span class="step-title">检验申请</span>
          </div>
          <a-checkbox-group v-model:value="labs" :options="labOptions" />
          <div class="actions">
            <a-button type="primary" :loading="loading" @click="onSubmit">提交病历</a-button>
          </div>
        </div>

        <div v-if="currentStep === 5">
          <a-result status="success" title="病历创建成功" :sub-title="`病历号: ${recordResult?.id || 'MR-20250101-xxxx'}`">
            <template #extra>
              <a-button type="primary" @click="reset">继续创建</a-button>
              <a-button @click="goToList">查看病历列表</a-button>
            </template>
          </a-result>
        </div>
      </div>
    </a-card>
  </div>
</template>

<style scoped lang="scss">
.steps-bar {
  margin-bottom: 40px;
  padding: 0 40px;
}

.step-content {
  min-height: 400px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  padding: 10px;
}

.selection-card {
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s;

  :deep(.ant-card-body) {
    padding: 16px;
  }

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: #1890ff;
  }
}

.card-icon {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  border-radius: 8px 8px 0 0;

  &.bg-blue { background: linear-gradient(135deg, #1890ff, #69c0ff); }
}

.doctor-select,
.patient-input {
  margin-top: 16px;
}

.label {
  margin-bottom: 8px;
  font-weight: 500;
}

.prescription-list {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.actions {
  margin-top: 24px;
}

.step-header {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  .step-title {
    font-size: 16px;
    font-weight: 500;
    margin-left: 16px;
    color: #1890ff;
  }
}

</style>
