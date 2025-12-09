<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  visits: { type: Array, default: () => [] },
  drugs: { type: Array, default: () => [] },
  date: { type: String, default: '' },
  setMenu: { type: Function, required: true },
  setDate: { type: Function, required: true },
  fetchVisits: { type: Function, required: true },
  fetchDrugs: { type: Function, required: true },
})

const selectedKey = computed(() => {
  const m = props.currentMenu || 'daily_visits'
  return m.startsWith('daily_') ? m : 'daily_visits'
})

function onRadioChange(e) {
  const v = e?.target?.value ?? e
  props.setMenu(v)
}

const visitColumns = [
  { title: '预约号', dataIndex: 'id', key: 'id' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '状态', dataIndex: 'status', key: 'status' },
]

const drugColumns = [
  { title: '药品', dataIndex: 'medicine', key: 'medicine' },
  { title: '规格', dataIndex: 'specification', key: 'specification' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '日期', dataIndex: 'date', key: 'date' },
]

const exportType = ref('visits')
const exporting = ref(false)

async function onDateChange(d) {
  const str = d?.format?.('YYYY-MM-DD') || props.date
  props.setDate(str)
  try {
    if (selectedKey.value === 'daily_visits') await props.fetchVisits(str)
    else if (selectedKey.value === 'daily_drugs') await props.fetchDrugs(str)
    else await Promise.all([props.fetchVisits(str), props.fetchDrugs(str)])
  } catch {
    message.error('刷新失败')
  }
}

function buildCSV(rows, cols) {
  const header = cols.map(c => c.title).join(',')
  const body = rows.map(r => cols.map(c => {
    const v = r[c.dataIndex]
    return (v ?? '').toString().replace(/"/g, '""')
  }).join(',')).join('\n')
  return header + '\n' + body
}

async function onExport() {
  exporting.value = true
  try {
    const isVisits = exportType.value === 'visits'
    const rows = isVisits ? props.visits : props.drugs
    const cols = isVisits ? visitColumns : drugColumns
    const csv = buildCSV(rows, cols)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${isVisits ? 'daily_visits' : 'daily_drugs'}_${props.date || ''}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    message.success('CSV 导出成功')
  } catch {
    message.error('导出失败')
  } finally {
    exporting.value = false
  }
}

watch(() => props.currentMenu, (m) => {
  const key = (m || '')
  if (key === 'daily_export') exportType.value = 'visits'
})

</script>

<template>
  <section>
    <a-card :bordered="false">
      <div class="toolbar">
        <a-radio-group :value="selectedKey" @change="onRadioChange">
          <a-radio-button value="daily_visits">就诊日报</a-radio-button>
          <a-radio-button value="daily_drugs">药品使用日报</a-radio-button>
          <a-radio-button value="daily_export">导出CSV</a-radio-button>
        </a-radio-group>

        <a-space>
          <a-date-picker @change="onDateChange" />
        </a-space>
      </div>
    </a-card>

    <a-card v-if="selectedKey === 'daily_visits'" title="就诊日报" :bordered="false">
      <a-table :columns="visitColumns" :data-source="visits" row-key="id" :pagination="{ pageSize: 10 }" />
    </a-card>

    <a-card v-else-if="selectedKey === 'daily_drugs'" title="药品使用日报" :bordered="false">
      <a-table :columns="drugColumns" :data-source="drugs" row-key="id" :pagination="{ pageSize: 10 }" />
    </a-card>

    <a-card v-else title="导出 CSV" :bordered="false">
      <a-space direction="vertical" style="width: 100%">
        <a-radio-group v-model:value="exportType">
          <a-radio value="visits">导出就诊日报</a-radio>
          <a-radio value="drugs">导出药品使用日报</a-radio>
        </a-radio-group>
        <a-button type="primary" :loading="exporting" @click="onExport">导出</a-button>
      </a-space>
    </a-card>
  </section>
</template>

<style scoped lang="scss">
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
