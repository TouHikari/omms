<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  UserOutlined,
  MedicineBoxOutlined,
  AlertOutlined,
  RightOutlined,
  ScheduleOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import PageLayout from '@/layouts/PageLayout.vue'
import { getDepartments, getAllDoctors, getAppointments } from '@/api/appointment'
import { getMedicines, getInventoryLogs, getPrescriptions } from '@/api/pharmacy'
import { getDailyVisits, getDailyDrugs, getMonthlyVisits, getMonthlyDrugs } from '@/api/report'

const route = useRoute()
const router = useRouter()

// --- State Management ---
const loading = ref(false)
const dailyDate = ref(new Date().toISOString().slice(0, 10))
const monthlyKey = ref(new Date().toISOString().slice(0, 7))

// Data Collections
const appointments = ref([])
const dailyVisits = ref([])
const dailyDrugs = ref([])
const medicines = ref([])
const inventoryLogs = ref([])
const pendingPrescriptions = ref([])
const monthlyVisits = ref([])
const monthlyDrugs = ref([])
const doctors = ref([])
const departments = ref([])

// --- API Calls ---
const loadBase = async () => {
  loading.value = true
  try {
    const [deptRes, docRes, medRes, apptRes, rxRes] = await Promise.all([
      getDepartments(),
      getAllDoctors(),
      getMedicines(),
      getAppointments(),
      getPrescriptions('pending')
    ])
    if (deptRes.code === 200) departments.value = deptRes.data
    if (docRes.code === 200) doctors.value = docRes.data
    if (medRes.code === 200) medicines.value = medRes.data
    if (apptRes.code === 200) appointments.value = apptRes.data
    if (rxRes.code === 200) pendingPrescriptions.value = rxRes.data
  } catch (error) {
    console.error(error)
    message.error('加载基础数据失败')
  } finally {
    loading.value = false
  }
}

const fetchDaily = async () => {
  try {
    const [visitRes, drugRes] = await Promise.all([
      getDailyVisits(dailyDate.value),
      getDailyDrugs(dailyDate.value)
    ])
    if (visitRes.code === 200) dailyVisits.value = visitRes.data
    if (drugRes.code === 200) dailyDrugs.value = drugRes.data
  } catch (e) { console.error(e) }
}

const fetchMonthly = async () => {
  try {
    const [visRes, drugsRes] = await Promise.all([
      getMonthlyVisits(monthlyKey.value),
      getMonthlyDrugs(monthlyKey.value)
    ])
    if (visRes.code === 200) monthlyVisits.value = visRes.data
    if (drugsRes.code === 200) monthlyDrugs.value = drugsRes.data
  } catch (e) { console.error(e) }
}

const refreshLogs = async () => {
  try {
    const res = await getInventoryLogs()
    if (res.code === 200) inventoryLogs.value = res.data
  } catch (e) { console.error(e) }
}

// --- Lifecycle & Watchers ---
onMounted(async () => {
  await loadBase()
  await fetchDaily()
  await fetchMonthly()
  await refreshLogs()
})

watch(dailyDate, () => fetchDaily())
watch(monthlyKey, () => fetchMonthly())

// --- Computed Metrics & Analysis ---

// Top Cards Metrics
const metrics = computed(() => {
  const visits = (dailyVisits.value || []).length
  const pendingRx = (pendingPrescriptions.value || []).length
  const lowStock = medicines.value.filter(m => (m.currentStock ?? 0) <= (m.warningStock ?? 0)).length
  const pendingAppts = appointments.value.filter(a => a.status === 'pending').length
  return { visits, pendingRx, lowStock, pendingAppts }
})

// Overview: Department Load (Progress Bars)
const deptLoad = computed(() => {
  const map = {}
  const total = dailyVisits.value.length || 1
  for (const v of dailyVisits.value) {
    const d = v.department || '未知'
    map[d] = (map[d] || 0) + 1
  }
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, percent: Math.round((count / total) * 100) }))
    .sort((a, b) => b.count - a.count)
})

// Overview: Recent Activities (Timeline)
const recentActivities = computed(() => {
  // Combine visits and logs, sort by time (mocking time for visits as they might only have date)
  // Assuming visits have 'time' field HH:mm:ss from API mock, or just order by index
  const visits = dailyVisits.value.map(v => ({
    type: 'visit',
    time: v.time || '00:00',
    content: `患者 ${v.patient} 完成了 ${v.department} 就诊`,
    color: 'blue'
  }))
  // Take last 5
  return visits.slice(-6).reverse()
})

