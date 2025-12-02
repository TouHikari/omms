<script setup>
defineProps({
  doctors: { type: Array, required: true },
})
</script>

<template>
  <a-card>
    <a-table
      :data-source="doctors.map(d => ({ doctor: d, monday: '可约', tuesday: '可约', wednesday: '休', thursday: '可约', friday: '可约' }))"
      :columns="[
        { title: '医生', dataIndex: 'doctor', key: 'doctor' },
        { title: '周一', dataIndex: 'monday', key: 'monday' },
        { title: '周二', dataIndex: 'tuesday', key: 'tuesday' },
        { title: '周三', dataIndex: 'wednesday', key: 'wednesday' },
        { title: '周四', dataIndex: 'thursday', key: 'thursday' },
        { title: '周五', dataIndex: 'friday', key: 'friday' },
      ]"
      :pagination="false"
      :scroll="{ x: 720 }"
      size="small"
      rowKey="doctor.id"
      bordered
    >
      <template #bodyCell="{ column, text }">
        <template v-if="column.key === 'doctor'">
          {{ text.name || text }}
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
