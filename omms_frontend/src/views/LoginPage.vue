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
    <a-card class="login-card" :bordered="false">
      <div class="title">在线医疗管理系统</div>
      <div class="subtitle">账号登录</div>
      <a-alert v-if="errorMsg" type="error" :message="errorMsg" show-icon style="margin-bottom: 12px;" />

      <a-form layout="vertical" :model="form" :rules="rules" @finish="onFinish">
        <a-form-item name="username" label="用户名">
          <a-input v-model:value="form.username" size="large" placeholder="请输入用户名">
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item name="password" label="密码">
          <a-input-password v-model:value="form.password" size="large" placeholder="请输入密码">
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <div class="extra">
          <a-checkbox v-model:checked="form.remember">记住我</a-checkbox>
        </div>

        <a-form-item>
          <a-button type="primary" size="large" block html-type="submit" :loading="loading">登录</a-button>
        </a-form-item>
      </a-form>

    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'

const form = ref({ username: '', password: '', remember: true })
const loading = ref(false)
const errorMsg = ref('')
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
}

const onFinish = async () => {
  loading.value = true
  setTimeout(() => {
    try {
      auth.loginWithPassword({ username: form.value.username, password: form.value.password })
      errorMsg.value = ''
      const redirect = route.query.redirect?.toString() || '/'
      router.replace(redirect)
    } catch (e) {
      errorMsg.value = e.message || '登录失败'
    } finally {
      loading.value = false
    }
  }, 300)
}
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

.login-card {
  width: 440px;
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.24);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  color: #fff;
  position: relative;
  z-index: 2;
}

.title {
  text-align: center;
  font-weight: 600;
  font-size: 20px;
  margin-bottom: 8px;
  color: #fff;
}

.subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 16px;
}

.extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

:deep(.ant-form-item-label > label) {
  color: rgba(255, 255, 255, 0.9);
}

//:deep(.ant-input),
//:deep(.ant-input-affix-wrapper) {
//  background: rgba(255,255,255,0.14);
//  border-color: rgba(255,255,255,0.35);
//  color: #fff;
//}

//:deep(.ant-input::placeholder) {
//  color: rgba(255,255,255,0.75);
//}

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

:deep(.ant-checkbox-wrapper) {
  color: rgba(255, 255, 255, 0.9);
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

  .login-card {
    border-top: 1px solid rgba(255, 255, 255, 0.25);
    padding-top: 24px;
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
  .login-card {
    width: 90%;
    padding: 16px;
  }

  .intro-title {
    //word-break: keep-all;
    //line-break: strict;
    //text-wrap: balance;
    font-size: 8vw;
  }

  :deep(.ant-divider-horizontal) {
    min-width: 0;
    max-width: 80%;
  }
}
</style>
