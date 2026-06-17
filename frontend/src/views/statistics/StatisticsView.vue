<template>
  <div class="page">
    <PageHeader title="数据统计" subtitle="工时、任务、项目、加班和工作类型的多维统计" />
    <div class="grid cols-2">
      <section class="panel panel-pad"><h2>每日工时趋势</h2><ChartBox :option="workOption" /></section>
      <section class="panel panel-pad"><h2>任务状态分布</h2><ChartBox :option="taskOption" /></section>
      <section class="panel panel-pad"><h2>项目工时分布</h2><ChartBox :option="projectOption" /></section>
      <section class="panel panel-pad"><h2>加班趋势</h2><ChartBox :option="overtimeOption" /></section>
      <section class="panel panel-pad"><h2>工作类型占比</h2><ChartBox :option="typeOption" /></section>
      <section class="panel panel-pad"><h2>工作记录热力</h2><ChartBox :option="heatOption" /></section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import ChartBox from "@/components/ChartBox.vue";
import { statisticsApi } from "@/api/resources";

const work = ref<any[]>([]);
const task = ref<any[]>([]);
const project = ref<any[]>([]);
const overtime = ref<any[]>([]);
const types = ref<any[]>([]);
const heat = ref<any[]>([]);
const axis = { axisLine: { lineStyle: { color: "#e5e7eb" } }, axisLabel: { color: "#64748b" } };
const workOption = computed(() => lineOption(work.value.map((i) => i.date?.slice(5)), work.value.map((i) => i.hours), "#2563eb"));
const overtimeOption = computed(() => lineOption(overtime.value.map((i) => i.date?.slice(5)), overtime.value.map((i) => i.hours), "#f59e0b"));
const taskOption = computed(() => pieOption(task.value));
const typeOption = computed(() => pieOption(types.value));
const projectOption = computed(() => barOption(project.value.map((i) => i.name), project.value.map((i) => i.hours), "#14b8a6"));
const heatOption = computed(() => barOption(heat.value.map((i) => i.date?.slice(5)), heat.value.map((i) => i.value), "#6366f1"));

function lineOption(x: string[], y: number[], color: string) {
  return { tooltip: { trigger: "axis" }, grid: { left: 36, right: 18, top: 28, bottom: 36 }, xAxis: { type: "category", data: x, ...axis }, yAxis: { type: "value", ...axis }, series: [{ type: "line", smooth: true, areaStyle: {}, data: y, color }] };
}

function barOption(x: string[], y: number[], color: string) {
  return { tooltip: {}, grid: { left: 36, right: 18, top: 28, bottom: 36 }, xAxis: { type: "category", data: x, ...axis }, yAxis: { type: "value", ...axis }, series: [{ type: "bar", data: y, color, barWidth: 16 }] };
}

function pieOption(data: any[]) {
  return { tooltip: { trigger: "item" }, legend: { bottom: 0 }, series: [{ type: "pie", radius: ["45%", "70%"], data }] };
}

async function load() {
  const [workData, taskData, projectData, overtimeData, typeData, heatData] = await Promise.all([
    statisticsApi.workHours(),
    statisticsApi.tasks(),
    statisticsApi.projects(),
    statisticsApi.overtime(),
    statisticsApi.workTypes(),
    statisticsApi.heatmap()
  ]);
  work.value = workData.trend;
  task.value = taskData.status;
  project.value = projectData;
  overtime.value = overtimeData.trend;
  types.value = typeData;
  heat.value = heatData;
}

onMounted(load);
</script>

<style scoped>
h2 {
  margin: 0 0 12px;
  font-size: 16px;
}
</style>
