import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import AppLayout from "@/layouts/AppLayout.vue";

const routes: RouteRecordRaw[] = [
  { path: "/login", name: "login", component: () => import("@/views/auth/LoginView.vue"), meta: { public: true } },
  { path: "/register", name: "register", component: () => import("@/views/auth/RegisterView.vue"), meta: { public: true } },
  {
    path: "/",
    component: AppLayout,
    children: [
      { path: "", redirect: "/dashboard" },
      { path: "dashboard", name: "dashboard", component: () => import("@/views/dashboard/DashboardView.vue") },
      { path: "tasks", name: "tasks", component: () => import("@/views/tasks/TasksView.vue") },
      { path: "work-logs", name: "workLogs", component: () => import("@/views/work-logs/WorkLogsView.vue") },
      { path: "overtime", name: "overtime", component: () => import("@/views/overtime/OvertimeView.vue") },
      { path: "projects", name: "projects", component: () => import("@/views/projects/ProjectsView.vue") },
      { path: "ai-report", name: "aiReport", component: () => import("@/views/ai-report/AIReportView.vue") },
      { path: "reports", name: "reports", component: () => import("@/views/reports/ReportsView.vue") },
      { path: "statistics", name: "statistics", component: () => import("@/views/statistics/StatisticsView.vue") },
      { path: "settings", name: "settings", component: () => import("@/views/settings/SettingsView.vue") },
      { path: "team", name: "team", component: () => import("@/views/settings/TeamView.vue") }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.token) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  if (to.meta.public && auth.token) {
    return "/dashboard";
  }
});

export default router;
