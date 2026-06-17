<template>
  <div class="page">
    <PageHeader title="系统设置" subtitle="管理 AI 模型、Prompt 模板和系统偏好" />

    <n-tabs v-model:value="tab" type="line" animated>
      <n-tab-pane name="models" tab="AI 模型配置">
        <section class="panel panel-pad">
          <div class="section-head">
            <h2>模型配置</h2>
            <n-button type="primary" @click="openModel()">新增模型</n-button>
          </div>
          <n-data-table :columns="modelColumns" :data="models" />
        </section>
      </n-tab-pane>
      <n-tab-pane name="prompts" tab="Prompt 模板管理">
        <section class="panel panel-pad">
          <div class="section-head">
            <h2>Prompt 模板</h2>
            <n-button type="primary" @click="openTemplate()">新增模板</n-button>
          </div>
          <n-data-table :columns="templateColumns" :data="templates" />
        </section>
      </n-tab-pane>
      <n-tab-pane name="preferences" tab="系统偏好">
        <section class="panel panel-pad settings-form">
          <n-form label-placement="left" label-width="160">
            <n-form-item label="默认启用脱敏">
              <n-switch v-model:value="settings.ai_desensitization_default" />
            </n-form-item>
            <n-form-item label="上传大小限制">
              <span>{{ settings.max_upload_size_mb || 50 }} MB</span>
            </n-form-item>
            <n-button type="primary" @click="saveSettings">保存设置</n-button>
          </n-form>
        </section>
      </n-tab-pane>
    </n-tabs>

    <n-drawer v-model:show="modelDrawer" :width="560" placement="right">
      <n-drawer-content :title="modelForm.id ? '编辑模型配置' : '新增模型配置'">
        <n-form :model="modelForm" label-placement="top">
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="名称"><n-input v-model:value="modelForm.name" /></n-form-item-gi>
            <n-form-item-gi label="Provider"><n-select v-model:value="modelForm.provider" :options="providerOptions" /></n-form-item-gi>
          </n-grid>
          <n-form-item label="Base URL"><n-input v-model:value="modelForm.base_url" placeholder="https://api.example.com/v1" /></n-form-item>
          <n-form-item label="API Key"><n-input v-model:value="modelForm.api_key" type="password" show-password-on="mousedown" :placeholder="modelForm.api_key_masked || '仅保存加密值，不明文展示'" /></n-form-item>
          <n-form-item label="Model Name"><n-input v-model:value="modelForm.model_name" /></n-form-item>
          <n-grid :cols="3" :x-gap="12">
            <n-form-item-gi label="Temperature"><n-input-number v-model:value="modelForm.temperature" :min="0" :max="2" :step="0.1" /></n-form-item-gi>
            <n-form-item-gi label="Max Tokens"><n-input-number v-model:value="modelForm.max_tokens" :min="1" /></n-form-item-gi>
            <n-form-item-gi label="Timeout"><n-input-number v-model:value="modelForm.timeout_seconds" :min="5" /></n-form-item-gi>
          </n-grid>
          <n-checkbox v-model:checked="modelForm.is_default">设为默认模型</n-checkbox>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="modelDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveModel">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="templateDrawer" :width="720" placement="right">
      <n-drawer-content :title="templateForm.id ? '编辑 Prompt 模板' : '新增 Prompt 模板'">
        <n-form :model="templateForm" label-placement="top">
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="模板名称"><n-input v-model:value="templateForm.name" /></n-form-item-gi>
            <n-form-item-gi label="模板编码"><n-input v-model:value="templateForm.code" /></n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="分类"><n-input v-model:value="templateForm.category" /></n-form-item-gi>
            <n-form-item-gi label="工作方向"><n-input v-model:value="templateForm.work_domain" /></n-form-item-gi>
          </n-grid>
          <n-form-item label="描述"><n-input v-model:value="templateForm.description" /></n-form-item>
          <n-form-item label="System Prompt"><n-input v-model:value="templateForm.system_prompt" type="textarea" :autosize="{ minRows: 6 }" class="mono" /></n-form-item>
          <n-form-item label="User Prompt"><n-input v-model:value="templateForm.user_prompt" type="textarea" :autosize="{ minRows: 10 }" class="mono" /></n-form-item>
          <n-alert type="info">可用变量：{{ variables.join("、") }}</n-alert>
          <n-checkbox v-model:checked="templateForm.is_default">设为默认模板</n-checkbox>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="templateDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveTemplate">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, reactive, ref } from "vue";
import { NButton, NSpace, NTag, useMessage, type DataTableColumns } from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import { aiApi, type ModelConfig, type PromptTemplate } from "@/api/resources";
import { apiGet, apiPut } from "@/api/http";

