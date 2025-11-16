<template>
  <div class="login-page">
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
  align-items: center;
  justify-content: center;
  padding: 0;
  background: #f5f5f5;
}

.login-card {
  width: 420px;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.title {
  text-align: center;
  font-weight: 600;
  font-size: 20px;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 16px;
}

.extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
</style>
