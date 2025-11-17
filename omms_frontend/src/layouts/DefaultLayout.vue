<script setup lang="ts">
</script>

<template>
  <section class="layout-container">
    <section class="sidebar-container">
      <AppSidebar />
    </section>
    <main class="content-container">
      <slot />
    </main>
  </section>
</template>

<style lang="scss" scoped>
@use '@/assets/_variables.scss' as *;

.sidebar-container {
  position: fixed;
  top: $header-height-prime;
  bottom: $footer-height-secondary;
  left: 0;
  width: $sidebar-width;
  overflow-y: auto;
}

.layout-container {
  display: flex;
  flex-direction: row;
  height: calc(100vh - $header-height-prime - $footer-height-secondary);
  padding-left: $sidebar-width;
}

.content-container {
  padding: 24px;
  width: 100%;
  background-color: $content-bg-color;
  overflow-y: scroll;
}
</style>
