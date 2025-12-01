<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  SolutionOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  LeftOutlined
} from '@ant-design/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { getDepartments, getDoctorsByDept, getDoctorSchedules, createAppointment } from '@/api/appointment'

const router = useRouter()
const route = useRoute()

// Define props to avoid warnings, though we might not use them if we fetch data internally
defineProps({
  departments: { type: Array, default: () => [] },
  doctors: { type: Array, default: () => [] },
})

const currentStep = ref(0)
const loading = ref(false)

// Data
const deptList = ref([])
const doctorList = ref([])
const scheduleList = ref([])

// Selections
const selectedDept = ref(null)
const selectedDoctor = ref(null)
const selectedSchedule = ref(null)
const symptomDesc = ref('')
const appointmentResult = ref(null)

// Steps configuration
const steps = [
  { title: '选择科室', icon: SolutionOutlined },
  { title: '选择医生', icon: UserOutlined },
  { title: '选择时间', icon: CalendarOutlined },
  { title: '确认预约', icon: FileTextOutlined },
]

// Fetch departments on init
onMounted(async () => {
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

// Step 1: Select Department
const onSelectDept = async (dept) => {
  selectedDept.value = dept
  selectedDoctor.value = null
  selectedSchedule.value = null
  doctorList.value = []

  loading.value = true
  try {
    const res = await getDoctorsByDept(dept.id)
    if (res.code === 200) {
      doctorList.value = res.data
      currentStep.value++
    }
  } catch {
    message.error('加载医生数据失败')
  } finally {
    loading.value = false
  }
}

// Step 2: Select Doctor
const onSelectDoctor = async (doc) => {
  selectedDoctor.value = doc
  selectedSchedule.value = null
  scheduleList.value = []

  loading.value = true
  try {
    const res = await getDoctorSchedules(doc.id)
    if (res.code === 200) {
      scheduleList.value = res.data
      currentStep.value++
    }
  } catch {
    message.error('加载排班数据失败')
  } finally {
    loading.value = false
  }
}

// Step 3: Select Schedule
const onSelectSchedule = (schedule) => {
  selectedSchedule.value = schedule
  currentStep.value++
}

// Step 4: Submit
const onSubmit = async () => {
  if (!symptomDesc.value.trim()) {
    message.warning('请简要描述您的症状')
    return
  }

  loading.value = true
  try {
    const payload = {
      deptId: selectedDept.value.id,
      doctorId: selectedDoctor.value.id,
      scheduleId: selectedSchedule.value.id,
      symptom: symptomDesc.value,
      patientId: 1 // Mock ID
    }

    const res = await createAppointment(payload)
    if (res.code === 200) {
      appointmentResult.value = res.data
      message.success('预约成功')
      currentStep.value++ // Move to success step (or just show result)
    }
  } catch {
    message.error('预约失败，请重试')
  } finally {
    loading.value = false
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const goToAppointments = () => {
  router.push({ query: { ...route.query, menu: 'list' } })
}

const reset = () => {
  currentStep.value = 0
  selectedDept.value = null
  selectedDoctor.value = null
  selectedSchedule.value = null
  symptomDesc.value = ''
  appointmentResult.value = null
}
</script>

<template>
  <div class="appointments-create">
    <a-card :bordered="false" class="main-card">
      <a-steps :current="currentStep" class="steps-bar">
        <a-step v-for="item in steps" :key="item.title" :title="item.title">
          <template #icon>
            <component :is="item.icon" />
          </template>
        </a-step>
      </a-steps>

      <div class="step-content">
        <!-- Step 0: Department Selection -->
        <div v-if="currentStep === 0">
          <a-spin :spinning="loading">
            <div class="grid-container">
              <a-card
                v-for="dept in deptList"
                :key="dept.id"
                hoverable
                class="selection-card"
                @click="onSelectDept(dept)"
              >
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
        </div>

        <!-- Step 1: Doctor Selection -->
        <div v-if="currentStep === 1">
          <div class="step-header">
            <a-button @click="prevStep" type="text">
              <template #icon><LeftOutlined /></template>
              返回
            </a-button>
            <span class="step-title">当前选择：{{ selectedDept?.name }}</span>
          </div>
          <a-spin :spinning="loading">
             <div v-if="doctorList.length === 0" class="empty-state">该科室暂无医生排班</div>
             <div class="grid-container" v-else>
              <a-card
                v-for="doc in doctorList"
                :key="doc.id"
                hoverable
                class="selection-card"
                @click="onSelectDoctor(doc)"
              >
                <template #cover>
                  <div class="card-icon bg-green">
                    <UserOutlined />
                  </div>
                </template>
                <a-card-meta :title="doc.name">
                  <template #description>
                    <div>{{ doc.title }}</div>
                    <div class="ellipsis">{{ doc.specialty }}</div>
                  </template>
                </a-card-meta>
              </a-card>
            </div>
          </a-spin>
        </div>

        <!-- Step 2: Schedule Selection -->
        <div v-if="currentStep === 2">
          <div class="step-header">
            <a-button @click="prevStep" type="text"> <LeftOutlined /> 返回</a-button>
            <span class="step-title">当前选择：{{ selectedDept?.name }} - {{ selectedDoctor?.name }}</span>
          </div>
          <a-spin :spinning="loading">
            <div v-if="scheduleList.length === 0" class="empty-state">该医生近期无排班</div>
            <div class="grid-container" v-else>
              <a-card
                v-for="sche in scheduleList"
                :key="sche.id"
                hoverable
                class="selection-card schedule-card"
                :class="{ 'disabled': sche.booked >= sche.maxAppointments }"
                @click="sche.booked < sche.maxAppointments && onSelectSchedule(sche)"
              >
                <div class="schedule-date">{{ sche.date }}</div>
                <div class="schedule-time">{{ sche.startTime }} - {{ sche.endTime }}</div>
                <div class="schedule-status">
                  剩余号源: <span :class="sche.booked >= sche.maxAppointments ? 'text-red' : 'text-green'">
                    {{ sche.maxAppointments - sche.booked }}
                  </span>
                </div>
              </a-card>
            </div>
          </a-spin>
        </div>

        <!-- Step 3: Confirmation -->
        <div v-if="currentStep === 3">
           <div class="step-header">
            <a-button @click="prevStep" type="text"> <LeftOutlined /> 返回</a-button>
            <span class="step-title">确认预约信息</span>
          </div>
          <div class="confirm-container">
            <a-descriptions bordered title="预约详情" :column="1">
              <a-descriptions-item label="就诊科室">{{ selectedDept?.name }}</a-descriptions-item>
              <a-descriptions-item label="就诊医生">{{ selectedDoctor?.name }} ({{ selectedDoctor?.title }})</a-descriptions-item>
              <a-descriptions-item label="就诊时间">{{ selectedSchedule?.date }} {{ selectedSchedule?.startTime }}-{{ selectedSchedule?.endTime }}</a-descriptions-item>
              <a-descriptions-item label="挂号费用">¥ 50.00</a-descriptions-item>
            </a-descriptions>

            <div class="symptom-input">
              <div class="label">症状描述 (必填):</div>
              <a-textarea
                v-model:value="symptomDesc"
                placeholder="请简要描述您的不适症状，以便医生提前了解..."
                :rows="4"
                show-count
                :maxlength="200"
              />
            </div>

            <div class="actions">
              <a-button type="primary" size="large" :loading="loading" @click="onSubmit">提交预约</a-button>
            </div>
          </div>
        </div>

        <!-- Step 4: Result -->
        <div v-if="currentStep === 4">
          <a-result
            status="success"
            title="预约成功！"
            :sub-title="`预约单号: ${appointmentResult?.id || 'R-20250101-xxxx'}，请按时就诊。`"
          >
            <template #extra>
              <a-button key="console" type="primary" @click="reset">再预约一个</a-button>
              <a-button key="buy" @click="goToAppointments">查看我的预约</a-button>
            </template>
          </a-result>
        </div>

      </div>
    </a-card>
  </div>
</template>

<style scoped lang="scss">
//.appointments-create {
//  // max-width: 1000px;
//  margin: 0 auto;
//}

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
  &.bg-green { background: linear-gradient(135deg, #52c41a, #95de64); }
}

.schedule-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  border: 1px solid #f0f0f0;

  .schedule-date {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 8px;
  }

  .schedule-time {
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
  }

  .schedule-status {
    font-size: 12px;
    color: #999;
  }

  &.disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
    opacity: 0.7;
    &:hover {
      transform: none;
      box-shadow: none;
      border-color: #f0f0f0;
    }
  }
}

.step-header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;

  .step-title {
    font-size: 16px;
    font-weight: 500;
    margin-left: 16px;
    color: #1890ff;
  }
}

.confirm-container {
  max-width: 600px;
  margin: 0 auto;
}

.symptom-input {
  margin-top: 24px;

  .label {
    margin-bottom: 8px;
    font-weight: 500;
  }
}

.actions {
  margin-top: 32px;
  text-align: center;
}

.text-red { color: #ff4d4f; font-weight: bold; }
.text-green { color: #52c41a; font-weight: bold; }
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
}
</style>
