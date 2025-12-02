<script setup>
import { computed, ref } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  prescriptions: { type: Array, default: () => [] },
  updateStatus: { type: Function, required: true },
})

const mode = computed(() => {
  const m = props.currentMenu || ''
  if (m.startsWith('prescriptions_')) return m.replace('prescriptions_', '')
  return 'list'
})

const statusFilter = ref('all')

const columns = [
  { title: '处方号', dataIndex: 'id', key: 'id' },
  { title: '患者', dataIndex: 'patient', key: 'patient' },
  { title: '科室', dataIndex: 'department', key: 'department' },
  { title: '医生', dataIndex: 'doctor', key: 'doctor' },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '药品项', key: 'items' },
  { title: '操作', key: 'action' },
]

const filtered = computed(() => {
  if (mode.value === 'review') return props.prescriptions.filter(p => p.status === 'pending')
  if (mode.value === 'dispense') return props.prescriptions.filter(p => p.status === 'approved')
  if (mode.value === 'status') {
    if (statusFilter.value === 'all') return props.prescriptions
    return props.prescriptions.filter(p => p.status === statusFilter.value)
  }
  return props.prescriptions
})

async function approve(record) {
  const ok = await props.updateStatus(record.id, 'approved')
  if (!ok) message.error('审核失败')
}

async function dispense(record) {
  const ok = await props.updateStatus(record.id, 'dispensed')
  if (!ok) message.error('发药失败')
}
</script>

<template>
  <a-card>
    <a-space style="margin-bottom: 12px; width: 100%; justify-content: space-between">
      <div>
        <a-button type="link">处方列表</a-button>
        <a-button type="link">审核</a-button>
        <a-button type="link">发药记录</a-button>
        <a-button type="link">按状态</a-button>
      </div>
      <div v-if="mode === 'status'">
        <a-radio-group v-model:value="statusFilter">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="pending">待审核</a-radio-button>
          <a-radio-button value="approved">已审核</a-radio-button>
          <a-radio-button value="dispensed">已发药</a-radio-button>
        </a-radio-group>
      </div>
    </a-space>

    <a-table :columns="columns" :data-source="filtered" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="{ pending: 'orange', approved: 'blue', dispensed: 'green' }[record.status]">
            {{ { pending: '待审核', approved: '已审核', dispensed: '已发药' }[record.status] }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'items'">
          {{ Array.isArray(record.items) ? record.items.length : 0 }} 项
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button v-if="record.status === 'pending'" type="link" @click="approve(record)">审核通过</a-button>
            <a-button v-if="record.status === 'approved'" type="link" @click="dispense(record)">发药</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<style scoped>
</style>
