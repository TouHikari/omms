<script setup>
import { RouterView, useRoute } from 'vue-router';
import { computed } from 'vue';
import AppHeader from '@/components/AppHeader.vue';
import AppFooter from '@/components/AppFooter.vue';
import DefaultLayout from '@/layouts/DefaultLayout.vue';

const route = useRoute();
const layoutMap = { default: DefaultLayout, blank: 'div' };
const rawLayout = computed(() => route.meta?.layout);
const CurrentLayout = computed(() => {
  const l = rawLayout.value;
  if (!l) return layoutMap.default;
  if (typeof l === 'string') return layoutMap[l] || layoutMap.default;
  return l;
});
const isBlankLayout = computed(() => rawLayout.value === 'blank');
</script>

<template>
  <div v-if="!isBlankLayout" class="app-container">
    <AppHeader />
    <component :is="CurrentLayout">
      <RouterView />
    </component>
    <AppFooter />
  </div>
  <component v-else :is="CurrentLayout">
    <RouterView />
  </component>
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
  height: 100vh;
  padding-top: $header-height-prime;
  padding-bottom: $footer-height-secondary;
  box-sizing: border-box;
}

.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: $header-height-prime;
  z-index: 1000;
}

.footer-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: $footer-height-secondary;
  z-index: 1000;
}
</style>
