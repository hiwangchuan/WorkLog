<template>
  <div class="page">
    <PageHeader title="加班记录" subtitle="记录加班、夜间值守和调休状态">
      <n-button type="primary" @click="openCreate">新增加班</n-button>
    </PageHeader>

    <div class="grid cols-5">
      <StatCard label="本月加班" :value="`${totalHours}h`" color="#f59e0b" />
      <StatCard label="工作日" :value="`${typeHours.weekday || 0}h`" />
      <StatCard label="周末" :value="`${typeHours.weekend || 0}h`" color="#2563eb" />
      <StatCard label="节假日" :value="`${typeHours.holiday || 0}h`" color="#ef4444" />
      <StatCard label="调休余额" value="预留" hint="团队版启用审批后计算" />
    </div>

    <section class="panel panel-pad">
      <div class="toolbar">
        <n-select v-model:value="filters.overtime_type" clearable placeholder="加班类型" :options="overtimeTypeOptions" style="width: 160px" />
        <n-select v-model:value="filters.approval_status" clearable placeholder="审核状态" :options="approvalOptions" style="width: 160px" />
        <n-button @click="load">筛选</n-button>
      </div>
    </section>

    <section class="panel">
      <n-data-table :columns="columns" :data="items" :loading="loading" :pagination="pagination" remote @update:page="onPage" />
    </section>

    <n-drawer v-model:show="drawerVisible" :width="520" placement="right">
      <n-drawer-content :title="editing?.id ? '编辑加班记录' : '新增加班记录'">
        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-grid :cols="2" :x-gap="12">
            <n-form-item-gi label="加班日期" path="overtime_date"><n-date-picker v-model:formatted-value="form.overtime_date" value-format="yyyy-MM-dd" type="date" /></n-form-item-gi>
            <n-form-item-gi label="加班类型"><n-select v-model:value="form.overtime_type" :options="overtimeTypeOptions" /></n-form-item-gi>
          </n-grid>
          <n-grid :cols="3" :x-gap="12">
            <n-form-item-gi label="开始时间"><n-time-picker v-model:formatted-value="form.start_time" value-format="HH:mm" format="HH:mm" clearable /></n-form-item-gi>
            <n-form-item-gi label="结束时间"><n-time-picker v-model:formatted-value="form.end_time" value-format="HH:mm" format="HH:mm" clearable /></n-form-item-gi>
            <n-form-item-gi label="时长"><n-input-number v-model:value="form.duration_hours" :min="0" /></n-form-item-gi>
          </n-grid>
          <n-form-item label="加班原因"><n-input v-model:value="form.reason" type="textarea" /></n-form-item>
          <n-form-item label="具体工作内容"><n-input v-model:value="form.content" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
          <n-checkbox v-model:checked="form.is_compensatory_leave">计入调休</n-checkbox>
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
import dayjs from "dayjs";
import { computed, h, onMounted, reactive, ref, watch } from "vue";
import { NButton, NSpace, NTag, useDialog, useMessage, type DataTableColumns, type FormInst, type FormRules } from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import { overtimeApi, type OvertimeLog } from "@/api/resources";
import { labelOf, overtimeTypeOptions } from "@/utils/options";

const approvalOptions = [
  { label: "草稿", value: "draft" },
  { label: "待审核", value: "pending" },
  { label: "已通过", value: "approved" },
  { label: "已驳回", value: "rejected" }
];
const message = useMessage();
const dialog = useDialog();
const formRef = ref<FormInst | null>(null);
const items = ref<OvertimeLog[]>([]);
const total = ref(0);
const loading = ref(false);
const saving = ref(false);
const drawerVisible = ref(false);
const editing = ref<OvertimeLog | null>(null);
const filters = reactive<any>({ overtime_type: null, approval_status: null, page: 1, page_size: 20 });
const form = reactive<any>({});
const rules: FormRules = { overtime_date: { required: true, message: "请选择日期" } };
const pagination = computed(() => ({ page: filters.page, pageSize: filters.page_size, itemCount: total.value }));
const totalHours = computed(() => Number(items.value.reduce((sum, item) => sum + item.duration_hours, 0).toFixed(2)));
const typeHours = computed(() =>
  items.value.reduce<Record<string, number>>((acc, item) => {
    acc[item.overtime_type] = Number(((acc[item.overtime_type] || 0) + item.duration_hours).toFixed(2));
    return acc;
  }, {})
);

const columns: DataTableColumns<OvertimeLog> = [
  { title: "日期", key: "overtime_date" },
  { title: "类型", key: "overtime_type", render: (row) => h(NTag, { size: "small" }, { default: () => labelOf(overtimeTypeOptions, row.overtime_type) }) },
  { title: "开始", key: "start_time" },
  { title: "结束", key: "end_time" },
  { title: "时长", key: "duration_hours", render: (row) => `${row.duration_hours}h` },
  { title: "原因", key: "reason", ellipsis: { tooltip: true } },
  { title: "审核状态", key: "approval_status", render: (row) => h(NTag, { size: "small" }, { default: () => labelOf(approvalOptions, row.approval_status) }) },
  {
    title: "操作",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => openEdit(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", onClick: () => submit(row) }, { default: () => "提交" }),
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
    overtime_date: dayjs().format("YYYY-MM-DD"),
    overtime_type: "weekday",
    start_time: null,
    end_time: null,
    duration_hours: 0,
    reason: "",
    content: "",
    approval_status: "draft",
    is_compensatory_leave: false,
    compensatory_status: "none"
  });
}

async function load() {
  loading.value = true;
  try {
    const data = await overtimeApi.list(filters);
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

function openEdit(row: OvertimeLog) {
  editing.value = row;
  Object.assign(form, row);
  drawerVisible.value = true;
}

async function save() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    if (editing.value?.id) await overtimeApi.update(editing.value.id, form);
    else await overtimeApi.create(form);
    message.success("加班记录已保存");
    drawerVisible.value = false;
    load();
  } finally {
    saving.value = false;
  }
}

async function submit(row: OvertimeLog) {
  await overtimeApi.submit(row.id);
  message.success("已提交审核");
  load();
}

function remove(row: OvertimeLog) {
  dialog.warning({
    title: "删除加班记录",
    content: `确认删除 ${row.overtime_date} 的加班记录？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await overtimeApi.remove(row.id);
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
