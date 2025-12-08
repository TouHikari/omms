<template>
  <section class="footer-container">
    <span>在线医疗管理系统（OMMS）</span>
    <span title="哪有什么版权（">版权所有 &copy; 2025</span>
  </section>
</template>

<style lang="scss" scoped>
@use '@/assets/_variables.scss' as *;

.footer-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background-color: #f5f7fa;
  text-align: center;
  color: #606266;
  font-size: 14px;
  height: $footer-height-secondary;
  box-sizing: border-box;
  border-top: 1px solid $border-color;
}
</style>
