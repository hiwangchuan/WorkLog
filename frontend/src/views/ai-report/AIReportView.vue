<template>
  <div class="page ai-page">
    <PageHeader title="AI 周报生成" subtitle="从工作记录、任务、加班和项目数据生成可编辑周报">
      <n-button @click="loadOptions">刷新配置</n-button>
    </PageHeader>

    <div class="ai-layout">
      <section class="panel panel-pad config-panel">
        <h2>生成配置</h2>
        <n-form :model="form" label-placement="top">
          <n-form-item label="时间范围">
            <n-date-picker v-model:formatted-value="dateRange" value-format="yyyy-MM-dd" type="daterange" clearable />
          </n-form-item>
          <n-form-item label="数据来源">
            <n-checkbox-group v-model:value="form.sources">
              <n-space vertical>
                <n-checkbox value="work_logs">工作记录</n-checkbox>
                <n-checkbox value="tasks">任务记录</n-checkbox>
                <n-checkbox value="overtime_logs">加班记录</n-checkbox>
                <n-checkbox value="projects">项目记录</n-checkbox>
              </n-space>
            </n-checkbox-group>
          </n-form-item>
          <n-form-item label="Prompt 模板">
            <n-select v-model:value="form.template_id" clearable :options="templateOptions" />
          </n-form-item>
          <n-form-item label="AI 模型">
            <n-select v-model:value="form.model_config_id" clearable :options="modelOptions" placeholder="不选则使用本地规则生成" />
          </n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="输出格式"><n-select v-model:value="form.output_format" :options="formatOptions" /></n-form-item-gi>
            <n-form-item-gi label="编号方式"><n-select v-model:value="form.number_style" :options="numberOptions" /></n-form-item-gi>
          </n-grid>
          <n-space vertical>
            <n-checkbox v-model:checked="form.group_by_category">按安全运营分类输出</n-checkbox>
            <n-checkbox v-model:checked="form.only_work_items">只写干了什么</n-checkbox>
            <n-checkbox v-model:checked="form.include_overtime">包含加班情况</n-checkbox>
            <n-checkbox v-model:checked="form.include_next_week_plan">包含下周计划</n-checkbox>
            <n-checkbox v-model:checked="form.enable_desensitization">启用敏感信息脱敏</n-checkbox>
          </n-space>
          <n-form-item label="手动补充内容">
            <n-input v-model:value="form.manual_extra_content" type="textarea" :autosize="{ minRows: 4 }" />
          </n-form-item>
          <n-button type="primary" block size="large" :loading="generating" @click="generate">生成周报</n-button>
        </n-form>

        <n-steps v-if="generating || activeStep > 0" class="steps" vertical :current="activeStep" status="process">
          <n-step v-for="step in steps" :key="step" :title="step" />
        </n-steps>
      </section>

      <section class="panel panel-pad result-panel">
        <div class="result-head">
          <div>
            <h2>生成结果</h2>
            <span class="muted">{{ currentRecord ? `${currentRecord.date_start} 至 ${currentRecord.date_end}` : "等待生成" }}</span>
          </div>
          <n-space>
            <n-button :disabled="!result" @click="copyResult">复制</n-button>
            <n-button :disabled="!currentRecord" :loading="saving" @click="saveFinal">保存</n-button>
            <n-dropdown :options="exportOptions" :disabled="!currentRecord" @select="exportReport">
              <n-button :disabled="!currentRecord">导出</n-button>
            </n-dropdown>
          </n-space>
        </div>

        <n-alert v-if="errorText" type="error" closable @close="errorText = ''">{{ errorText }}</n-alert>

        <n-tabs v-model:value="activeTab">
          <n-tab-pane name="result" tab="AI 生成结果">
            <textarea v-model="result" class="editor" placeholder="生成结果会显示在这里，可直接编辑最终版本"></textarea>
          </n-tab-pane>
          <n-tab-pane name="input" tab="输入数据预览">
            <pre class="preview">{{ JSON.stringify(currentRecord?.input_snapshot || {}, null, 2) }}</pre>
          </n-tab-pane>
          <n-tab-pane name="prompt" tab="实际 Prompt">
            <pre class="preview">{{ currentRecord?.prompt_content || "暂无 Prompt" }}</pre>
          </n-tab-pane>
          <n-tab-pane name="history" tab="历史记录">
            <n-data-table :columns="historyColumns" :data="history" :loading="historyLoading" />
          </n-tab-pane>
        </n-tabs>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from "dayjs";
import { h, onMounted, reactive, ref } from "vue";
import { NButton, NSpace, NTag, useMessage, type DataTableColumns } from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import { aiApi, downloadExport, type GenerationRecord, type ModelConfig, type PromptTemplate } from "@/api/resources";

const message = useMessage();
const templates = ref<PromptTemplate[]>([]);
const models = ref<ModelConfig[]>([]);
const history = ref<GenerationRecord[]>([]);
const currentRecord = ref<GenerationRecord | null>(null);
const result = ref("");
const activeTab = ref("result");
const historyLoading = ref(false);
const generating = ref(false);
const saving = ref(false);
const errorText = ref("");
const activeStep = ref(0);
const dateRange = ref<[string, string]>([dayjs().startOf("week").format("YYYY-MM-DD"), dayjs().endOf("week").format("YYYY-MM-DD")]);
const form = reactive<any>({
  sources: ["work_logs", "tasks", "overtime_logs", "projects"],
  template_id: null,
  model_config_id: null,
  output_format: "markdown",
  number_style: "chinese_comma",
  group_by_category: true,
  only_work_items: true,
  include_overtime: false,
  include_next_week_plan: false,
  enable_desensitization: true,
  manual_extra_content: ""
});

