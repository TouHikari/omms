<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getRecordTemplates, createRecordTemplate, updateRecordTemplate, deleteRecordTemplate, getRecordDictionaries, getRecordDictionaryImaging, getRecordDictionaryLabs } from '@/api/record'

const route = useRoute()
const router = useRouter()

const templates = ref([])
const loading = ref(false)
const imagingOpts = ref([])
const labOpts = ref([])
const currentMenu = computed(() => route.query.menu ? route.query.menu.toString() : 'templates_list')
const isCreateView = computed(() => currentMenu.value === 'templates_create')
const previewVisible = ref(false)
const previewItem = ref(null)

function setMenu(key) {
  router.replace({ path: route.path, query: { ...route.query, menu: key } })
}

async function loadTemplates() {
  loading.value = true
  try {
    const res = await getRecordTemplates()
    if (res.code === 200) templates.value = res.data
    const dict = await getRecordDictionaries()
    if (dict.code === 200) {
      const imgs = (dict.data.imaging || []).map(v => ({ label: String(v), value: String(v) }))
      const labs = (dict.data.labs || []).map(v => ({ label: String(v), value: String(v) }))
      imagingOpts.value = imgs
      labOpts.value = labs
    }
    if (!imagingOpts.value.length) {
      const r = await getRecordDictionaryImaging()
      if (r.code === 200) imagingOpts.value = (r.data || []).map(v => ({ label: String(v), value: String(v) }))
    }
    if (!labOpts.value.length) {
      const r = await getRecordDictionaryLabs()
      if (r.code === 200) labOpts.value = (r.data || []).map(v => ({ label: String(v), value: String(v) }))
    }
  } catch {
    imagingOpts.value = []
    labOpts.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => loadTemplates())

function openPreview(tpl) {
  previewItem.value = tpl
  previewVisible.value = true
}

const editVisible = ref(false)
const editForm = ref({ id: null, name: '', scope: '通用', fields: [], defaults: { chiefComplaint: '', diagnosis: '', prescriptions: [], labs: [], imaging: [] } })

function openEdit(tpl) {
  editForm.value = { id: tpl.id, name: tpl.name, scope: tpl.scope, fields: [...tpl.fields], defaults: {
    chiefComplaint: tpl.defaults?.chiefComplaint || '',
    diagnosis: tpl.defaults?.diagnosis || '',
    prescriptions: Array.isArray(tpl.defaults?.prescriptions) ? [...tpl.defaults.prescriptions] : [],
    labs: Array.isArray(tpl.defaults?.labs) ? [...tpl.defaults.labs] : [],
    imaging: Array.isArray(tpl.defaults?.imaging) ? [...tpl.defaults.imaging] : [],
  } }
  editVisible.value = true
}

function addField(input) {
  const v = (input || '').trim()
  if (!v) return
  if (!editForm.value.fields.includes(v)) editForm.value.fields.push(v)
}

function removeField(idx) {
  editForm.value.fields.splice(idx, 1)
}

async function submitEdit() {
  const res = await updateRecordTemplate(editForm.value.id, { name: editForm.value.name, scope: editForm.value.scope, fields: editForm.value.fields, defaults: editForm.value.defaults })
  if (res.code === 200) {
    message.success('模板更新成功')
    editVisible.value = false
    const idx = templates.value.findIndex(t => t.id === res.data.id)
    if (idx !== -1) templates.value[idx] = res.data
  } else {
    message.error(res.message || '更新失败')
  }
}

async function removeTemplate(id) {
  const res = await deleteRecordTemplate(id)
  if (res.code === 200) {
    message.success('模板删除成功')
    templates.value = templates.value.filter(t => t.id !== id)
  } else {
    message.error(res.message || '删除失败')
  }
}

const createForm = ref({ name: '', scope: '通用', fields: [], defaults: { chiefComplaint: '', diagnosis: '', prescriptions: [], labs: [], imaging: [] } })

function addCreateField(input) {
  const v = (input || '').trim()
  if (!v) return
  if (!createForm.value.fields.includes(v)) createForm.value.fields.push(v)
}

function removeCreateField(idx) {
  createForm.value.fields.splice(idx, 1)
}

async function submitCreate() {
  if (!createForm.value.name.trim()) {
    message.warning('请输入模板名称')
    return
  }
  const res = await createRecordTemplate({ name: createForm.value.name, scope: createForm.value.scope, fields: createForm.value.fields, defaults: createForm.value.defaults })
  if (res.code === 200) {
    message.success('模板创建成功')
    templates.value.unshift(res.data)
    createForm.value = { name: '', scope: '通用', fields: [], defaults: { chiefComplaint: '', diagnosis: '', prescriptions: [], labs: [], imaging: [] } }
    setMenu('templates_list')
  } else {
    message.error(res.message || '创建失败')
  }
}

</script>

<template>
  <div>
    <div v-if="!isCreateView">
      <a-card :bordered="false" title="模板列表" :loading="loading">
        <template #extra>
          <a-button type="primary" @click="setMenu('templates_create')">新建模板</a-button>
        </template>
        <a-list :data-source="templates">
          <template #renderItem="{ item }">
            <a-list-item class="tpl-item">
              <a-list-item-meta :title="item.name" :description="`范围：${item.scope}`" class="tpl-meta" />
              <div class="tpl-fields">
                <a-tag v-for="f in item.fields" :key="f">{{ f }}</a-tag>
              </div>
              <template #actions>
                <a-button type="link" @click="openPreview(item)">预览</a-button>
                <a-button type="link" @click="openEdit(item)">编辑</a-button>
                <a-popconfirm title="确认删除该模板？" ok-text="删除" cancel-text="取消" @confirm="removeTemplate(item.id)">
                  <a-button type="link" danger>删除</a-button>
                </a-popconfirm>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-card>

      <a-modal v-model:open="editVisible" title="编辑模板" @ok="submitEdit">
        <a-form layout="vertical">
          <a-form-item label="模板名称">
            <a-input v-model:value="editForm.name" placeholder="输入模板名称" />
          </a-form-item>
          <a-form-item label="适用范围">
            <a-select v-model:value="editForm.scope" :options="[{ label: '通用', value: '通用' }, { label: '科室', value: '科室' }]" />
          </a-form-item>
          <a-form-item label="模板字段">
            <a-input-search placeholder="输入字段名称后回车加入" @search="addField" />
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap">
              <a-tag v-for="(f, idx) in editForm.fields" :key="f" closable @close.prevent="removeField(idx)">{{ f }}</a-tag>
            </div>
          </a-form-item>
          <a-divider />
          <a-form-item label="默认主诉">
            <a-textarea v-model:value="editForm.defaults.chiefComplaint" :rows="3" placeholder="例如：发热伴咳嗽3天" />
          </a-form-item>
          <a-form-item label="默认诊断">
            <a-textarea v-model:value="editForm.defaults.diagnosis" :rows="3" placeholder="例如：上呼吸道感染" />
          </a-form-item>
          <a-form-item label="默认处方">
            <a-input-search placeholder="输入药品名称后回车加入" @search="v => { const t=(v||'').trim(); if(t && !editForm.defaults.prescriptions.includes(t)) editForm.defaults.prescriptions.push(t) }" />
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap">
              <a-tag v-for="(p, idx) in editForm.defaults.prescriptions" :key="p" closable @close.prevent="editForm.defaults.prescriptions.splice(idx, 1)" color="blue">{{ p }}</a-tag>
            </div>
          </a-form-item>
          <a-form-item label="默认检查申请">
            <a-checkbox-group v-model:value="editForm.defaults.imaging" :options="imagingOpts" />
          </a-form-item>
          <a-form-item label="默认检验申请">
            <a-checkbox-group v-model:value="editForm.defaults.labs" :options="labOpts" />
          </a-form-item>
        </a-form>
      </a-modal>
      <a-modal v-model:open="previewVisible" title="模板预览" :footer="null" width="720px">
        <a-descriptions bordered :column="1">
          <a-descriptions-item label="名称">{{ previewItem?.name }}</a-descriptions-item>
          <a-descriptions-item label="范围">{{ previewItem?.scope }}</a-descriptions-item>
          <a-descriptions-item label="字段">
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <a-tag v-for="f in previewItem?.fields || []" :key="f">{{ f }}</a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="默认主诉">{{ previewItem?.defaults?.chiefComplaint || '—' }}</a-descriptions-item>
          <a-descriptions-item label="默认诊断">{{ previewItem?.defaults?.diagnosis || '—' }}</a-descriptions-item>
          <a-descriptions-item label="默认处方">
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <a-tag v-for="p in previewItem?.defaults?.prescriptions || []" :key="p" color="blue">{{ p }}</a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="默认检查">
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <a-tag v-for="i in previewItem?.defaults?.imaging || []" :key="i">{{ i }}</a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="默认检验">
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <a-tag v-for="l in previewItem?.defaults?.labs || []" :key="l">{{ l }}</a-tag>
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </a-modal>
    </div>

    <div v-else>
      <a-card :bordered="false" title="新建模板">
        <a-form layout="vertical">
          <a-form-item label="模板名称">
            <a-input v-model:value="createForm.name" placeholder="输入模板名称" />
          </a-form-item>
          <a-form-item label="适用范围">
            <a-select v-model:value="createForm.scope" :options="[{ label: '通用', value: '通用' }, { label: '科室', value: '科室' }]" />
          </a-form-item>
          <a-form-item label="模板字段">
            <a-input-search placeholder="输入字段名称后回车加入" @search="addCreateField" />
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap">
              <a-tag v-for="(f, idx) in createForm.fields" :key="f" closable @close.prevent="removeCreateField(idx)">{{ f }}</a-tag>
            </div>
          </a-form-item>
          <a-divider />
          <a-form-item label="默认主诉">
            <a-textarea v-model:value="createForm.defaults.chiefComplaint" :rows="3" placeholder="例如：发热伴咳嗽3天" />
          </a-form-item>
          <a-form-item label="默认诊断">
            <a-textarea v-model:value="createForm.defaults.diagnosis" :rows="3" placeholder="例如：上呼吸道感染" />
          </a-form-item>
          <a-form-item label="默认处方">
            <a-input-search placeholder="输入药品名称后回车加入" @search="v => { const t=(v||'').trim(); if(t && !createForm.defaults.prescriptions.includes(t)) createForm.defaults.prescriptions.push(t) }" />
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap">
              <a-tag v-for="(p, idx) in createForm.defaults.prescriptions" :key="p" closable @close.prevent="createForm.defaults.prescriptions.splice(idx, 1)" color="blue">{{ p }}</a-tag>
            </div>
          </a-form-item>
          <a-form-item label="默认检查申请">
            <a-checkbox-group v-model:value="createForm.defaults.imaging" :options="imagingOpts" />
          </a-form-item>
          <a-form-item label="默认检验申请">
            <a-checkbox-group v-model:value="createForm.defaults.labs" :options="labOpts" />
          </a-form-item>
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="submitCreate">创建模板</a-button>
              <a-button @click="setMenu('templates_list')">返回列表</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/_variables.scss' as *;

.tpl-meta {
  min-width: 150px;
}

.tpl-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 200px;
}

:deep(.tpl-item) {
  display: flex;
  flex-wrap: wrap;
}

:deep(.ant-list-item) {
  align-items: flex-start;
}

:deep(.ant-list-item-meta) {
  flex: 1 1 auto;
}

:deep(.ant-list-item-action) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@container (max-width: $breakpoint-sm) {
  :deep(.ant-list-item-action) {
    width: 100%;
    justify-content: flex-start;
    margin-top: 8px;
  }
}

@container (max-width: $breakpoint-md) {
  :deep(.tpl-item) {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  :deep(.tpl-item .ant-list-item-meta) {
    width: 100%;
    flex: 0 0 100%;
  }
  .tpl-fields {
    width: 100%;
  }
  :deep(.tpl-item .ant-list-item-action) {
    width: 100%;
    flex: 0 0 100%;
  }
}
</style>
