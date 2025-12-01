<script setup>
defineProps({
  departments: { type: Array, required: true },
})
</script>

<template>
  <a-card title="科室设置">
    <a-row :gutter="12">
      <a-col :span="6" v-for="d in departments" :key="d.id || d">
        <a-card :title="d.name || d" size="small">
          <a-space>
            <a-button type="link">编辑</a-button>
            <a-button type="link">排班配置</a-button>
          </a-space>
        </a-card>
      </a-col>
    </a-row>
    <a-space style="margin-top: 12px">
      <a-button type="primary">新建科室</a-button>
    </a-space>
  </a-card>
</template>

<style scoped lang="scss">
</style>
