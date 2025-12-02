<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, required: true },
  desc: { type: String, default: '' },
  panels: { type: Array, required: true },
  accordion: { type: Boolean, default: true },
  menuSync: { type: Boolean, default: true },
  menuMap: { type: Object, default: () => ({}) },
})

const route = useRoute()
const router = useRouter()
const activeKey = ref('')

function computeActiveFromRoute() {
  const menu = route.query.menu ? route.query.menu.toString() : ''
  if (menu === 'none') {
    return props.accordion ? '' : []
  }
  if (!menu) return props.panels?.[0]?.key || ''
  const inverse = Object.entries(props.menuMap || {}).reduce((acc, [k, v]) => { acc[v] = k; return acc }, {})
  const byMap = inverse[menu]
  if (byMap) return byMap
  const group = menu.split('_')[0]
  const panelKeys = (props.panels || []).map(p => p.key)
  if (panelKeys.includes(group)) return group
  return props.panels?.[0]?.key || ''
}

function syncActive() {
  activeKey.value = computeActiveFromRoute()
}

watch(() => route.query.menu, () => props.menuSync && syncActive(), { immediate: true })
watch(() => route.path, () => props.menuSync && syncActive())

function onChange(key) {
  const isArray = Array.isArray(key)
  const k = isArray ? key[0] : key
  activeKey.value = isArray ? key : (k ?? '')
  if (!props.menuSync) return
  if (isArray ? (key.length === 0) : (k === undefined || k === null || k === '')) {
    router.replace({ path: route.path, query: { ...route.query, menu: 'none' } })
    return
  }
  const menuKey = props.menuMap?.[k] || k
  router.replace({ path: route.path, query: { ...route.query, menu: menuKey } })
}
</script>

<template>
  <section class="page-layout">
    <a-page-header :title="title" :sub-title="desc">
      <template #extra>
        <slot name="header-extra" />
      </template>
    </a-page-header>

    <section class="metrics">
      <slot name="metrics" />
    </section>

    <section class="content">
      <a-collapse v-model:activeKey="activeKey" :accordion="accordion" @change="onChange">
        <a-collapse-panel v-for="p in panels" :key="p.key" :header="p.header">
          <slot :name="'panel-' + p.key" />
        </a-collapse-panel>
      </a-collapse>
    </section>
  </section>

</template>

<style scoped lang="scss">
.page-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metrics {
  margin-top: 8px;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
