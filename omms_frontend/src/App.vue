<script setup>
import { RouterView, useRoute } from 'vue-router';
import { computed } from 'vue';
import AppHeader from '@/components/AppHeader.vue';
import AppFooter from '@/components/AppFooter.vue';
import DefaultLayout from '@/layouts/DefaultLayout.vue';

const route = useRoute();
const isBlankLayout = computed(() => route.meta?.layout === 'blank');
</script>

<template>
  <div v-if="!isBlankLayout" class="app-container">
    <AppHeader />
    <DefaultLayout>
      <RouterView />
    </DefaultLayout>
    <AppFooter />
  </div>
  <RouterView v-else />
</template>

<style lang="scss">
@use '@/assets/main.scss' as *;

html,
body {
  margin: 0;
}

#app {
  position: relative;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
