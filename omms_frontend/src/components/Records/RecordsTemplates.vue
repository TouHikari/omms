<script setup>
import { ref } from 'vue'

const templates = ref([
  { id: 1, name: '内科通用病历模板', scope: '科室', fields: ['主诉', '现病史', '既往史', '诊断', '处方'] },
  { id: 2, name: '外科术后随访模板', scope: '科室', fields: ['术后天数', '伤口情况', '复查项目', '诊断', '处方'] },
  { id: 3, name: '通用简易模板', scope: '通用', fields: ['主诉', '诊断'] },
])

</script>

<template>
  <a-card :bordered="false">
    <a-list :data-source="templates">
      <template #renderItem="{ item }">
        <a-list-item>
          <a-list-item-meta :title="item.name" :description="`范围：${item.scope}`" />
          <div>
            <a-tag v-for="f in item.fields" :key="f" style="margin-right: 8px">{{ f }}</a-tag>
          </div>
          <template #actions>
            <a-button type="link">使用模板</a-button>
            <a-button type="link">编辑</a-button>
          </template>
        </a-list-item>
      </template>
    </a-list>
  </a-card>
</template>

<style scoped lang="scss"></style>
