<template>
  <n-layout class="app-shell" has-sider>
    <n-layout-sider
      class="app-sider desktop-only"
      bordered
      collapse-mode="width"
      :collapsed-width="72"
      :width="232"
      :collapsed="collapsed"
    >
      <div class="brand">
        <div class="brand-mark">W</div>
        <div v-if="!collapsed">
          <strong>WorkLog AI</strong>
          <span>安全运营工作台</span>
        </div>
      </div>
      <n-menu :value="activeKey" :options="menuOptions" :collapsed="collapsed" @update:value="go" />
    </n-layout-sider>
    <n-layout>
      <n-layout-header class="topbar" bordered>
        <div class="topbar-left">
          <n-button class="desktop-only" quaternary circle @click="collapsed = !collapsed">
            <template #icon><n-icon><PanelLeft /></n-icon></template>
          </n-button>
          <n-input v-model:value="search" class="global-search" clearable placeholder="搜索任务、记录、项目" />
        </div>
        <div class="topbar-actions">
          <n-button size="small" @click="go('/tasks')">
            <template #icon><n-icon><Plus /></n-icon></template>
            任务
          </n-button>
          <n-button size="small" @click="go('/work-logs')">工作记录</n-button>
          <n-button size="small" @click="go('/overtime')">加班</n-button>
          <n-button type="primary" size="small" @click="go('/ai-report')">AI 周报</n-button>
          <n-dropdown :options="userOptions" @select="handleUserAction">
            <n-button quaternary>{{ auth.user?.nickname || auth.user?.username || "我的" }}</n-button>
          </n-dropdown>
        </div>
      </n-layout-header>
      <n-layout-content class="content">
        <router-view />
      </n-layout-content>
      <nav class="mobile-nav mobile-only">
        <button v-for="item in mobileNav" :key="item.path" :class="{ active: route.path === item.path }" @click="go(item.path)">
          {{ item.label }}
        </button>
      </nav>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import type { MenuOption } from "naive-ui";
import { useAuthStore } from "@/stores/auth";
import {
  BarChart3,
  Bot,
  Briefcase,
  CalendarClock,
  ClipboardList,
  FileText,
  LayoutDashboard,
  PanelLeft,
  PieChart,
  Plus,
  Settings,
  Users
} from "lucide-vue-next";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const collapsed = ref(false);
const search = ref("");

function icon(component: object) {
  return () => h(component as any, { size: 18, strokeWidth: 2 });
}

const menuOptions: MenuOption[] = [
  { label: () => h(RouterLink, { to: "/dashboard" }, { default: () => "首页仪表盘" }), key: "/dashboard", icon: icon(LayoutDashboard) },
  { label: () => h(RouterLink, { to: "/tasks" }, { default: () => "任务管理" }), key: "/tasks", icon: icon(ClipboardList) },
  { label: () => h(RouterLink, { to: "/work-logs" }, { default: () => "工作记录" }), key: "/work-logs", icon: icon(FileText) },
  { label: () => h(RouterLink, { to: "/overtime" }, { default: () => "加班记录" }), key: "/overtime", icon: icon(CalendarClock) },
  { label: () => h(RouterLink, { to: "/projects" }, { default: () => "项目管理" }), key: "/projects", icon: icon(Briefcase) },
  { label: () => h(RouterLink, { to: "/ai-report" }, { default: () => "AI 周报生成" }), key: "/ai-report", icon: icon(Bot) },
  { label: () => h(RouterLink, { to: "/reports" }, { default: () => "报表中心" }), key: "/reports", icon: icon(BarChart3) },
  { label: () => h(RouterLink, { to: "/team" }, { default: () => "团队管理" }), key: "/team", icon: icon(Users) },
  { label: () => h(RouterLink, { to: "/statistics" }, { default: () => "数据统计" }), key: "/statistics", icon: icon(PieChart) },
  { label: () => h(RouterLink, { to: "/settings" }, { default: () => "系统设置" }), key: "/settings", icon: icon(Settings) }
];

const activeKey = computed(() => `/${route.path.split("/")[1] || "dashboard"}`);
const userOptions = [
  { label: "系统设置", key: "settings" },
  { label: "退出登录", key: "logout" }
];
const mobileNav = [
  { label: "首页", path: "/dashboard" },
  { label: "任务", path: "/tasks" },
  { label: "记录", path: "/work-logs" },
  { label: "加班", path: "/overtime" },
  { label: "AI周报", path: "/ai-report" },
  { label: "我的", path: "/settings" }
];

function go(path: string) {
  router.push(path);
}

function handleUserAction(key: string) {
  if (key === "logout") {
    auth.logout();
    router.push("/login");
  } else {
    router.push("/settings");
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-sider {
  background: #ffffff;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 64px;
  padding: 0 18px;
}

.brand-mark {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  border-radius: 10px;
  font-weight: 800;
}

.brand strong,
.brand span {
  display: block;
}

.brand span {
  color: #64748b;
  font-size: 12px;
}

.menu-icon {
  display: inline-flex;
  width: 18px;
  height: 18px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
}

.topbar-left,
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.global-search {
  width: min(360px, 40vw);
}

.content {
  min-height: calc(100vh - 64px);
  padding: 20px;
  background: #f5f7fb;
}

.mobile-nav {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  padding: 8px 6px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
}

.mobile-nav button {
  border: 0;
  color: #64748b;
  background: transparent;
  font-size: 12px;
}

.mobile-nav button.active {
  color: #2563eb;
  font-weight: 700;
}

@media (max-width: 900px) {
  .topbar {
    padding: 0 12px;
  }

  .global-search {
    width: 48vw;
  }

  .topbar-actions {
    gap: 4px;
  }

  .content {
    padding: 14px 12px 70px;
  }
}
</style>
