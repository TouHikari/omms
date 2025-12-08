<template>
  <div class="login-page">
    <video class="bg-video" src="/video.min.mp4" autoplay muted loop playsinline></video>
    <div class="bg-mask"></div>
    <div class="login-left">
      <div class="intro">
        <h2 class="intro-title">医者之心，数据之光</h2>
        <p class="intro-desc">
          仁术为本，数据为器；<br />
          诊治有序，合规如磐。
        </p>
      </div>
    </div>
    <a-divider />
    <a-divider type="vertical" />

    <!-- Dynamic Component Injection -->
    <transition name="fade" mode="out-in">
      <component :is="currentComponent" @switch-mode="handleSwitchMode" />
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoginCard from '@/components/auth/LoginCard.vue'
import RegisterCard from '@/components/auth/RegisterCard.vue'

const route = useRoute()
const router = useRouter()
const mode = ref('login') // 'login' or 'register'

const currentComponent = computed(() => {
  return mode.value === 'register' ? RegisterCard : LoginCard
})

const handleSwitchMode = (newMode) => {
  mode.value = newMode
  // Optionally update URL without reloading
  if (newMode === 'register') {
    router.replace('/register')
  } else {
    router.replace('/login')
  }
}

// Sync with route on mount and change
const syncModeFromRoute = () => {
  if (route.path === '/register') {
    mode.value = 'register'
  } else {
    mode.value = 'login'
  }
}

onMounted(() => {
  syncModeFromRoute()
})

watch(
  () => route.path,
  () => {
    syncModeFromRoute()
  }
)
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.login-page {
  height: 100vh;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.bg-video {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
  pointer-events: none;
  filter: brightness(0.6) saturate(0.95);
}

.bg-mask {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.4) 100%);
  z-index: 1;
  pointer-events: none;
}

.login-left {
  width: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.intro {
  max-width: 480px;
}

.intro-title {
  font-size: 50px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  word-break: break-all;
}

.intro-desc {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

:deep(.ant-divider-vertical) {
  height: 320px;
  border-left-color: rgba(255, 255, 255, 0.25);
  margin: 0 24px;
  position: relative;
  z-index: 2;
}

:deep(.ant-divider-horizontal) {
  display: none;
  min-width: 0;
  max-width: 400px;
  border-top-color: rgba(255, 255, 255, 0.25);
  margin: 24px 0 40px 0;
  position: relative;
  z-index: 2;
}

/* Transition effects */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: $breakpoint-lg) {
  .login-page {
    max-height: 90vh;
    flex-direction: column;
    justify-content: center;
    padding: 24px;
  }

  .intro {
    text-align: center;
  }

  :deep(.ant-divider-vertical) {
    display: none;
  }

  :deep(.ant-divider-horizontal) {
    display: flex;
  }
}

@media (max-width: $breakpoint-sm) {
  .intro-title {
    font-size: 40px;
  }

  .intro-desc {
    font-size: 14px;
  }
}

@media (max-width: $breakpoint-xs) {
  .intro-title {
    font-size: 8vw;
  }

  :deep(.ant-divider-horizontal) {
    min-width: 0;
    max-width: 80%;
  }
}
</style>
