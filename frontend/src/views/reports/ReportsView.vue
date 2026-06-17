<template>
  <div class="page">
    <PageHeader title="报表中心" subtitle="查看历史日报、周报、月报和加班说明，并导出多种格式">
      <n-button @click="load">刷新</n-button>
    </PageHeader>

    <section class="panel panel-pad">
      <n-tabs v-model:value="reportType" @update:value="load">
        <n-tab-pane name="daily" tab="日报" />
        <n-tab-pane name="weekly" tab="周报" />
        <n-tab-pane name="monthly" tab="月报" />
        <n-tab-pane name="overtime" tab="加班说明" />
      </n-tabs>
    </section>

    <section class="panel">
      <n-data-table :columns="columns" :data="items" :loading="loading" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from "vue";
import { NButton, NSpace, NTag, type DataTableColumns } from "naive-ui";
import PageHeader from "@/components/PageHeader.vue";
import { aiApi, downloadExport, type GenerationRecord } from "@/api/resources";

const reportType = ref("weekly");
const items = ref<GenerationRecord[]>([]);
const loading = ref(false);
const columns: DataTableColumns<GenerationRecord> = [
  { title: "类型", key: "report_type", render: (row) => h(NTag, { size: "small" }, { default: () => row.report_type }) },
  { title: "时间范围", key: "range", render: (row) => `${row.date_start} 至 ${row.date_end}` },
  { title: "状态", key: "status" },
  { title: "创建时间", key: "created_at" },
  {
    title: "导出",
    key: "actions",
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => downloadExport(row.id, "markdown") }, { default: () => "Markdown" }),
        h(NButton, { size: "small", onClick: () => downloadExport(row.id, "excel") }, { default: () => "Excel" }),
        h(NButton, { size: "small", onClick: () => downloadExport(row.id, "word") }, { default: () => "Word" }),
        h(NButton, { size: "small", onClick: () => downloadExport(row.id, "pdf") }, { default: () => "PDF" })
      ])
  }
];

async function load() {
  loading.value = true;
  try {
    items.value = (await aiApi.records({ report_type: reportType.value, page_size: 50 })).items;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
