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
}, { immediate: true })

function syncOpen() {
  const selected = route.query.menu ? route.query.menu.toString() : ''
  state.selectedKeys = selected ? [selected] : []
  const parent = items.value.find(g => (g.children || []).some(c => c.key === selected))
  const validGroupKeys = items.value.map(g => g.key)
  const current = (state.openKeys || []).filter(k => validGroupKeys.includes(k))
  if (parent && !current.includes(parent.key)) current.push(parent.key)
  state.openKeys = current
}

const onOpenChange = openKeys => {
  state.openKeys = openKeys
}

function onSelect({ key }) {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

watch(() => route.query.menu, () => syncOpen(), { immediate: true })
watch(() => route.path, () => syncOpen())
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
