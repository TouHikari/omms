<script setup>
import { ref, watch, onMounted } from 'vue'
import { getDoctorSchedules } from '@/api/appointment'

const props = defineProps({
  doctors: { type: Array, required: true },
})

const selectedDoctorId = ref(null)
const schedules = ref([])
const loading = ref(false)

async function loadSchedules() {
  if (!selectedDoctorId.value) return
  loading.value = true
  try {
    const res = await getDoctorSchedules(selectedDoctorId.value)
    schedules.value = res.code === 200 ? res.data : []
  } finally {
    loading.value = false
  }
}

watch(() => selectedDoctorId.value, loadSchedules)
onMounted(() => {
  selectedDoctorId.value = props.doctors?.[0]?.id || null
  loadSchedules()
})
</script>

<template>
  <a-card>
    <a-space style="margin-bottom: 12px">
      <a-select v-model:value="selectedDoctorId" style="min-width: 220px" :options="props.doctors.map(d => ({ value: d.id, label: d.name }))" />
      <a-button type="primary" @click="loadSchedules" :loading="loading">刷新排班</a-button>
    </a-space>
    <a-table
      :data-source="schedules"
      :columns="[
        { title: '日期', dataIndex: 'date', key: 'date' },
        { title: '时间段', key: 'period' },
        { title: '科室', dataIndex: 'deptName', key: 'deptName' },
        { title: '医生', dataIndex: 'doctorName', key: 'doctorName' },
        { title: '可预约', dataIndex: 'availableQuota', key: 'availableQuota' },
      ]"
      :pagination="false"
      :scroll="{ x: 720 }"
      size="small"
      rowKey="id"
      bordered
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'period'">
          {{ record.startTime }} - {{ record.endTime }}
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

:deep(.ant-card) {
  container-type: inline-size;
}

@container (max-width: $breakpoint_md) {
  :deep(.ant-card-body) {
    padding: 12px;
  }
}
</style>
