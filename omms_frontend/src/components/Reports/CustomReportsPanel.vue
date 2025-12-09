<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'

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
const selectedFields = ref(['patient', 'department', 'doctor', 'time'])

const previewRows = ref([
  { patient: '张三', department: '内科', doctor: '王医生', time: '2025-12-09 09:35', status: 'completed', drugItems: 2 },
  { patient: '李四', department: '儿科', doctor: '李医生', time: '2025-12-09 10:20', status: 'pending', drugItems: 1 },
  { patient: '王五', department: '外科', doctor: '赵医生', time: '2025-12-08 14:00', status: 'completed', drugItems: 3 },
])

const filtered = computed(() => {
  let rows = previewRows.value
  if (filterDept.value) rows = rows.filter(r => r.department === filterDept.value)
  if (filterDoctor.value) rows = rows.filter(r => r.doctor === filterDoctor.value)
  const [start, end] = dateRange.value || []
  if (start && end) {
    const s = start?.toDate?.() ? start.toDate().getTime() : 0
    const e = end?.toDate?.() ? end.toDate().getTime() : Number.MAX_SAFE_INTEGER
    rows = rows.filter(r => {
      const t = new Date(r.time.replace(' ', 'T')).getTime()
      return t >= s && t <= e
    })
  }
  return rows
})

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
    const csv = buildCSV(filtered.value, cols)
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

watch(() => props.currentMenu, () => {})

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
        <a-table :columns="buildColumns()" :data-source="filtered" row-key="time" :pagination="{ pageSize: 8 }" />
        <div style="display: flex; justify-content: flex-end">
          <a-button type="primary" @click="onExport">导出 CSV</a-button>
        </div>
      </a-space>
    </a-card>
  </section>
</template>

<style scoped lang="scss">
</style>
