<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { MenuOutlined } from '@ant-design/icons-vue'

const drawerVisible = ref(false)
const route = useRoute()

// Close drawer when route changes
watch(() => route.fullPath, () => {
  drawerVisible.value = false
})
</script>

<template>
  <section class="layout-container">
    <section class="sidebar-container">
      <AppSidebar />
    </section>

    <!-- Mobile Sidebar Trigger -->
    <div class="mobile-sidebar-trigger" @click="drawerVisible = true">
      <MenuOutlined />
    </div>

    <!-- Mobile Sidebar Drawer -->
    <a-drawer
      v-model:open="drawerVisible"
      placement="left"
      :closable="false"
      :body-style="{ padding: 0 }"
      width="65vw"
    >
      <div class="brand">
        <i class="brand-icon">
          <img src="/favicon.png" draggable="false" alt="logo" style="height: 100%; width: 100%;" />
        </i>
        <span class="brand-name">在线医疗管理系统 OMMS</span>
      </div>
      <AppSidebar />
    </a-drawer>

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

.mobile-sidebar-trigger {
  display: none;
  position: fixed;
  bottom: 120px;
  left: 0;
  z-index: 999;
  background: $color-primary;
  color: #fff;
  padding: 10px 12px 10px 8px;
  border-radius: 0 24px 24px 0;
  cursor: pointer;
  box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
  font-size: 20px;
  transition: all 0.3s;

  &:hover {
    padding-left: 12px;
  }
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  margin-top: 60px;
  margin-bottom: 20px;
}

.brand-icon {
  height: 20px;
  width: 20px;
}

.brand-name {
  font-weight: 600;
  font-size: 16px;
}

.content-container {
  padding: 24px;
  width: 100%;
  background-color: $content-bg-color;
  overflow-y: scroll;
}

@media (max-width: $breakpoint-md) {
  .sidebar-container {
    display: none;
  }
  .layout-container {
    padding-left: 0;
  }
  .mobile-sidebar-trigger {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: $breakpoint-sm) {
  .content-container {
    padding: 16px;
  }
}
</style>
