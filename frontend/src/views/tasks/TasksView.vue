<template>
  <div class="page">
    <PageHeader title="任务管理" subtitle="列表、看板和日历视图统一管理个人任务">
      <n-button type="primary" @click="openCreate">新建任务</n-button>
    </PageHeader>

    <section class="panel panel-pad">
      <div class="toolbar">
        <n-input v-model:value="filters.keyword" clearable placeholder="搜索任务" style="width: 220px" @keyup.enter="load" />
        <n-select v-model:value="filters.status" clearable placeholder="状态" :options="taskStatusOptions" style="width: 150px" />
        <n-select v-model:value="filters.priority" clearable placeholder="优先级" :options="priorityOptions" style="width: 150px" />
        <n-button @click="load">筛选</n-button>
      </div>
    </section>

    <n-tabs v-model:value="view">
      <n-tab-pane name="list" tab="列表视图">
        <section class="panel">
          <n-data-table :columns="columns" :data="items" :loading="loading" :pagination="pagination" remote @update:page="onPage" />
        </section>
      </n-tab-pane>
      <n-tab-pane name="kanban" tab="看板视图">
        <div class="kanban">
          <div v-for="status in taskStatusOptions" :key="status.value" class="panel kanban-col">
            <div class="kanban-head">
              <strong>{{ status.label }}</strong>
              <n-tag size="small">{{ grouped[status.value]?.length || 0 }}</n-tag>
            </div>
            <div v-for="task in grouped[status.value]" :key="task.id" class="task-card">
              <div class="task-title">{{ task.title }}</div>
              <n-space size="small">
                <n-tag size="small" :type="tagType(priorityOptions, task.priority) as any">{{ labelOf(priorityOptions, task.priority) }}</n-tag>
                <span class="muted">{{ task.actual_hours }}h / {{ task.estimated_hours }}h</span>
              </n-space>
            </div>
          </div>
        </div>
      </n-tab-pane>
      <n-tab-pane name="calendar" tab="日历视图">
        <section class="panel panel-pad">
          <n-calendar>
            <template #default="{ year, month, date }">
              <div v-for="task in byDate(`${year}-${String(month).padStart(2, '0')}-${String(date).padStart(2, '0')}`)" :key="task.id" class="calendar-task">
                {{ task.title }}
              </div>
            </template>
          </n-calendar>
        </section>
      </n-tab-pane>
      <n-tab-pane name="gantt" tab="甘特图预留">
        <section class="panel panel-pad">
          <EmptyState description="甘特图能力已预留，将在后续阶段增强" />
        </section>
      </n-tab-pane>
    </n-tabs>

    <n-drawer v-model:show="drawerVisible" :width="520" placement="right">
      <n-drawer-content :title="editing?.id ? '编辑任务' : '新建任务'">
        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-form-item label="任务标题" path="title"><n-input v-model:value="form.title" /></n-form-item>
          <n-form-item label="任务描述"><n-input v-model:value="form.description" type="textarea" /></n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="状态"><n-select v-model:value="form.status" :options="taskStatusOptions" /></n-form-item-gi>
            <n-form-item-gi label="优先级"><n-select v-model:value="form.priority" :options="priorityOptions" /></n-form-item-gi>
          </n-grid>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="截止日期"><n-date-picker v-model:formatted-value="form.due_date" value-format="yyyy-MM-dd" type="date" clearable /></n-form-item-gi>
            <n-form-item-gi label="预计工时"><n-input-number v-model:value="form.estimated_hours" :min="0" /></n-form-item-gi>
          </n-grid>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="drawerVisible = false">取消</n-button>
            <n-button type="primary" :loading="saving" @click="save">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from "vue";
import { NButton, NSpace, NTag, useDialog, useMessage, type DataTableColumns, type FormInst, type FormRules } from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import EmptyState from "@/components/EmptyState.vue";
import { taskApi, type Task } from "@/api/resources";
import { labelOf, priorityOptions, tagType, taskStatusOptions } from "@/utils/options";

const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const saving = ref(false);
const drawerVisible = ref(false);
const view = ref("list");
const formRef = ref<FormInst | null>(null);
const items = ref<Task[]>([]);
const editing = ref<Task | null>(null);
const filters = reactive({ keyword: "", status: null as string | null, priority: null as string | null, page: 1, page_size: 20 });
const form = reactive<any>({ title: "", description: "", status: "todo", priority: "medium", due_date: null, estimated_hours: 0 });
const rules: FormRules = { title: { required: true, message: "请输入任务标题" } };
const total = ref(0);

const pagination = computed(() => ({ page: filters.page, pageSize: filters.page_size, itemCount: total.value }));
const grouped = computed(() =>
  items.value.reduce<Record<string, Task[]>>((acc, item) => {
    acc[item.status] ||= [];
    acc[item.status].push(item);
    return acc;
  }, {})
);
const columns: DataTableColumns<Task> = [
  { title: "任务", key: "title", minWidth: 180 },
  { title: "状态", key: "status", render: (row) => h(NTag, { type: tagType(taskStatusOptions, row.status) as any }, { default: () => labelOf(taskStatusOptions, row.status) }) },
  { title: "优先级", key: "priority", render: (row) => h(NTag, { type: tagType(priorityOptions, row.priority) as any }, { default: () => labelOf(priorityOptions, row.priority) }) },
  { title: "截止", key: "due_date" },
  { title: "工时", key: "hours", render: (row) => `${row.actual_hours} / ${row.estimated_hours}h` },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => openEdit(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", type: "success", secondary: true, onClick: () => finish(row) }, { default: () => "完成" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => remove(row) }, { default: () => "删除" })
      ])
  }
];

async function load() {
  loading.value = true;
  try {
    const data = await taskApi.list(filters);
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

function resetForm() {
  Object.assign(form, { title: "", description: "", status: "todo", priority: "medium", due_date: null, estimated_hours: 0 });
}

function openCreate() {
  editing.value = null;
  resetForm();
  drawerVisible.value = true;
}

function openEdit(row: Task) {
  editing.value = row;
  Object.assign(form, row);
  drawerVisible.value = true;
}

async function save() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    if (editing.value?.id) await taskApi.update(editing.value.id, form);
    else await taskApi.create(form);
    message.success("任务已保存");
    drawerVisible.value = false;
    load();
  } finally {
    saving.value = false;
  }
}

async function finish(row: Task) {
  await taskApi.status(row.id, "completed");
  message.success("任务已标记完成");
  load();
}

function remove(row: Task) {
  dialog.warning({
    title: "删除任务",
    content: `确认删除「${row.title}」？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await taskApi.remove(row.id);
      message.success("已删除");
      load();
    }
  });
}

function byDate(date: string) {
  return items.value.filter((item) => item.due_date === date).slice(0, 3);
}

onMounted(load);
</script>

<style scoped>
.kanban {
  display: grid;
  grid-template-columns: repeat(5, minmax(180px, 1fr));
  gap: 14px;
  overflow-x: auto;
}

.kanban-col {
  min-height: 420px;
  padding: 12px;
}

.kanban-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.task-card {
  padding: 12px;
  margin-bottom: 10px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.task-title {
  margin-bottom: 8px;
  font-weight: 700;
}

.calendar-task {
  overflow: hidden;
  margin-top: 4px;
  padding: 2px 6px;
  color: #1d4ed8;
  background: #eff6ff;
  border-radius: 6px;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
