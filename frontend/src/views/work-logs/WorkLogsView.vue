<template>
  <div class="page">
    <PageHeader title="工作记录" subtitle="快速记录每日工作内容，作为 AI 周报的数据来源">
      <n-button type="primary" @click="openCreate">新增工作记录</n-button>
    </PageHeader>

    <section class="panel panel-pad">
      <div class="toolbar">
        <n-input v-model:value="filters.keyword" clearable placeholder="搜索标题或内容" style="width: 220px" @keyup.enter="load" />
        <n-date-picker v-model:formatted-value="filters.date_start" value-format="yyyy-MM-dd" type="date" clearable placeholder="开始日期" />
        <n-date-picker v-model:formatted-value="filters.date_end" value-format="yyyy-MM-dd" type="date" clearable placeholder="结束日期" />
        <n-select v-model:value="filters.work_type" clearable placeholder="工作类型" :options="workTypeOptions" style="width: 160px" />
        <n-button @click="load">筛选</n-button>
      </div>
    </section>

    <n-tabs v-model:value="view">
      <n-tab-pane name="timeline" tab="时间线视图">
        <section class="panel panel-pad">
          <n-timeline v-if="items.length">
            <n-timeline-item v-for="item in items" :key="item.id" :time="item.work_date" :title="item.title">
              <div class="timeline-content">
                <n-space size="small">
                  <n-tag size="small">{{ labelOf(workTypeOptions, item.work_type) }}</n-tag>
                  <span>{{ item.duration_hours }}h</span>
                </n-space>
                <p>{{ item.content || item.result || "无详细内容" }}</p>
                <n-button size="tiny" @click="openEdit(item)">编辑</n-button>
              </div>
            </n-timeline-item>
          </n-timeline>
          <EmptyState v-else description="暂无工作记录">
            <n-button size="small" @click="openCreate">新增记录</n-button>
          </EmptyState>
        </section>
      </n-tab-pane>
      <n-tab-pane name="table" tab="表格视图">
        <section class="panel">
          <n-data-table :columns="columns" :data="items" :loading="loading" :pagination="pagination" remote @update:page="onPage" />
        </section>
      </n-tab-pane>
    </n-tabs>

    <n-drawer v-model:show="drawerVisible" :width="560" placement="right">
      <n-drawer-content :title="editing?.id ? '编辑工作记录' : '新增工作记录'">
        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="工作日期" path="work_date"><n-date-picker v-model:formatted-value="form.work_date" value-format="yyyy-MM-dd" type="date" /></n-form-item-gi>
            <n-form-item-gi label="工作类型"><n-select v-model:value="form.work_type" :options="workTypeOptions" /></n-form-item-gi>
          </n-grid>
          <n-form-item label="安全运营模板">
            <n-select v-model:value="selectedTemplate" clearable filterable :options="templateOptions" @update:value="applyTemplate" />
          </n-form-item>
          <n-form-item label="工作标题" path="title"><n-input v-model:value="form.title" /></n-form-item>
          <n-grid :cols="3" :x-gap="12">
            <n-form-item-gi label="开始时间"><n-time-picker v-model:formatted-value="form.start_time" value-format="HH:mm" format="HH:mm" clearable /></n-form-item-gi>
            <n-form-item-gi label="结束时间"><n-time-picker v-model:formatted-value="form.end_time" value-format="HH:mm" format="HH:mm" clearable /></n-form-item-gi>
            <n-form-item-gi label="工时"><n-input-number v-model:value="form.duration_hours" :min="0" /></n-form-item-gi>
          </n-grid>
          <n-form-item label="工作内容"><n-input v-model:value="form.content" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
          <n-form-item label="处理结果"><n-input v-model:value="form.result" type="textarea" :autosize="{ minRows: 2 }" /></n-form-item>
          <n-form-item label="问题风险"><n-input v-model:value="form.problem" type="textarea" :autosize="{ minRows: 2 }" /></n-form-item>
          <n-form-item label="后续计划"><n-input v-model:value="form.next_plan" type="textarea" :autosize="{ minRows: 2 }" /></n-form-item>
          <n-form-item v-if="editing?.id" label="附件">
            <div class="attachment-box">
              <n-input v-model:value="attachmentSummary" type="textarea" :autosize="{ minRows: 2 }" placeholder="附件摘要，可作为 AI 周报输入" />
              <n-upload :show-file-list="false" :custom-request="uploadAttachment">
                <n-button :loading="attachmentLoading">上传附件</n-button>
              </n-upload>
              <n-list v-if="attachments.length" bordered>
                <n-list-item v-for="file in attachments" :key="file.id">
                  <div class="attachment-row">
                    <div>
                      <strong>{{ file.file_name }}</strong>
                      <span>{{ formatSize(file.file_size) }}</span>
                      <p v-if="file.summary">{{ file.summary }}</p>
                    </div>
                    <n-space size="small">
                      <n-button size="tiny" tag="a" :href="attachmentApi.downloadUrl(file.id)" target="_blank">下载</n-button>
                      <n-button size="tiny" type="error" secondary @click="deleteAttachment(file)">删除</n-button>
                    </n-space>
                  </div>
                </n-list-item>
              </n-list>
              <n-text v-else depth="3">暂无附件</n-text>
            </div>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="drawerVisible = false">取消</n-button>
            <n-button :loading="saving" @click="save(true)">保存并继续</n-button>
            <n-button type="primary" :loading="saving" @click="save(false)">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import dayjs from "dayjs";
