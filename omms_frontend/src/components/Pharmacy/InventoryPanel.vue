<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentMenu: { type: String, required: true },
  medicines: { type: Array, default: () => [] },
  batches: { type: Array, default: () => [] },
  logs: { type: Array, default: () => [] },
  setMenu: { type: Function },
})

const mode = computed(() => {
  const m = props.currentMenu || ''
  if (m.startsWith('inventory_')) return m.replace('inventory_', '')
  return 'drugs'
})

const selectedKey = computed(() => {
  const m = props.currentMenu || 'inventory_drugs'
  return m.startsWith('inventory_') ? m : 'inventory_drugs'
})

function onRadioChange(e) {
  const v = e?.target?.value ?? e
  props.setMenu && props.setMenu(v)
}

const drugColumns = [
  { title: '药品名称', dataIndex: 'name', key: 'name' },
  { title: '规格', dataIndex: 'specification', key: 'specification' },
  { title: '单价', dataIndex: 'price', key: 'price' },
  { title: '库存', dataIndex: 'currentStock', key: 'currentStock' },
  { title: '预警值', dataIndex: 'warningStock', key: 'warningStock' },
  { title: '状态', key: 'status' },
]

const batchColumns = [
  { title: '批次号', dataIndex: 'batchNo', key: 'batchNo' },
  { title: '药品', dataIndex: 'medicine', key: 'medicine' },
  { title: '规格', dataIndex: 'specification', key: 'specification' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity' },
  { title: '入库日期', dataIndex: 'receivedAt', key: 'receivedAt' },
  { title: '效期', dataIndex: 'expiryDate', key: 'expiryDate' },
]

const logColumns = [
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '药品', dataIndex: 'medicine', key: 'medicine' },
  { title: '规格', dataIndex: 'specification', key: 'specification' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity' },
  { title: '时间', dataIndex: 'time', key: 'time' },
  { title: '备注', dataIndex: 'note', key: 'note' },
]

const lowStockList = computed(() => props.medicines.filter(m => (m.currentStock ?? 0) <= (m.warningStock ?? 0)))

const expiringList = computed(() => {
  const now = new Date()
  return props.batches.filter(b => {
    const exp = new Date(b.expiryDate)
    const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    return diff >= 0 && diff <= 30
  })
})
</script>

<template>
  <a-card>
    <a-space style="margin-bottom: 12px; width: 100%; justify-content: space-between">
      <a-radio-group :value="selectedKey" @change="onRadioChange">
        <a-radio-button value="inventory_drugs">药品列表</a-radio-button>
        <a-radio-button value="inventory_batches">库存批次</a-radio-button>
        <a-radio-button value="inventory_low_stock">低库存预警</a-radio-button>
        <a-radio-button value="inventory_expiry">近效期批次</a-radio-button>
        <a-radio-button value="inventory_inout">入库/出库记录</a-radio-button>
      </a-radio-group>
    </a-space>

    <a-table v-if="mode === 'drugs'" :columns="drugColumns" :data-source="medicines" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'price'">
          ￥{{ Number(record.price).toFixed(2) }} / {{ record.unit }}
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="(record.currentStock ?? 0) <= (record.warningStock ?? 0) ? 'red' : 'green'">
            {{ (record.currentStock ?? 0) <= (record.warningStock ?? 0) ? '低库存' : '正常' }}
          </a-tag>
        </template>
      </template>
    </a-table>

    <a-table v-else-if="mode === 'batches'" :columns="batchColumns" :data-source="batches" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'expiryDate'">
          <a-tag :color="new Date(record.expiryDate) < new Date() ? 'default' : 'blue'">{{ record.expiryDate }}</a-tag>
        </template>
      </template>
    </a-table>

    <a-table v-else-if="mode === 'low_stock'" :columns="drugColumns" :data-source="lowStockList" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'price'">
          ￥{{ Number(record.price).toFixed(2) }} / {{ record.unit }}
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag color="red">低库存</a-tag>
        </template>
      </template>
    </a-table>

    <a-table v-else-if="mode === 'expiry'" :columns="batchColumns" :data-source="expiringList" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'expiryDate'">
          <a-tag color="orange">{{ record.expiryDate }}</a-tag>
        </template>
      </template>
    </a-table>

    <a-table v-else-if="mode === 'inout'" :columns="logColumns" :data-source="logs" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">
          <a-tag :color="record.type === 'in' ? 'green' : 'blue'">{{ record.type === 'in' ? '入库' : '出库' }}</a-tag>
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<style scoped>
</style>