const steps = ["正在整理工作记录...", "正在合并重复事项...", "正在进行敏感信息脱敏...", "正在调用 AI 模型...", "正在生成周报内容...", "正在进行格式校验..."];
const formatOptions = [
  { label: "Markdown", value: "markdown" },
  { label: "纯文本", value: "text" },
  { label: "JSON", value: "json" }
];
const numberOptions = [
  { label: "1、2、3、4", value: "chinese_comma" },
  { label: "1. 2. 3. 4.", value: "dot" },
  { label: "- 无序列表", value: "markdown_dash" }
];
const exportOptions = [
  { label: "Markdown", key: "markdown" },
  { label: "Excel", key: "excel" },
  { label: "Word", key: "word" },
  { label: "PDF", key: "pdf" }
];
const templateOptions = ref<{ label: string; value: number }[]>([]);
const modelOptions = ref<{ label: string; value: number }[]>([]);

const historyColumns: DataTableColumns<GenerationRecord> = [
  { title: "类型", key: "report_type", render: (row) => h(NTag, { size: "small" }, { default: () => row.report_type }) },
  { title: "时间范围", key: "range", render: (row) => `${row.date_start} 至 ${row.date_end}` },
  { title: "状态", key: "status" },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => selectHistory(row) }, { default: () => "查看" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => deleteHistory(row) }, { default: () => "删除" })
      ])
  }
];

async function loadOptions() {
  const [templateData, modelData] = await Promise.all([aiApi.templates(), aiApi.models()]);
  templates.value = templateData;
  models.value = modelData;
  templateOptions.value = templateData.map((item) => ({ label: item.is_default ? `${item.name}（默认）` : item.name, value: item.id }));
  modelOptions.value = modelData.map((item) => ({ label: item.is_default ? `${item.name}（默认）` : item.name, value: item.id }));
  if (!form.template_id) form.template_id = templateData.find((item) => item.is_default)?.id || templateData[0]?.id || null;
  if (!form.model_config_id) form.model_config_id = modelData.find((item) => item.is_default)?.id || null;
}

async function loadHistory() {
  historyLoading.value = true;
  try {
    history.value = (await aiApi.records({ report_type: "weekly", page_size: 20 })).items;
  } finally {
    historyLoading.value = false;
  }
}

async function generate() {
  if (!dateRange.value?.[0] || !dateRange.value?.[1]) {
    message.warning("请选择时间范围");
    return;
  }
  generating.value = true;
  errorText.value = "";
  activeStep.value = 1;
  const timer = window.setInterval(() => {
    activeStep.value = Math.min(activeStep.value + 1, steps.length);
  }, 550);
  try {
    const record = await aiApi.generateWeekly({
      ...form,
      date_start: dateRange.value[0],
      date_end: dateRange.value[1]
    });
    currentRecord.value = record;
    result.value = record.final_output || record.ai_output || "";
    activeTab.value = "result";
    if (record.status === "failed") errorText.value = record.error_message || "AI 生成失败";
    else message.success("周报已生成");
    loadHistory();
  } catch (error: any) {
    errorText.value = error.response?.data?.message || "AI 生成失败：模型连接超时，请检查 API Key、Base URL 或网络配置。";
  } finally {
    window.clearInterval(timer);
    activeStep.value = steps.length;
    generating.value = false;
  }
}

async function copyResult() {
  await navigator.clipboard.writeText(result.value);
  message.success("已复制周报内容");
}

async function saveFinal() {
  if (!currentRecord.value) return;
  saving.value = true;
  try {
    currentRecord.value = await aiApi.updateFinal(currentRecord.value.id, result.value);
    message.success("最终版本已保存");
    loadHistory();
  } finally {
    saving.value = false;
  }
}

function selectHistory(row: GenerationRecord) {
  currentRecord.value = row;
  result.value = row.final_output || row.ai_output || "";
  activeTab.value = "result";
}

async function deleteHistory(row: GenerationRecord) {
  await aiApi.deleteRecord(row.id);
  if (currentRecord.value?.id === row.id) {
    currentRecord.value = null;
    result.value = "";
  }
  message.success("历史记录已删除");
  loadHistory();
}

async function exportReport(format: string) {
  if (!currentRecord.value) return;
  await downloadExport(currentRecord.value.id, format);
}

onMounted(() => {
  loadOptions();
  loadHistory();
});
</script>

<style scoped>
.ai-layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
}

.config-panel h2,
.result-head h2 {
  margin: 0;
  font-size: 16px;
}

.steps {
  margin-top: 18px;
}

.result-panel {
  min-width: 0;
}

.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.preview {
  overflow: auto;
  min-height: 360px;
  max-height: 620px;
  padding: 14px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  white-space: pre-wrap;
}

@media (max-width: 1100px) {
  .ai-layout {
    grid-template-columns: 1fr;
  }
}
</style>
