<template>
  <a-layout-sider width="100%" height="100%" style="background: #fff" id="sidebar">
    <a-menu
      v-model:selectedKeys="state.selectedKeys"
      style="width: 256px"
      mode="inline"
      :open-keys="state.openKeys"
      :items="items"
      :style="{ height: '100%', borderRight: 0 }"
      @openChange="onOpenChange"
      @select="onSelect"
    >
    </a-menu>
  </a-layout-sider>
</template>

<script setup>
import { reactive, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

function getItem(label, key, icon, children, type) {
  return {
    key,
    icon,
    children,
    label,
    type,
  };
}
const route = useRoute()
const router = useRouter()

const state = reactive({
  rootSubmenuKeys: [],
  openKeys: [],
  selectedKeys: [],
})

const items = computed(() => {
  const sidebar = route.meta?.sidebar || []
  const groups = sidebar.map(g => getItem(g.label, g.key, undefined, (g.children || []).map(c => getItem(c.label, c.key))))
  return groups
})

const rootSubmenuKeys = computed(() => items.value.map(g => g.key))

watch(rootSubmenuKeys, (keys) => {
  state.rootSubmenuKeys = keys
  if (!state.openKeys.length) {
    state.openKeys = keys.length ? [keys[0]] : []
  }
}, { immediate: true })

watch(() => route.path, () => {
  const first = rootSubmenuKeys.value[0]
  state.openKeys = first ? [first] : []
})

const onOpenChange = openKeys => {
  const latestOpenKey = openKeys.find(key => state.openKeys.indexOf(key) === -1)
  if (state.rootSubmenuKeys.indexOf(latestOpenKey) === -1) {
    state.openKeys = openKeys
  } else {
    state.openKeys = latestOpenKey ? [latestOpenKey] : []
  }
}

function onSelect({ key }) {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

watch(() => route.query.menu, (menu) => {
  state.selectedKeys = menu ? [menu.toString()] : []
}, { immediate: true })
</script>

<style scoped lang="scss">
#sidebar {
  padding: 8px;
  box-sizing: border-box;
  border-right: 1px solid $border-color;
  background-color: rgba(0, 0, 0, 0.02);
}

:deep(.ant-menu) {
  width: 100% !important;
}
</style>