const message = useMessage();
const tab = ref("models");
const models = ref<ModelConfig[]>([]);
const templates = ref<PromptTemplate[]>([]);
const settings = reactive<any>({});
const modelDrawer = ref(false);
const templateDrawer = ref(false);
const modelForm = reactive<any>({});
const templateForm = reactive<any>({});
const variables = ["{work_logs}", "{tasks}", "{overtime_logs}", "{projects}", "{date_start}", "{date_end}", "{output_format}", "{manual_extra_content}", "{number_style}", "{group_by_category}", "{only_work_items}", "{include_overtime}", "{include_next_week_plan}"];
const providerOptions = ["openai", "anthropic", "deepseek", "qwen", "zhipu", "ollama", "openai_compatible"].map((value) => ({ label: value, value }));

const modelColumns: DataTableColumns<ModelConfig> = [
  { title: "名称", key: "name" },
  { title: "Provider", key: "provider" },
  { title: "模型", key: "model_name" },
  { title: "API Key", key: "api_key_masked" },
  { title: "默认", key: "is_default", render: (row) => (row.is_default ? h(NTag, { type: "success" }, { default: () => "默认" }) : "") },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => openModel(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", onClick: () => testModel(row) }, { default: () => "测试" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => deleteModel(row) }, { default: () => "删除" })
      ])
  }
];

const templateColumns: DataTableColumns<PromptTemplate> = [
  { title: "名称", key: "name" },
  { title: "编码", key: "code" },
  { title: "分类", key: "category" },
  { title: "工作方向", key: "work_domain" },
  { title: "默认", key: "is_default", render: (row) => (row.is_default ? h(NTag, { type: "success" }, { default: () => "默认" }) : "") },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => openTemplate(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => deleteTemplate(row) }, { default: () => "删除" })
      ])
  }
];

async function load() {
  const [modelData, templateData, settingsData] = await Promise.all([aiApi.models(), aiApi.templates(), apiGet<any>("/settings")]);
  models.value = modelData;
  templates.value = templateData;
  Object.assign(settings, settingsData);
}

function openModel(row?: ModelConfig) {
  Object.assign(modelForm, {
    id: row?.id,
    provider: row?.provider || "openai_compatible",
    name: row?.name || "",
    base_url: row?.base_url || "",
    api_key: "",
    api_key_masked: row?.api_key_masked,
    model_name: row?.model_name || "",
    temperature: row?.temperature ?? 0.2,
    max_tokens: row?.max_tokens ?? 3000,
    timeout_seconds: row?.timeout_seconds ?? 60,
    is_default: row?.is_default ?? false
  });
  modelDrawer.value = true;
}

async function saveModel() {
  if (modelForm.id) await aiApi.updateModel(modelForm.id, modelForm);
  else await aiApi.createModel(modelForm);
  message.success("模型配置已保存");
  modelDrawer.value = false;
  load();
}

async function testModel(row: ModelConfig) {
  try {
    await aiApi.testModel(row.id);
    message.success("模型连接正常");
  } catch (error: any) {
    message.error(error.response?.data?.message || "连接测试失败");
  }
}

async function deleteModel(row: ModelConfig) {
  await aiApi.deleteModel(row.id);
  message.success("已删除模型配置");
  load();
}

function openTemplate(row?: PromptTemplate) {
  Object.assign(templateForm, {
    id: row?.id,
    name: row?.name || "",
    code: row?.code || "",
    category: row?.category || "weekly",
    description: row?.description || "",
    system_prompt: row?.system_prompt || "",
    user_prompt: row?.user_prompt || "",
    output_format: row?.output_format || "markdown",
    work_domain: row?.work_domain || "security_operations",
    is_default: row?.is_default || false
  });
  templateDrawer.value = true;
}

async function saveTemplate() {
  if (templateForm.id) await aiApi.updateTemplate(templateForm.id, templateForm);
  else await aiApi.createTemplate(templateForm);
  message.success("Prompt 模板已保存");
  templateDrawer.value = false;
  load();
}

async function deleteTemplate(row: PromptTemplate) {
  await aiApi.deleteTemplate(row.id);
  message.success("已删除 Prompt 模板");
  load();
}

async function saveSettings() {
  await apiPut("/settings", { ai_desensitization_default: settings.ai_desensitization_default });
  message.success("设置已保存");
}

onMounted(load);
</script>

<style scoped>
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-head h2 {
  margin: 0;
  font-size: 16px;
}

.mono :deep(textarea) {
  font-family: "SFMono-Regular", Consolas, monospace;
}

.settings-form {
  max-width: 680px;
}
</style>
