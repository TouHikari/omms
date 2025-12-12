<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FileTextOutlined, ClockCircleOutlined, CheckCircleOutlined, ExperimentOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import RecordsList from '@/components/Records/RecordsList.vue'
import RecordsCreate from '@/components/Records/RecordsCreate.vue'
import RecordsTemplates from '@/components/Records/RecordsTemplates.vue'
import PageLayout from '@/layouts/PageLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { getDepartments, getAllDoctors } from '@/api/appointment'
import { getRecords, updateRecordStatus } from '@/api/record'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'list_all')

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ref([])
const doctors = ref([])
const records = ref([])
const loading = ref(false)
const recTotal = ref(0)
const recPage = ref(1)
const recPageSize = ref(10)

const loadData = async () => {
  loading.value = true
  try {
    const [deptRes, docRes, recRes] = await Promise.all([
      getDepartments(),
      getAllDoctors(),
      getRecords({ page: recPage.value, pageSize: recPageSize.value })
    ])

    if (deptRes.code === 200) departments.value = deptRes.data
    if (docRes.code === 200) doctors.value = docRes.data
    if (recRes.code === 200) {
      records.value = recRes.data.list || []
      recTotal.value = recRes.data.total || 0
      recPage.value = recRes.data.page || recPage.value
      recPageSize.value = recRes.data.pageSize || recPageSize.value
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

const refreshRecords = async () => {
  try {
    const recRes = await getRecords({ page: recPage.value, pageSize: recPageSize.value })
    if (recRes.code === 200) {
      records.value = recRes.data.list || []
      recTotal.value = recRes.data.total || 0
      recPage.value = recRes.data.page || recPage.value
      recPageSize.value = recRes.data.pageSize || recPageSize.value
    }
  } catch {
    return
  }
}

function onRecordCreated() {
  refreshRecords()
}

watch(currentMenu, (m) => {
  if ((m || '').startsWith('list')) {
    refreshRecords()
  }
})

function onRecordsPagination(pagination) {
  recPage.value = pagination?.current || 1
  recPageSize.value = pagination?.pageSize || recPageSize.value
  refreshRecords()
}

const metrics = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  const totalToday = records.value.filter(r => (r.createdAt || '').slice(0, 10) === todayStr).length
  const draft = records.value.filter(r => r.status === 'draft').length
  const finalized = records.value.filter(r => r.status === 'finalized').length
  const cancelled = records.value.filter(r => r.status === 'cancelled').length
  const withTests = records.value.filter(r => r.hasLab || r.hasImaging).length
  return { totalToday, draft, finalized, cancelled, withTests }
})

async function updateStatus(id, status) {
  try {
    const res = await updateRecordStatus(id, status)
    if (res.code === 200) {
      message.success('状态更新成功')
      const a = records.value.find(x => x.id === id)
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
  const panels = [{ key: 'list', header: '病历列表' }]
  if (['admin', 'doctor'].includes(auth.role)) {
    panels.push({ key: 'create', header: '新建病历' })
    panels.push({ key: 'templates', header: '模板管理' })
  }
  return panels
})

const panelMenuMap = { list: 'list_all', create: 'create', templates: 'templates_list' }

</script>

<template>
  <PageLayout title="病历管理" desc="病历列表、新建病历与模板管理" :panels="pagePanels" :menu-map="panelMenuMap">
    <template #metrics>
      <div class="metrics-grid">
        <a-card class="metric-card metric-today" :bordered="false" @click="setMenu('list_all')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <FileTextOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">今日病历</div>
              <div class="metric-value">{{ metrics.totalToday }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-pending" :bordered="false" @click="setMenu('list_status_draft')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <ClockCircleOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">草稿中</div>
              <div class="metric-value">{{ metrics.draft }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-completed" :bordered="false" @click="setMenu('list_status_finalized')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <CheckCircleOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">已定稿</div>
              <div class="metric-value">{{ metrics.finalized }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-archived" :bordered="false" @click="setMenu('list_status_cancelled')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <FileTextOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">已作废</div>
              <div class="metric-value">{{ metrics.cancelled }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-cancelled" :bordered="false" @click="setMenu('list_lab_imaging')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <ExperimentOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">含检验/检查</div>
              <div class="metric-value">{{ metrics.withTests }}</div>
            </div>
          </div>
        </a-card>
      </div>
    </template>

    <template #panel-list>
      <RecordsList :current-menu="currentMenu" :departments="departments" :doctors="doctors" :records="records" :total="recTotal" :set-menu="setMenu" :update-status="updateStatus" :on-pagination="onRecordsPagination" />
    </template>

    <template #panel-create>
      <RecordsCreate :departments="departments" :doctors="doctors" :on-created="onRecordCreated" />
    </template>

    <template #panel-templates>
      <RecordsTemplates />
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

.metric-archived {
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

@media (min-width: 1600px) {
  .metrics-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

</style>
