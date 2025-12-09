<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BarChartOutlined, MedicineBoxOutlined, AreaChartOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import PageLayout from '@/layouts/PageLayout.vue'
import DailyReportsPanel from '@/components/Reports/DailyReportsPanel.vue'
import MonthlyReportsPanel from '@/components/Reports/MonthlyReportsPanel.vue'
import CustomReportsPanel from '@/components/Reports/CustomReportsPanel.vue'
import { getDailyVisits, getDailyDrugs, getMonthlyVisits, getMonthlyDrugs } from '@/api/report'
import { getDepartments, getAllDoctors } from '@/api/appointment'

const route = useRoute()
const router = useRouter()

const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'daily_visits')

const setMenu = key => {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

const departments = ref([])
const doctors = ref([])
const dailyVisits = ref([])
const dailyDrugs = ref([])
const monthlyVisits = ref([])
const monthlyDrugs = ref([])
const loading = ref(false)

const dailyDate = ref(new Date().toISOString().slice(0, 10))
const monthlyKey = ref(new Date().toISOString().slice(0, 7))

const loadBase = async () => {
  const [deptRes, docRes] = await Promise.all([getDepartments(), getAllDoctors()])
  if (deptRes.code === 200) departments.value = deptRes.data
  if (docRes.code === 200) doctors.value = docRes.data
}

const fetchDaily = async (dateStr) => {
  try {
    const [vRes, dRes] = await Promise.all([getDailyVisits(dateStr), getDailyDrugs(dateStr)])
    if (vRes.code === 200) dailyVisits.value = vRes.data
    if (dRes.code === 200) dailyDrugs.value = dRes.data
  } catch (e) {
    console.error(e)
  }
}

const fetchMonthly = async (monthStr) => {
  try {
    const [vRes, dRes] = await Promise.all([getMonthlyVisits(monthStr), getMonthlyDrugs(monthStr)])
    if (vRes.code === 200) monthlyVisits.value = vRes.data
    if (dRes.code === 200) monthlyDrugs.value = dRes.data
  } catch (e) {
    console.error(e)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    await loadBase()
    await fetchDaily(dailyDate.value)
    await fetchMonthly(monthlyKey.value)
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

watch(currentMenu, (m) => {
  if ((m || '').startsWith('daily')) {
    fetchDaily(dailyDate.value)
  } else if ((m || '').startsWith('monthly')) {
    fetchMonthly(monthlyKey.value)
  }
})

function setDailyDate(dateStr) {
  dailyDate.value = dateStr
}

function setMonthlyKey(monthStr) {
  monthlyKey.value = monthStr
}


const metrics = computed(() => {
  const totalDailyVisits = dailyVisits.value.length
  const totalDailyDrugItems = dailyDrugs.value.length
  const monthlyVisitDays = monthlyVisits.value.length
  return { totalDailyVisits, totalDailyDrugItems, monthlyVisitDays }
})

const pagePanels = [
  { key: 'daily', header: '日报' },
  { key: 'monthly', header: '月报' },
  { key: 'custom', header: '自定义报表' },
]

const panelMenuMap = { daily: 'daily_visits', monthly: 'monthly_visits', custom: 'custom_export' }

</script>

<template>
  <PageLayout title="报告管理" desc="就诊/药品日报与月报、自定义报表与导出" :panels="pagePanels" :menu-map="panelMenuMap">
    <template #metrics>
      <div class="metrics-grid">
        <a-card class="metric-card metric-daily-visits" :bordered="false" @click="setMenu('daily_visits')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <BarChartOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">今日就诊</div>
              <div class="metric-value">{{ metrics.totalDailyVisits }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-daily-drugs" :bordered="false" @click="setMenu('daily_drugs')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <MedicineBoxOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">药品使用项</div>
              <div class="metric-value">{{ metrics.totalDailyDrugItems }}</div>
            </div>
          </div>
        </a-card>

        <a-card class="metric-card metric-monthly" :bordered="false" @click="setMenu('monthly_visits')">
          <div class="metric">
            <div class="metric-icon-wrap">
              <AreaChartOutlined class="metric-icon" />
            </div>
            <div class="metric-content">
              <div class="metric-label">月报统计天数</div>
              <div class="metric-value">{{ metrics.monthlyVisitDays }}</div>
            </div>
          </div>
        </a-card>


      </div>
    </template>

    <template #panel-daily>
      <DailyReportsPanel
        :current-menu="currentMenu"
        :visits="dailyVisits"
        :drugs="dailyDrugs"
        :date="dailyDate"
        :set-menu="setMenu"
        :set-date="setDailyDate"
        :fetch-visits="fetchDaily"
        :fetch-drugs="fetchDaily"
      />
    </template>

    <template #panel-monthly>
      <MonthlyReportsPanel
        :current-menu="currentMenu"
        :visits="monthlyVisits"
        :drugs="monthlyDrugs"
        :month-key="monthlyKey"
        :set-menu="setMenu"
        :set-month="setMonthlyKey"
        :fetch-visits="fetchMonthly"
        :fetch-drugs="fetchMonthly"
      />
    </template>

    <template #panel-custom>
      <CustomReportsPanel
        :current-menu="currentMenu"
        :departments="departments"
        :doctors="doctors"
      />
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

.metric-daily-visits {
  background-color: $flat-warm-bg;
  border: 1px solid $flat-warm-border;
  color: $flat-warm-text;
}

.metric-daily-drugs {
  background-color: $flat-info-bg;
  border: 1px solid $flat-info-border;
  color: $flat-info-text;
}

.metric-monthly {
  background-color: $flat-success-bg;
  border: 1px solid $flat-success-border;
  color: $flat-success-text;
}

.metric-templates {
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
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
