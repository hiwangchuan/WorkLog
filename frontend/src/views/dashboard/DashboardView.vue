<template>
  <div class="page">
    <PageHeader title="首页仪表盘" subtitle="汇总任务、工时、加班与近期安全运营记录">
      <n-button type="primary" @click="$router.push('/work-logs')">快速新增工作记录</n-button>
      <n-button @click="$router.push('/ai-report')">生成周报</n-button>
    </PageHeader>

    <div class="grid cols-5">
      <StatCard label="今日待办" :value="summary.today_todo ?? 0" hint="未完成任务" />
      <StatCard label="今日完成" :value="summary.today_completed ?? 0" color="#16a34a" />
      <StatCard label="本周完成" :value="summary.week_completed ?? 0" color="#2563eb" />
      <StatCard label="本月工时" :value="`${summary.month_work_hours ?? 0}h`" color="#0f766e" />
      <StatCard label="本月加班" :value="`${summary.month_overtime_hours ?? 0}h`" hint="含值守与周末支撑" color="#f59e0b" />
    </div>

    <div class="grid cols-2">
      <section class="panel panel-pad">
        <div class="section-head">
          <h2>本周工时趋势</h2>
          <span class="muted">按工作记录自动汇总</span>
        </div>
        <ChartBox :option="workTrendOption" />
      </section>
      <section class="panel panel-pad">
        <div class="section-head">
          <h2>任务状态分布</h2>
          <span class="muted">任务闭环情况</span>
        </div>
        <ChartBox :option="taskStatusOption" />
      </section>
    </div>

    <div class="grid cols-3">
      <section class="panel panel-pad">
        <div class="section-head">
          <h2>今日待办任务</h2>
          <n-tag type="error" v-if="summary.overdue_tasks">{{ summary.overdue_tasks }} 个超期</n-tag>
        </div>
        <n-list v-if="summary.today_tasks?.length">
          <n-list-item v-for="task in summary.today_tasks" :key="task.id">
            <n-thing :title="task.title">
              <template #description>
                <n-space size="small">
                  <n-tag size="small" :type="tagType(taskStatusOptions, task.status) as any">{{ labelOf(taskStatusOptions, task.status) }}</n-tag>
                  <n-tag size="small" :type="tagType(priorityOptions, task.priority) as any">{{ labelOf(priorityOptions, task.priority) }}</n-tag>
                  <span v-if="task.due_date" class="muted">截止 {{ task.due_date }}</span>
                </n-space>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        <EmptyState v-else description="暂无待办任务">
          <n-button size="small" @click="$router.push('/tasks')">创建任务</n-button>
        </EmptyState>
      </section>

      <section class="panel panel-pad">
        <div class="section-head">
          <h2>最近工作记录</h2>
          <n-button text type="primary" @click="$router.push('/work-logs')">查看全部</n-button>
        </div>
        <n-timeline v-if="summary.recent_work_logs?.length">
          <n-timeline-item
            v-for="log in summary.recent_work_logs"
            :key="log.id"
            :title="log.title"
            :content="`${log.work_date} · ${labelOf(workTypeOptions, log.work_type)} · ${log.duration_hours}h`"
          />
        </n-timeline>
        <EmptyState v-else description="暂无工作记录">
          <n-button size="small" @click="$router.push('/work-logs')">新增记录</n-button>
        </EmptyState>
      </section>

      <section class="panel panel-pad">
        <div class="section-head">
          <h2>项目工时分布</h2>
          <span class="muted">按项目聚合</span>
        </div>
        <ChartBox :option="projectHoursOption" />
      </section>
    </div>

    <section class="panel panel-pad">
      <div class="section-head">
        <h2>加班趋势</h2>
        <span class="muted">近 30 天加班与值守</span>
      </div>
      <ChartBox :option="overtimeOption" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import ChartBox from "@/components/ChartBox.vue";
import EmptyState from "@/components/EmptyState.vue";
import { dashboardApi } from "@/api/resources";
import { labelOf, priorityOptions, tagType, taskStatusOptions, workTypeOptions } from "@/utils/options";

const summary = ref<any>({});
const workTrend = ref<any[]>([]);
const statusData = ref<any[]>([]);
const projectData = ref<any[]>([]);
const overtimeData = ref<any[]>([]);

const axis = { axisLine: { lineStyle: { color: "#e5e7eb" } }, axisLabel: { color: "#64748b" } };

const workTrendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 18, top: 28, bottom: 36 },
  xAxis: { type: "category", data: workTrend.value.map((i) => i.date.slice(5)), ...axis },
  yAxis: { type: "value", ...axis },
  series: [{ type: "line", smooth: true, areaStyle: { color: "rgba(37,99,235,.12)" }, data: workTrend.value.map((i) => i.hours), color: "#2563eb" }]
}));

const taskStatusOption = computed(() => ({
  tooltip: { trigger: "item" },
  legend: { bottom: 0 },
  series: [{ type: "pie", radius: ["45%", "70%"], data: statusData.value, color: ["#94a3b8", "#2563eb", "#f59e0b", "#16a34a", "#cbd5e1"] }]
}));

const projectHoursOption = computed(() => ({
  tooltip: {},
  grid: { left: 36, right: 12, top: 20, bottom: 34 },
  xAxis: { type: "category", data: projectData.value.map((i) => i.name), ...axis },
  yAxis: { type: "value", ...axis },
  series: [{ type: "bar", data: projectData.value.map((i) => i.hours), color: "#14b8a6", barWidth: 18 }]
}));

const overtimeOption = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { left: 36, right: 18, top: 28, bottom: 36 },
  xAxis: { type: "category", data: overtimeData.value.map((i) => i.date.slice(5)), ...axis },
  yAxis: { type: "value", ...axis },
  series: [{ type: "bar", data: overtimeData.value.map((i) => i.hours), color: "#f59e0b", barWidth: 16 }]
}));

async function load() {
  const [s, trend, status, projects, overtime] = await Promise.all([
    dashboardApi.summary(),
    dashboardApi.workTrend(),
    dashboardApi.taskStatus(),
    dashboardApi.projectHours(),
    dashboardApi.overtimeTrend()
  ]);
  summary.value = s;
  workTrend.value = trend;
  statusData.value = status;
  projectData.value = projects;
  overtimeData.value = overtime;
}

onMounted(load);
</script>

<style scoped>
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-head h2 {
  margin: 0;
  font-size: 16px;
}
</style>
