<template>
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

    <div style="text-align:center;margin-top:8px;">
      <a href="#" @click.prevent="goToRegister">没有账号？去注册</a>
    </div>

    <div class="quick-login">
      <div class="quick-title">快速登录</div>
      <a-space wrap>
        <a-button size="small" @click="fillAndLogin('admin@omms','admin123')">管理员</a-button>
        <a-button size="small" @click="fillAndLogin('doctor001','omms123')">医生</a-button>
        <a-button size="small" @click="fillAndLogin('nurse001','omms123')">护士</a-button>
        <a-button size="small" @click="fillAndLogin('patient001','omms123')">患者</a-button>
      </a-space>
    </div>

  </a-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const emit = defineEmits(['switch-mode'])

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
  setTimeout(async () => {
    try {
      await auth.loginWithApi({ username: form.value.username, password: form.value.password })
      errorMsg.value = ''
      message.success('登录成功')
      const redirect = route.query.redirect?.toString() || '/'
      router.replace(redirect)
    } catch (e) {
      errorMsg.value = e.message || '登录失败'
      message.error(errorMsg.value)
    } finally {
      loading.value = false
    }
  }, 300)
}

const fillAndLogin = (u, p) => {
  form.value.username = u
  form.value.password = p
  onFinish()
}

const goToRegister = () => {
  emit('switch-mode', 'register')
}
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

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

.quick-login {
  margin-top: 8px;
}

.quick-title {
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  margin-bottom: 6px;
}

:deep(.ant-form-item-label > label) {
  color: rgba(255, 255, 255, 0.9);
}

:deep(.ant-checkbox-wrapper) {
  color: rgba(255, 255, 255, 0.9);
}

@media (max-width: $breakpoint-lg) {
  .login-card {
    border-top: 1px solid rgba(255, 255, 255, 0.25);
    padding-top: 24px;
  }
}

@media (max-width: $breakpoint-xs) {
  .login-card {
    width: 90%;
    padding: 16px;
  }
}
</style>
