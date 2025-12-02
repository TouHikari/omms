<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { createSupplier } from '@/api/pharmacy'

const props = defineProps({
  currentMenu: { type: String, required: true },
  suppliers: { type: Array, default: () => [] },
  orders: { type: Array, default: () => [] },
  onCreated: { type: Function },
})

const mode = computed(() => {
  const m = props.currentMenu || ''
  if (m.startsWith('suppliers_')) return m.replace('suppliers_', '')
  return 'list'
})

const columns = [
  { title: '供应商名称', dataIndex: 'name', key: 'name' },
  { title: '联系人', dataIndex: 'contact', key: 'contact' },
  { title: '联系电话', dataIndex: 'phone', key: 'phone' },
  { title: '地址', dataIndex: 'address', key: 'address' },
]

const orderColumns = [
  { title: '订单号', dataIndex: 'id', key: 'id' },
  { title: '供应商', dataIndex: 'supplierId', key: 'supplierId' },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '金额', dataIndex: 'amount', key: 'amount' },
]

const name = ref('')
const contact = ref('')
const phone = ref('')
const address = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    const res = await createSupplier({ name: name.value, contact: contact.value, phone: phone.value, address: address.value })
    if (res.code === 200) {
      message.success('供应商创建成功')
      name.value = ''
      contact.value = ''
      phone.value = ''
      address.value = ''
      props.onCreated && props.onCreated()
    } else {
      message.error(res.message || '创建失败')
    }
  } catch {
    message.error('创建失败')
  } finally {
    loading.value = false
  }
}

const supplierNameMap = computed(() => {
  const map = new Map()
  for (const s of props.suppliers) map.set(s.id, s.name)
  return map
})
</script>

<template>
  <a-card>
    <a-space style="margin-bottom: 12px; width: 100%; justify-content: space-between">
      <div>
        <a-button type="link">供应商列表</a-button>
        <a-button type="link">新建供应商</a-button>
        <a-button type="link">采购订单</a-button>
        <a-button type="link">供应商对账</a-button>
      </div>
    </a-space>

    <div v-if="mode === 'list'">
      <a-table :columns="columns" :data-source="suppliers" rowKey="id" />
    </div>

    <div v-else-if="mode === 'create'" class="create-form">
      <a-form layout="vertical">
        <a-form-item label="供应商名称">
          <a-input v-model:value="name" placeholder="请输入供应商名称" />
        </a-form-item>
        <a-form-item label="联系人">
          <a-input v-model:value="contact" placeholder="请输入联系人" />
        </a-form-item>
        <a-form-item label="联系电话">
          <a-input v-model:value="phone" placeholder="请输入联系电话" />
        </a-form-item>
        <a-form-item label="地址">
          <a-input v-model:value="address" placeholder="请输入地址" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" :loading="loading" :disabled="!name?.trim()" @click="submit">创建</a-button>
        </a-form-item>
      </a-form>
    </div>

    <div v-else-if="mode === 'orders'">
      <a-table :columns="orderColumns" :data-source="orders" rowKey="id">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'supplierId'">
            {{ supplierNameMap.get(record.supplierId) || record.supplierId }}
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="{ pending: 'orange', completed: 'green' }[record.status]">{{ { pending: '待处理', completed: '已完成' }[record.status] }}</a-tag>
          </template>
          <template v-else-if="column.key === 'amount'">
            ￥{{ Number(record.amount).toFixed(2) }}
          </template>
        </template>
      </a-table>
    </div>

    <div v-else-if="mode === 'reconciliation'">
      <a-empty description="对账功能暂未接通，后端准备中" />
    </div>
  </a-card>
</template>

<style scoped>
.create-form {
  max-width: 520px;
}
</style>