// Workbench: Pending Appointments
const todoAppointments = computed(() => {
  return appointments.value
    .filter(a => a.status === 'pending')
    .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time))
    .slice(0, 5)
})

// Workbench: Low Stock
const stockAlerts = computed(() => {
  return medicines.value
    .filter(m => (m.currentStock ?? 0) <= (m.warningStock ?? 0))
    .slice(0, 5)
})

// Analysis: Doctor Performance
const doctorPerf = computed(() => {
  const map = {}
  for (const v of dailyVisits.value) {
    const d = v.doctor || '未知'
    map[d] = (map[d] || 0) + 1
  }
  return Object.entries(map)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

// --- Navigation & Layout ---
const pagePanels = [
  { key: 'overview', header: '运营概览' },
  { key: 'workbench', header: '工作台' },
  { key: 'analysis', header: '数据分析' },
]

// Mapping internal keys to query param 'menu' to keep Sidebar sync logic working
// We map our panels to the most relevant Sidebar item
const panelMenuMap = {
  overview: 'view_overview',
  workbench: 'view_work',
  analysis: 'view_analysis'
}

const setMenu = (menuKey) => {
  router.replace({ path: route.path, query: { ...route.query, menu: menuKey } })
}
</script>

<template>
  <PageLayout
    title="医疗数据中心"
    desc="实时监控医疗服务运行状态与核心指标"
    :panels="pagePanels"
    :menu-map="panelMenuMap"
  >
    <!-- Top Metrics Area -->
    <template #metrics>
      <div class="metrics-container">
        <a-card class="metric-card primary" :bordered="false" @click="setMenu('view_overview')">
          <a-statistic :value="metrics.visits" suffix="人次">
            <template #title>
              <span class="metric-title"><UserOutlined /> 今日就诊</span>
            </template>
          </a-statistic>
        </a-card>

        <a-card class="metric-card success" :bordered="false" @click="setMenu('view_work')">
          <a-statistic :value="metrics.pendingAppts" suffix="待办">
            <template #title>
              <span class="metric-title"><ScheduleOutlined /> 预约候诊</span>
            </template>
          </a-statistic>
        </a-card>

        <a-card class="metric-card warning" :bordered="false" @click="setMenu('view_work')">
          <a-statistic :value="metrics.lowStock" suffix="项">
            <template #title>
              <span class="metric-title"><AlertOutlined /> 库存预警</span>
            </template>
          </a-statistic>
        </a-card>

        <a-card class="metric-card info" :bordered="false" @click="setMenu('view_work')">
          <a-statistic :value="metrics.pendingRx" suffix="单">
            <template #title>
              <span class="metric-title"><MedicineBoxOutlined /> 待审处方</span>
            </template>
          </a-statistic>
        </a-card>
      </div>
    </template>

    <!-- Panel: Overview -->
    <template #panel-overview>
      <div class="panel-content">
        <a-row :gutter="[24, 24]">
          <!-- Left: Real-time Timeline -->
          <a-col :xs="24" :lg="14">
            <a-card title="今日实时动态" :bordered="false" class="h-full">
              <template #extra>
                <a-tag color="blue">{{ dailyDate }}</a-tag>
              </template>
              <div v-if="recentActivities.length === 0" class="empty-state">
                <a-empty description="暂无今日动态" />
              </div>
              <a-timeline v-else mode="left">
                <a-timeline-item v-for="(act, idx) in recentActivities" :key="idx" :color="act.color">
                  <span class="timeline-time">{{ act.time }}</span>
                  <span class="timeline-content">{{ act.content }}</span>
                </a-timeline-item>
              </a-timeline>
            </a-card>
          </a-col>

          <!-- Right: Department Distribution -->
          <a-col :xs="24" :lg="10">
            <a-card title="今日科室负荷" :bordered="false" class="h-full">
              <div v-if="deptLoad.length === 0" class="empty-state">
                <a-empty description="暂无数据" />
              </div>
              <div class="dept-list">
                <div v-for="d in deptLoad" :key="d.name" class="dept-item">
                  <div class="dept-info">
                    <span class="dept-name">{{ d.name }}</span>
                    <span class="dept-count">{{ d.count }} 人</span>
                  </div>
                  <a-progress :percent="d.percent" :show-info="false" stroke-color="#1890ff" />
                </div>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </template>

    <!-- Panel: Workbench -->
    <template #panel-workbench>
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :lg="12">
          <a-card title="待处理预约" :bordered="false">
            <template #extra>
              <router-link to="/appointments?tab=pending">查看全部 <RightOutlined /></router-link>
            </template>
            <a-list item-layout="horizontal" :data-source="todoAppointments">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :description="`${item.date} ${item.time} | ${item.department} - ${item.doctor}`"
                  >
                    <template #title>
                      <span class="list-title">{{ item.patient }}</span>
                      <a-tag color="orange" style="margin-left: 8px">待就诊</a-tag>
                    </template>
                    <template #avatar>
                      <a-avatar style="background-color: #87d068">
                        <template #icon><UserOutlined /></template>
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>

        <a-col :xs="24" :lg="12">
          <a-card title="库存预警提醒" :bordered="false">
            <template #extra>
              <router-link to="/pharmacy?tab=inventory">去处理 <RightOutlined /></router-link>
            </template>
            <a-list item-layout="horizontal" :data-source="stockAlerts">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :description="`当前库存: ${item.currentStock} ${item.unit} (预警线: ${item.warningStock})`"
                  >
                    <template #title>
                      <span class="list-title">{{ item.name }}</span>
                      <span style="font-size: 12px; color: #999; margin-left: 8px;">{{ item.specification }}</span>
                    </template>
                    <template #avatar>
                      <a-avatar style="background-color: #ff4d4f">
                        <template #icon><AlertOutlined /></template>
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-button type="link" size="small" danger>补货</a-button>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>
      </a-row>
    </template>

    <!-- Panel: Analysis -->
    <template #panel-analysis>
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :md="16">
          <a-card title="月度趋势分析" :bordered="false">
            <template #extra>
               <a-date-picker v-model:value="monthlyKey" picker="month" value-format="YYYY-MM" :allowClear="false" />
            </template>
            <a-table
              :data-source="monthlyVisits"
              :pagination="{ pageSize: 5 }"
              size="middle"
              :scroll="{ x: 600 }"
              row-key="date"
            >
              <a-table-column title="日期" data-index="date" />
              <a-table-column title="就诊人数" data-index="count">
                <template #default="{ text }">
                   <div class="trend-bar-wrapper">
                     <span style="min-width: 40px">{{ text }}</span>
                     <div class="trend-bar" :style="{ width: Math.min(text * 5, 200) + 'px' }"></div>
                   </div>
                </template>
              </a-table-column>
            </a-table>
          </a-card>
        </a-col>

        <a-col :xs="24" :md="8">
          <a-card title="今日医生接诊排名" :bordered="false">
            <a-list item-layout="horizontal" :data-source="doctorPerf">
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <div class="rank-item">
                    <div class="rank-badge" :class="{ 'top-3': index < 3 }">{{ index + 1 }}</div>
                    <div class="rank-content">
                      <div class="rank-name">{{ item.name }}</div>
                      <div class="rank-value">{{ item.count }} 接诊</div>
                    </div>
                  </div>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </a-col>
      </a-row>
    </template>

  </PageLayout>
</template>

<style lang="scss" scoped>
@use '@/assets/_variables.scss' as *;

.metrics-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}

.metric-card {
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  &.primary :deep(.ant-statistic-title) { color: #1890ff; }
  &.success :deep(.ant-statistic-title) { color: #52c41a; }
  &.warning :deep(.ant-statistic-title) { color: #faad14; }
  &.info :deep(.ant-statistic-title) { color: #722ed1; }
}

.metric-title {
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.timeline-time {
  font-weight: bold;
  margin-right: 8px;
  color: #666;
}

.dept-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dept-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dept-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.trend-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-bar {
  height: 8px;
  background-color: #1890ff;
  border-radius: 4px;
  opacity: 0.6;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f0f0f0;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;

  &.top-3 {
    background-color: #314659;
    color: #fff;
  }
}

.rank-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
}

.rank-value {
  color: #1890ff;
  font-weight: 500;
}

.h-full {
  height: 100%;
}

@container (max-width: $breakpoint-lg) {
  .metrics-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container (max-width: $breakpoint-sm) {
  .metrics-container {
    grid-template-columns: 1fr;
  }
}
</style>
