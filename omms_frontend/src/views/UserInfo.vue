<template>
  <section class="user-info-page">
    <a-card :bordered="false" class="user-card">
      <div class="user-header">
        <a-avatar :size="64" :style="avatarStyle">{{ avatarLetter }}</a-avatar>
        <div class="user-basic">
          <div class="user-name">{{ displayName }}</div>
          <div class="user-role">{{ roleLabel }}</div>
        </div>
        <a-space>
          <a-button type="default" @click="refresh">刷新资料</a-button>
          <a-button type="primary" @click="goHome">返回首页</a-button>
        </a-space>
      </div>

      <a-divider />

      <a-descriptions title="基础信息" :column="responsiveColumns">
        <a-descriptions-item label="用户ID">{{ userId }}</a-descriptions-item>
        <a-descriptions-item label="用户名">{{ username || '-' }}</a-descriptions-item>
        <a-descriptions-item label="邮箱">{{ email || '-' }}</a-descriptions-item>
        <a-descriptions-item label="手机号">{{ phone || '-' }}</a-descriptions-item>
      </a-descriptions>

    </a-card>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const displayName = computed(() => auth.user?.name || auth.user?.username || '')
const avatarLetter = computed(() => (displayName.value || 'U')[0]?.toUpperCase?.() || 'U')
const avatarStyle = { color: '#f56a00', backgroundColor: '#fde3cf' }
const roleLabel = computed(() => {
  const m = { admin: '管理员', doctor: '医生', nurse: '护士', patient: '患者' }
  return m[auth.role || 'patient'] || '患者'
})

const userId = computed(() => auth.user?.id || '-')
const username = computed(() => auth.user?.username || '')
const email = computed(() => auth.user?.email || '')
const phone = computed(() => auth.user?.phone || '')

const responsiveColumns = ref(3)

onMounted(async () => {
  try {
    if (auth.isAuthenticated) {
      await auth.fetchMe()
    }
  } catch {
    // ignore errors; page still shows whatever we have
  }
})

function refresh() {
  auth.fetchMe().catch(() => {})
}

function goHome() {
  router.push('/')
}
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.user-info-page {
  display: flex;
  justify-content: center;
}

.user-card {
  max-width: 900px;
  width: 100%;
  background: #fff;
}

.user-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-basic {
  flex: 1;
  margin: 0 16px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
}

.user-role {
  color: #888;
  margin-top: 4px;
}

@media (max-width: $breakpoint-sm) {
  .user-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
