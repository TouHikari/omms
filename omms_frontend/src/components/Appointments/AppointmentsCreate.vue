<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'

defineProps({
  departments: { type: Array, required: true },
  doctors: { type: Array, required: true },
})

const form = ref({ department: undefined, doctor: undefined, date: undefined, time: undefined })

const onCreateSubmit = () => {
  if (!form.value.department || !form.value.doctor || !form.value.date || !form.value.time) {
    message.warning('请填写完整信息')
    return
  }
  message.success('预约已生成')
}
</script>

<template>
  <a-card title="新建预约">
    <a-steps :current="0" style="margin-bottom: 16px">
      <a-step title="选择科室" />
      <a-step title="选择医生" />
      <a-step title="选择时间段" />
      <a-step title="确认生成" />
    </a-steps>
    <a-form layout="inline">
      <a-form-item label="科室">
        <a-select v-model:value="form.department" style="width: 200px" placeholder="选择科室">
          <a-select-option v-for="d in departments" :key="d" :value="d">{{ d }}</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="医生">
        <a-select v-model:value="form.doctor" style="width: 200px" placeholder="选择医生">
          <a-select-option v-for="d in doctors" :key="d" :value="d">{{ d }}</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="日期">
        <a-date-picker v-model:value="form.date" style="width: 180px" />
      </a-form-item>
      <a-form-item label="时间">
        <a-time-picker v-model:value="form.time" style="width: 140px" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onCreateSubmit">生成预约单</a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<style scoped lang="scss">
</style>
