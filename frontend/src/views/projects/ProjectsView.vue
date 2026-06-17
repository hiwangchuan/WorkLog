<template>
  <div class="page">
    <PageHeader title="项目管理" subtitle="按项目归集任务、工作记录和工时">
      <n-button type="primary" @click="openCreate">创建项目</n-button>
    </PageHeader>

    <section class="panel panel-pad">
      <div class="toolbar">
        <n-input v-model:value="filters.keyword" clearable placeholder="搜索项目" style="width: 220px" @keyup.enter="load" />
        <n-select v-model:value="filters.status" clearable placeholder="项目状态" :options="statusOptions" style="width: 160px" />
        <n-button @click="load">筛选</n-button>
      </div>
    </section>

    <section class="panel">
      <n-data-table :columns="columns" :data="items" :loading="loading" :pagination="pagination" remote @update:page="onPage" />
    </section>

    <n-drawer v-model:show="drawerVisible" :width="520" placement="right">
      <n-drawer-content :title="editing?.id ? '编辑项目' : '创建项目'">
        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-form-item label="项目名称" path="name"><n-input v-model:value="form.name" /></n-form-item>
          <n-form-item label="项目描述"><n-input v-model:value="form.description" type="textarea" /></n-form-item>
          <n-form-item label="项目状态"><n-select v-model:value="form.status" :options="statusOptions" /></n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="开始日期"><n-date-picker v-model:formatted-value="form.start_date" value-format="yyyy-MM-dd" type="date" clearable /></n-form-item-gi>
            <n-form-item-gi label="结束日期"><n-date-picker v-model:formatted-value="form.end_date" value-format="yyyy-MM-dd" type="date" clearable /></n-form-item-gi>
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
import { projectApi, type Project } from "@/api/resources";
import { labelOf } from "@/utils/options";

const statusOptions = [
  { label: "进行中", value: "active" },
  { label: "已完成", value: "completed" },
  { label: "暂停", value: "paused" },
  { label: "已取消", value: "cancelled" }
];
const message = useMessage();
const dialog = useDialog();
const formRef = ref<FormInst | null>(null);
const items = ref<Project[]>([]);
const total = ref(0);
const loading = ref(false);
const saving = ref(false);
const drawerVisible = ref(false);
const editing = ref<Project | null>(null);
const filters = reactive<any>({ keyword: "", status: null, page: 1, page_size: 20 });
const form = reactive<any>({});
const rules: FormRules = { name: { required: true, message: "请输入项目名称" } };
const pagination = computed(() => ({ page: filters.page, pageSize: filters.page_size, itemCount: total.value }));
const columns: DataTableColumns<Project> = [
  { title: "项目名称", key: "name", minWidth: 180 },
  { title: "状态", key: "status", render: (row) => h(NTag, { type: row.status === "active" ? "success" : "default" }, { default: () => labelOf(statusOptions, row.status) }) },
  { title: "开始日期", key: "start_date" },
  { title: "结束日期", key: "end_date" },
  { title: "描述", key: "description", ellipsis: { tooltip: true } },
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

function resetForm() {
  Object.assign(form, { name: "", description: "", status: "active", start_date: null, end_date: null });
}

async function load() {
  loading.value = true;
  try {
    const data = await projectApi.list(filters);
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
  resetForm();
  drawerVisible.value = true;
}

function openEdit(row: Project) {
  editing.value = row;
  Object.assign(form, row);
  drawerVisible.value = true;
}

async function save() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    if (editing.value?.id) await projectApi.update(editing.value.id, form);
    else await projectApi.create(form);
    message.success("项目已保存");
    drawerVisible.value = false;
    load();
  } finally {
    saving.value = false;
  }
}

function remove(row: Project) {
  dialog.warning({
    title: "删除项目",
    content: `确认删除「${row.name}」？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await projectApi.remove(row.id);
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
