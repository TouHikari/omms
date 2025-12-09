<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getCustomReportRows } from '@/api/report'

const props = defineProps({
  currentMenu: { type: String, required: true },
  departments: { type: Array, default: () => [] },
  doctors: { type: Array, default: () => [] },
})

const selectedKey = computed(() => {
  const m = props.currentMenu || 'custom_export'
  return m.startsWith('custom_') ? m : 'custom_export'
})

const filterDept = ref(null)
const filterDoctor = ref(null)
const dateRange = ref([])

const fieldOptions = [
  { label: '患者', value: 'patient' },
  { label: '科室', value: 'department' },
  { label: '医生', value: 'doctor' },
  { label: '时间', value: 'time' },
  { label: '状态', value: 'status' },
  { label: '药品项数', value: 'drugItems' },
]
const selectedFields = ref(['patient', 'department', 'doctor', 'time', 'status'])

const rows = ref([])

function toDateStr(d) {
  if (!d) return null
  if (typeof d === 'string') return d.slice(0, 10)
  return d?.format?.('YYYY-MM-DD') || null
}

async function fetchRows() {
  const start = toDateStr((dateRange.value || [])[0])
  const end = toDateStr((dateRange.value || [])[1])
  const { code, data, message: msg } = await getCustomReportRows({ deptName: filterDept.value, doctorName: filterDoctor.value, dateRange: start && end ? [start, end] : null })
  if (code !== 200) {
    message.error(msg || '获取报表数据失败')
    return
  }
  rows.value = data || []
}

function buildColumns() {
  return selectedFields.value.map(f => ({ title: fieldOptions.find(x => x.value === f)?.label || f, dataIndex: f, key: f }))
}

function buildCSV(rows, fields) {
  const fieldMap = Object.fromEntries(fieldOptions.map(f => [f.value, f.label]))
  const header = fields.map(f => fieldMap[f] || f).join(',')
  const body = rows.map(r => fields.map(f => {
    const v = r[f]
    return (v ?? '').toString().replace(/"/g, '""')
  }).join(',')).join('\n')
  return header + '\n' + body
}

function onExport() {
  try {
    const cols = [...selectedFields.value]
    if (!cols.length) {
      message.warning('请至少选择一个字段')
      return
    }
    const csv = buildCSV(rows.value, cols)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `custom_export_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    message.success('CSV 导出成功')
  } catch {
    message.error('导出失败')
  }
}

watch(() => props.currentMenu, (val) => { if (val === 'custom_export') fetchRows() })
watch(filterDept, fetchRows)
watch(filterDoctor, fetchRows)
watch(dateRange, fetchRows)
onMounted(() => fetchRows())

</script>

<template>
  <section>
    <a-card v-if="selectedKey === 'custom_export'" title="导出自定义报表" :bordered="false">
      <a-form layout="inline">
        <a-form-item label="科室">
          <a-select v-model:value="filterDept" style="min-width: 160px" allow-clear :options="(departments || []).map(d => ({ label: d.name || d, value: d.name || d }))" />
        </a-form-item>
        <a-form-item label="医生">
          <a-select v-model:value="filterDoctor" style="min-width: 160px" allow-clear :options="(doctors || []).map(d => ({ label: d.name || d, value: d.name || d }))" />
        </a-form-item>
        <a-form-item label="日期范围">
          <a-range-picker v-model:value="dateRange" />
        </a-form-item>
      </a-form>
      <a-divider />
      <a-space direction="vertical" style="width: 100%">
        <div>
          <span style="margin-right: 12px">选择字段：</span>
          <a-checkbox-group v-model:value="selectedFields" :options="fieldOptions" />
        </div>
        <a-table :columns="buildColumns()" :data-source="rows" row-key="id" :pagination="{ pageSize: 8 }" :scroll="{ x: 860 }" />
        <div style="display: flex; justify-content: flex-end">
          <a-button type="primary" @click="onExport">导出 CSV</a-button>
        </div>
      </a-space>
    </a-card>
  </section>
</template>

<style scoped lang="scss">
</style>
