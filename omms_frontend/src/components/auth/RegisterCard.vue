<template>
  <a-card class="login-card" :bordered="false">
    <div class="title">在线医疗管理系统</div>
    <div class="subtitle">账号注册</div>
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

      <a-form-item name="confirmPassword" label="确认密码">
        <a-input-password v-model:value="form.confirmPassword" size="large" placeholder="请再次输入密码">
          <template #prefix>
            <LockOutlined />
          </template>
        </a-input-password>
      </a-form-item>

      <a-form-item name="realName" label="真实姓名">
        <a-input v-model:value="form.realName" size="large" placeholder="请输入真实姓名">
          <template #prefix>
            <IdcardOutlined />
          </template>
        </a-input>
      </a-form-item>

      <a-form-item name="email" label="邮箱">
        <a-input v-model:value="form.email" size="large" placeholder="请输入邮箱">
          <template #prefix>
            <MailOutlined />
          </template>
        </a-input>
      </a-form-item>

      <a-form-item name="phone" label="手机号">
        <a-input v-model:value="form.phone" size="large" placeholder="请输入手机号">
          <template #prefix>
            <PhoneOutlined />
          </template>
        </a-input>
      </a-form-item>

      <a-form-item>
        <a-button type="primary" size="large" block html-type="submit" :loading="loading">注册</a-button>
      </a-form-item>
    </a-form>

    <div style="text-align:center;margin-top:8px;">
      <a href="#" @click.prevent="goToLogin">已有账号？去登录</a>
    </div>

  </a-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, IdcardOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const emit = defineEmits(['switch-mode'])

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  realName: '',
  email: '',
  phone: ''
})
const loading = ref(false)
const errorMsg = ref('')
const router = useRouter()
const auth = useAuthStore()

const validateConfirmPassword = async (_rule, value) => {
  if (value === '') {
    return Promise.reject('请再次输入密码')
  } else if (value !== form.password) {
    return Promise.reject('两次输入的密码不一致')
  } else {
    return Promise.resolve()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
  confirmPassword: [{ required: true, validator: validateConfirmPassword }],
  realName: [{ required: true, message: '请输入真实姓名' }],
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '请输入有效的邮箱地址' }
  ],
  phone: [{ required: true, message: '请输入手机号' }]
}

const onFinish = async () => {
  loading.value = true
  try {
    await auth.registerWithApi({
      username: form.username,
      password: form.password,
      email: form.email,
      phone: form.phone,
      realName: form.realName
    })
    errorMsg.value = ''
    message.success('注册成功，请登录')
    emit('switch-mode', 'login')
  } catch (e) {
    errorMsg.value = e.message || '注册失败'
    message.error(errorMsg.value)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  emit('switch-mode', 'login')
}
</script>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.login-card {
  width: 440px;
  // Increase height/scroll handling if form is too long
  max-height: 90vh;
  overflow-y: auto;
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

:deep(.ant-form-item-label > label) {
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
