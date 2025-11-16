<template>
  <a-layout-sider width="100%" height="100%" style="background: #fff" id="sidebar">
    <a-menu v-model:selectedKeys="selectedKeys" v-model:openKeys="openKeys" mode="inline"
      :style="{ height: '100%', borderRight: 0 }">
      <a-sub-menu key="sub1">
        <template #title>
          <span>
            <UserOutlined />
            subnav 1
          </span>
        </template>
        <a-menu-item key="1">option1</a-menu-item>
        <a-menu-item key="2">option2</a-menu-item>
        <a-menu-item key="3">option3</a-menu-item>
        <a-menu-item key="4">option4</a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="sub2">
        <template #title>
          <span>
            <LaptopOutlined />
            subnav 2
          </span>
        </template>
        <a-menu-item key="5">option5</a-menu-item>
        <a-menu-item key="6">option6</a-menu-item>
        <a-menu-item key="7">option7</a-menu-item>
        <a-menu-item key="8">option8</a-menu-item>
      </a-sub-menu>
      <a-sub-menu key="sub3">
        <template #title>
          <span>
            <NotificationOutlined />
            subnav 3
          </span>
        </template>
        <a-menu-item key="9">option9</a-menu-item>
        <a-menu-item key="10">option10</a-menu-item>
        <a-menu-item key="11">option11</a-menu-item>
        <a-menu-item key="12">option12</a-menu-item>
      </a-sub-menu>
    </a-menu>
  </a-layout-sider>

</template>

<script setup>
import { ref } from 'vue'
import { UserOutlined, LaptopOutlined, NotificationOutlined } from '@ant-design/icons-vue'

const selectedKeys = ref(['1'])
const openKeys = ref(['sub1'])
</script>

<style scoped lang="scss">
#sidebar {
  padding: 8px;
  box-sizing: border-box;
  border-right: 1px solid $border-color;
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