import { computed, h, onMounted, reactive, ref, watch } from "vue";
import {
  NButton,
  NSpace,
  NTag,
  useDialog,
  useMessage,
  type DataTableColumns,
  type FormInst,
  type FormRules,
  type UploadCustomRequestOptions
} from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import EmptyState from "@/components/EmptyState.vue";
import { attachmentApi, workLogApi, type Attachment, type WorkLog } from "@/api/resources";
import { labelOf, securityTemplates, workTypeOptions } from "@/utils/options";

const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const saving = ref(false);
const drawerVisible = ref(false);
const view = ref("timeline");
const formRef = ref<FormInst | null>(null);
const selectedTemplate = ref<string | null>(null);
const items = ref<WorkLog[]>([]);
const attachments = ref<Attachment[]>([]);
const attachmentSummary = ref("");
const attachmentLoading = ref(false);
const editing = ref<WorkLog | null>(null);
const total = ref(0);
const filters = reactive<any>({ keyword: "", date_start: null, date_end: null, work_type: null, page: 1, page_size: 20 });
const form = reactive<any>({});
const rules: FormRules = { work_date: { required: true, message: "请选择工作日期" }, title: { required: true, message: "请输入标题" } };

const templateOptions = securityTemplates.map((item) => ({ label: item, value: item }));
const pagination = computed(() => ({ page: filters.page, pageSize: filters.page_size, itemCount: total.value }));
const columns: DataTableColumns<WorkLog> = [
  { title: "日期", key: "work_date", width: 120 },
  { title: "标题", key: "title", minWidth: 180 },
  { title: "类型", key: "work_type", render: (row) => h(NTag, { size: "small" }, { default: () => labelOf(workTypeOptions, row.work_type) }) },
  { title: "时长", key: "duration_hours", render: (row) => `${row.duration_hours}h` },
  { title: "内容", key: "content", ellipsis: { tooltip: true } },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => openEdit(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => remove(row) }, { default: () => "删除" })
      ])
  }
];

watch(
  () => [form.start_time, form.end_time],
  () => {
    if (!form.start_time || !form.end_time) return;
    const start = dayjs(`2026-01-01 ${form.start_time}`);
    let end = dayjs(`2026-01-01 ${form.end_time}`);
    if (end.isBefore(start)) end = end.add(1, "day");
    form.duration_hours = Number((end.diff(start, "minute") / 60).toFixed(2));
  }
);

function resetForm() {
  Object.assign(form, {
    work_date: dayjs().format("YYYY-MM-DD"),
    title: "",
    content: "",
    work_type: "security",
    start_time: null,
    end_time: null,
    duration_hours: 0,
    result: "",
    problem: "",
    next_plan: "",
    visibility: "private"
  });
}

async function load() {
  loading.value = true;
  try {
    const data = await workLogApi.list(filters);
    items.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function onPage(page: number) {
  filters.page = page;
  load();
}

function openCreate() {
  editing.value = null;
  selectedTemplate.value = null;
  attachments.value = [];
  attachmentSummary.value = "";
  resetForm();
  drawerVisible.value = true;
}

async function openEdit(row: WorkLog) {
  editing.value = row;
  selectedTemplate.value = null;
  attachmentSummary.value = "";
  Object.assign(form, row);
  drawerVisible.value = true;
  await loadAttachments(row.id);
}

function applyTemplate(value: string | null) {
  if (!value) return;
  form.title = value;
  form.work_type = value.includes("告警") || value.includes("应急") || value.includes("重保") ? "security" : "operation";
  form.content = value;
}

async function save(continueAdd: boolean) {
  await formRef.value?.validate();
  saving.value = true;
  try {
    if (editing.value?.id) await workLogApi.update(editing.value.id, form);
    else await workLogApi.create(form);
    message.success("工作记录已保存");
    await load();
    if (continueAdd) resetForm();
    else drawerVisible.value = false;
  } finally {
    saving.value = false;
  }
}

async function loadAttachments(logId: number) {
  attachmentLoading.value = true;
  try {
    attachments.value = await attachmentApi.list("work_log", logId);
  } finally {
    attachmentLoading.value = false;
  }
}

async function uploadAttachment(options: UploadCustomRequestOptions) {
  const rawFile = options.file.file;
  if (!editing.value?.id || !rawFile) {
    options.onError();
    return;
  }
  attachmentLoading.value = true;
  try {
    await attachmentApi.upload("work_log", editing.value.id, rawFile, attachmentSummary.value);
    attachmentSummary.value = "";
    await loadAttachments(editing.value.id);
    message.success("附件已上传");
    options.onFinish();
  } catch (error) {
    options.onError();
  } finally {
    attachmentLoading.value = false;
  }
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

async function deleteAttachment(file: Attachment) {
  await attachmentApi.remove(file.id);
  message.success("附件已删除");
  if (editing.value?.id) await loadAttachments(editing.value.id);
}

function remove(row: WorkLog) {
  dialog.warning({
    title: "删除工作记录",
    content: `确认删除「${row.title}」？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await workLogApi.remove(row.id);
      message.success("已删除");
      load();
    }
  });
}

onMounted(() => {
  resetForm();
  load();
});
</script>

<style scoped>
.timeline-content p {
  margin: 8px 0;
  color: #334155;
}

.attachment-box {
  display: grid;
  width: 100%;
  gap: 10px;
}

.attachment-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.attachment-row strong,
.attachment-row span {
  display: block;
}

.attachment-row span,
.attachment-row p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}
</style>
