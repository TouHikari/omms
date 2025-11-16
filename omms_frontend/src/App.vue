<script setup>
import { RouterView } from 'vue-router';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
</script>

<template>
  <AppHeader />
  <RouterView />
  <AppFooter />
</template>

<style lang="scss">
@use '@/assets/main.scss' as *;

#app {
  position: relative;
  min-height: 100vh;
}

html,
body {
  margin: 0;
}
</style>
