<template>
  <div class="app-header">
    <div class="brand">
      <i class="brand-icon">
        <img src="/favicon.png" draggable="false" alt="logo" style="height: 100%; width: 100%;" />
      </i>
      <span class="brand-name">在线医疗管理系统 OMMS</span>
    </div>

    <a-menu mode="horizontal" v-model:selectedKeys="selectedMenuKeys" :style="{ flex: 1, minWidth: '480px' }">
      <a-menu-item key="appointments">预约管理</a-menu-item>
      <a-menu-item key="records">病历管理</a-menu-item>
      <a-menu-item key="pharmacy">药品与库存</a-menu-item>
      <a-menu-item key="inpatient">住院管理</a-menu-item>
      <a-menu-item key="payments">在线支付</a-menu-item>
      <a-menu-item key="reports">报表统计</a-menu-item>
    </a-menu>

    <div class="actions">
      <a-input-search v-model:value="searchValue" class="search" placeholder="搜索预约/病历/处方..."
        :style="{ width: '280px' }" />

      <a-dropdown>
        <div class="user" role="button">
          <a-avatar size="small" icon="" />
          <span class="user-name">管理员</span>
          <DownOutlined />
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="profile">
              <UserOutlined />
              个人中心
            </a-menu-item>
            <a-menu-item key="settings">
              <SettingOutlined />
              系统设置
            </a-menu-item>
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
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  DownOutlined,
  LogoutOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'

const selectedMenuKeys = ref(['appointments'])
const searchValue = ref('')
const router = useRouter()
const auth = useAuthStore()

function onLogout() {
  auth.logout()
  router.replace('/login')
}
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.app-header {
  display: flex;
  align-items: center;
  gap: 16px;
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
  font-size: 18px;
}

.user {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
