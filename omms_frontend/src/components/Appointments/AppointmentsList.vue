<script setup>
import { computed } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  departments: { type: Array, required: true },
  doctors: { type: Array, required: true },
  appointments: { type: Array, required: true },
  setMenu: { type: Function, required: true },
})

const columns = [
  { title: '预约号', dataIndex: 'id', key: 'id' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action' },
]

const filteredAppointments = computed(() => {
  const m = props.currentMenu
  if (m === 'list_pending') return props.appointments.filter(a => a.status === 'pending')
  if (m === 'list_completed') return props.appointments.filter(a => a.status === 'completed')
  if (m === 'list_cancelled') return props.appointments.filter(a => a.status === 'cancelled')
  return props.appointments
})
</script>

<template>
  <a-card title="预约列表">
    <a-space style="margin-bottom: 12px">
      <a-select v-if="currentMenu === 'list_by_department'" style="width: 200px" placeholder="选择科室">
        <a-select-option v-for="d in departments" :key="d" :value="d">{{ d }}</a-select-option>
      </a-select>
      <a-select v-if="currentMenu === 'list_by_doctor'" style="width: 200px" placeholder="选择医生">
        <a-select-option v-for="d in doctors" :key="d" :value="d">{{ d }}</a-select-option>
      </a-select>
      <a-button type="primary" @click="setMenu('create')">新建预约</a-button>
    </a-space>
    <a-table :columns="columns" :data-source="filteredAppointments" :pagination="{ pageSize: 5 }" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="{ pending: 'blue', completed: 'green', cancelled: 'red' }[record.status]">
            {{ { pending: '待就诊', completed: '已完成', cancelled: '已取消' }[record.status] }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="message.info(`查看 ${record.id}`)">详情</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<style scoped lang="scss">
</style>
