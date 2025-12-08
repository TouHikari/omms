<script setup lang="ts">
</script>

<template>
  <section class="layout-container">
    <main class="content-container">
      <slot />
    </main>
  </section>
</template>

<style lang="scss" scoped>
@use '@/assets/_variables.scss' as *;

.layout-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  height: calc(100vh - $header-height-prime - $footer-height-secondary);
}

.content-container {
  padding: 24px;
  width: 100%;
  background-color: $content-bg-color;
  overflow-y: scroll;
}

@media (max-width: $breakpoint-sm) {
  .content-container {
    padding: 16px;
  }
}
</style>
