<template>
  <div class="app-header">
    <div class="brand">
      <i class="brand-icon">
        <img src="/favicon.png" draggable="false" alt="logo" style="height: 100%; width: 100%;" />
      </i>
      <span class="brand-name">
        <span class="brand-name-primary">在线医疗管理系统 </span>
        <span class="brand-name-secondary">OMMS</span></span>
    </div>

    <a-menu class="nav" mode="horizontal" v-model:selectedKeys="selectedMenuKeys" @select="onMenuSelect">
      <template #overflowedIndicator>
        <EllipsisOutlined />
      </template>
      <a-menu-item key="dashboard">数据看板</a-menu-item>
      <a-menu-item key="appointments">预约管理</a-menu-item>
      <a-menu-item key="records">病历管理</a-menu-item>
      <a-menu-item key="pharmacy">药品与库存</a-menu-item>
      <!--<a-menu-item key="inpatient">住院管理</a-menu-item>-->
      <!--<a-menu-item key="payments">在线支付</a-menu-item>-->
      <a-menu-item key="reports">报表统计</a-menu-item>
    </a-menu>

    <div class="actions">
      <div class="mobile-menu-trigger" role="button" @click="mobileMenuOpen = true">
        <MenuOutlined class="action-icon" />
      </div>
      <div class="search-trigger">
        <a-popover placement="bottomRight">
          <template #content>
            <a-input-search v-model:value="searchValue" size="middle" placeholder="搜索预约/病历/处方..." style="width: 260px;" />
          </template>
          <a-button type="text" class="action-icon" aria-label="搜索">
            <SearchOutlined />
          </a-button>
        </a-popover>
      </div>
      <a-input-search v-model:value="searchValue" class="search" placeholder="搜索预约/病历/处方..." />

      <a-dropdown>
        <div class="user" role="button">
          <a-avatar size="small" :style="avatarStyle">{{ avatarLetter }}</a-avatar>
          <span class="user-name">{{ displayName }}</span>
          <DownOutlined style="font-size: 10px;" />
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="profile" @click="goProfile">
              <UserOutlined />
              个人中心
            </a-menu-item>
            <!--<a-menu-item key="settings">
              <SettingOutlined />
              系统设置
            </a-menu-item>-->
            <a-menu-divider />
            <a-menu-item key="logout" @click="onLogout">
              <LogoutOutlined />
              退出登录
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </div>

  <a-drawer :open="mobileMenuOpen" placement="top" :height="440" @close="mobileMenuOpen = false" title="功能导航">
    <a-menu mode="inline" v-model:selectedKeys="selectedMenuKeys" @select="onMenuSelect">
      <a-menu-item key="dashboard">数据看板</a-menu-item>
      <a-menu-item key="appointments">预约管理</a-menu-item>
      <a-menu-item key="records">病历管理</a-menu-item>
      <a-menu-item key="pharmacy">药品与库存</a-menu-item>
      <!--<a-menu-item key="inpatient">住院管理</a-menu-item>-->
      <!--<a-menu-item key="payments">在线支付</a-menu-item>-->
      <a-menu-item key="reports">报表统计</a-menu-item>
    </a-menu>
  </a-drawer>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  DownOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuOutlined,
  EllipsisOutlined,
  SearchOutlined,
} from '@ant-design/icons-vue'

const selectedMenuKeys = ref(['dashboard'])
const searchValue = ref('')
const mobileMenuOpen = ref(false)
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const displayName = computed(() => auth.user?.name || auth.user?.username || '未登录')
const avatarLetter = computed(() => (displayName.value || 'A').slice(0, 1).toUpperCase())
const avatarStyle = { color: '#f56a00', backgroundColor: '#fde3cf' }

onMounted(async () => {
  try {
    if (auth.isAuthenticated && !auth.user) {
      await auth.fetchMe()
    }
  } catch (e) {
    void e
  }
})

function onLogout() {
  auth.logout()
  router.replace('/login')
}

const keyToPath = {
  dashboard: '/',
  appointments: '/appointments',
  records: '/records',
  pharmacy: '/pharmacy',
  //inpatient: '/inpatient',
  //payments: '/payments',
  reports: '/reports',
}

function onMenuSelect({ key }) {
  const path = keyToPath[key]
  const defaultMenuByKey = {
    dashboard: 'overview_today',
    appointments: 'list_all',
    records: 'list_all',
    pharmacy: 'inventory_drugs',
    //inpatient: 'wards_list',
    //payments: 'transactions_list',
    reports: 'daily_visits',
  }
  if (path) {
    const menu = defaultMenuByKey[key]
    router.push(menu ? { path, query: { menu } } : { path })
    mobileMenuOpen.value = false
  }
}

function goProfile() {
  router.push('/user')
}

function syncSelected() {
  const path = route.path
  const pairs = Object.entries(keyToPath)
  const found = pairs.find(([, p]) => p === path)
  selectedMenuKeys.value = found ? [found[0]] : []
}

watch(() => route.path, syncSelected, { immediate: true })
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: $header-height-prime;
  box-sizing: border-box;
  border-bottom: 1px solid $border-color;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 280px;
}

.brand-icon {
  height: 20px;
  width: 20px;
}

.brand-name {
  font-weight: 600;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.user-name {
  white-space: nowrap;
}

.nav {
  flex: 1;
  min-width: 10px;
}

.mobile-menu-trigger {
  display: none;
}

.search {
  width: 280px;
}

.search-trigger {
  display: none;
}

@media (max-width: $breakpoint-xl) {
  .actions {
    gap: 8px;
  }
  .search {
    width: 100% !important;
  }
}

@media (max-width: $breakpoint-lg) {
  .search {
    display: none;
  }
  .search-trigger {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: $breakpoint-md) {
  .brand {
    min-width: auto;
  }
  .nav {
    display: none;
  }
  .mobile-menu-trigger {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: $breakpoint-xs) {
  .brand {
    min-width: auto;
  }
  .brand-name-primary {
    display: none;
  }
}
</style>
