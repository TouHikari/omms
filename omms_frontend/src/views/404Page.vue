<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => router.replace('/')
</script>

<template>
  <div class="not-found-container">
    <h2 class="not-found-title">404</h2>
    <a-divider>Not Found</a-divider>
    <p class="not-found-message">Oops! 很抱歉，页面不存在</p>
    <div class="not-found-actions">
      <a-button size="large" @click="goHome">返回主页</a-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.not-found-title {
  font-size: 128px;
  font-weight: bold;
  font-family: 'JetBrains Mono', sans-serif;
  margin: 0;
  background: linear-gradient(120deg, #ff7a45 0%, #ff4d4f 50%, #cf1322 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

.not-found-message {
  font-size: 18px;
}
.not-found-actions {
  margin-top: 16px;
}

@media (max-width: $breakpoint-md) {
  .not-found-title {
    font-size: 80px;
  }
}

@media (max-width: $breakpoint-xs) {
  .not-found-title {
    font-size: 60px;
  }
  .not-found-message {
    font-size: 16px;
    padding: 0 16px;
    text-align: center;
  }
}
</style>
