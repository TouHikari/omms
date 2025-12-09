<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  visits: { type: Array, default: () => [] },
  drugs: { type: Array, default: () => [] },
  monthKey: { type: String, default: '' },
  setMenu: { type: Function, required: true },
  setMonth: { type: Function, required: true },
  fetchVisits: { type: Function, required: true },
  fetchDrugs: { type: Function, required: true },
})

const selectedKey = computed(() => {
  const m = props.currentMenu || 'monthly_visits'
  return m.startsWith('monthly_') ? m : 'monthly_visits'
})

function onRadioChange(e) {
  const v = e?.target?.value ?? e
  props.setMenu(v)
}

const visitColumns = [
  { title: '日期', dataIndex: 'date', key: 'date' },
  { title: '就诊数', dataIndex: 'count', key: 'count' },
]

const drugColumns = [
  { title: '日期', dataIndex: 'date', key: 'date' },
  { title: '药品使用项数', dataIndex: 'items', key: 'items' },
]

const exportType = ref('visits')
const exporting = ref(false)

async function onMonthChange(d) {
  const str = d?.format?.('YYYY-MM') || props.monthKey
  props.setMonth(str)
  try {
    if (selectedKey.value === 'monthly_visits') await props.fetchVisits(str)
    else if (selectedKey.value === 'monthly_drugs') await props.fetchDrugs(str)
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
    a.download = `${isVisits ? 'monthly_visits' : 'monthly_drugs'}_${props.monthKey || ''}.csv`
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

</script>

<template>
  <section>
    <a-card :bordered="false">
      <div class="toolbar">
        <a-radio-group :value="selectedKey" @change="onRadioChange">
          <a-radio-button value="monthly_visits">就诊月报</a-radio-button>
          <a-radio-button value="monthly_drugs">药品使用月报</a-radio-button>
          <a-radio-button value="monthly_export">导出CSV</a-radio-button>
        </a-radio-group>

        <a-space>
          <a-date-picker picker="month" @change="onMonthChange" />
        </a-space>
      </div>
    </a-card>

    <a-card v-if="selectedKey === 'monthly_visits'" title="就诊月报" :bordered="false">
      <a-table :columns="visitColumns" :data-source="visits" row-key="date" :pagination="{ pageSize: 31 }" :scroll="{ x: 860 }" />
    </a-card>

    <a-card v-else-if="selectedKey === 'monthly_drugs'" title="药品使用月报" :bordered="false">
      <a-table :columns="drugColumns" :data-source="drugs" row-key="date" :pagination="{ pageSize: 31 }" :scroll="{ x: 860 }" />
    </a-card>

    <a-card v-else title="导出 CSV" :bordered="false">
      <a-space direction="vertical" style="width: 100%">
        <a-radio-group v-model:value="exportType">
          <a-radio value="visits">导出就诊月报</a-radio>
          <a-radio value="drugs">导出药品使用月报</a-radio>
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
