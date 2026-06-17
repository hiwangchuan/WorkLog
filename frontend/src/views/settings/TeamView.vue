<template>
  <div class="page">
    <PageHeader title="团队管理" subtitle="成员、角色与团队空间">
      <n-button type="primary" @click="openCreate">新建团队</n-button>
    </PageHeader>

    <div class="team-layout">
      <section class="panel">
        <n-data-table :columns="teamColumns" :data="teams" :loading="loading" :pagination="pagination" remote @update:page="onPage" />
      </section>

      <section class="panel panel-pad">
        <template v-if="selectedTeam">
          <div class="section-head">
            <div>
              <h3>{{ selectedTeam.name }}</h3>
              <p>{{ selectedTeam.description || "暂无描述" }}</p>
            </div>
            <n-tag :type="selectedTeam.status === 'active' ? 'success' : 'default'">{{ selectedTeam.status === "active" ? "启用" : "归档" }}</n-tag>
          </div>

          <div class="member-form">
            <n-input v-model:value="memberForm.username" placeholder="用户名或邮箱" />
            <n-select v-model:value="memberForm.role" :options="roleOptions" style="width: 140px" />
            <n-button :loading="memberSaving" @click="addMember">添加成员</n-button>
          </div>

          <n-data-table :columns="memberColumns" :data="members" :loading="memberLoading" />
        </template>
        <EmptyState v-else description="暂无团队">
          <n-button size="small" type="primary" @click="openCreate">新建团队</n-button>
        </EmptyState>
      </section>
    </div>

    <n-drawer v-model:show="drawerVisible" :width="460" placement="right">
      <n-drawer-content :title="editingTeam?.id ? '编辑团队' : '新建团队'">
        <n-form ref="formRef" :model="teamForm" :rules="rules" label-placement="top">
          <n-form-item label="团队名称" path="name"><n-input v-model:value="teamForm.name" /></n-form-item>
          <n-form-item label="团队描述"><n-input v-model:value="teamForm.description" type="textarea" :autosize="{ minRows: 3 }" /></n-form-item>
          <n-form-item label="状态"><n-select v-model:value="teamForm.status" :options="statusOptions" /></n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="drawerVisible = false">取消</n-button>
            <n-button type="primary" :loading="saving" @click="saveTeam">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from "vue";
import { NButton, NSelect, NSpace, NTag, useDialog, useMessage, type DataTableColumns, type FormInst, type FormRules } from "naive-ui";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import { teamApi, type Team, type TeamMember } from "@/api/resources";

const loading = ref(false);
const saving = ref(false);
const memberLoading = ref(false);
const memberSaving = ref(false);
const drawerVisible = ref(false);
const formRef = ref<FormInst | null>(null);
const teams = ref<Team[]>([]);
const members = ref<TeamMember[]>([]);
const selectedTeam = ref<Team | null>(null);
const editingTeam = ref<Team | null>(null);
const total = ref(0);
const filters = reactive({ page: 1, page_size: 20 });
const teamForm = reactive({ name: "", description: "", status: "active" });
const memberForm = reactive({ username: "", role: "member" });
const message = useMessage();
const dialog = useDialog();

const statusOptions = [
  { label: "启用", value: "active" },
  { label: "归档", value: "archived" }
];
const roleOptions = [
  { label: "管理员", value: "admin" },
  { label: "负责人", value: "leader" },
  { label: "成员", value: "member" },
  { label: "只读", value: "viewer" }
];
const rules: FormRules = { name: { required: true, message: "请输入团队名称" } };
const pagination = computed(() => ({ page: filters.page, pageSize: filters.page_size, itemCount: total.value }));

const teamColumns: DataTableColumns<Team> = [
  { title: "团队", key: "name", minWidth: 160 },
  { title: "成员", key: "member_count", width: 80 },
  { title: "我的角色", key: "role", width: 110, render: (row) => roleLabel(row.role || "") },
  {
    title: "状态",
    key: "status",
    width: 90,
    render: (row) => h(NTag, { size: "small", type: row.status === "active" ? "success" : "default" }, { default: () => statusLabel(row.status) })
  },
  {
    title: "操作",
    key: "actions",
    width: 210,
    render: (row) =>
      h(NSpace, { size: "small" }, () => [
        h(NButton, { size: "small", onClick: () => selectTeam(row) }, { default: () => "成员" }),
        h(NButton, { size: "small", onClick: () => openEdit(row) }, { default: () => "编辑" }),
        h(NButton, { size: "small", type: "error", secondary: true, onClick: () => removeTeam(row) }, { default: () => "删除" })
      ])
  }
];

const memberColumns: DataTableColumns<TeamMember> = [
  { title: "用户名", key: "username", minWidth: 150 },
  { title: "邮箱", key: "email", minWidth: 180 },
  {
    title: "角色",
    key: "role",
    width: 160,
    render: (row) =>
      h(NSelect, {
        value: row.role,
        options: roleOptions,
        size: "small",
        onUpdateValue: (role: string) => updateMemberRole(row, role)
      })
  },
  { title: "加入时间", key: "joined_at", width: 180, render: (row) => row.joined_at?.replace("T", " ").slice(0, 16) },
  {
    title: "操作",
    key: "actions",
    width: 90,
    render: (row) =>
      h(NButton, { size: "small", type: "error", secondary: true, onClick: () => removeMember(row) }, { default: () => "移除" })
  }
];

function statusLabel(status: string) {
  return status === "active" ? "启用" : "归档";
}

function roleLabel(role: string) {
  return roleOptions.find((item) => item.value === role)?.label || role || "-";
}

async function loadTeams() {
  loading.value = true;
  try {
    const data = await teamApi.list(filters);
    teams.value = data.items;
    total.value = data.total;
    if (!selectedTeam.value && teams.value.length) await selectTeam(teams.value[0]);
    if (selectedTeam.value) {
      const refreshed = teams.value.find((item) => item.id === selectedTeam.value?.id);
      if (refreshed) selectedTeam.value = refreshed;
    }
  } finally {
    loading.value = false;
  }
}

function onPage(page: number) {
  filters.page = page;
  loadTeams();
}

async function selectTeam(team: Team) {
  selectedTeam.value = team;
  memberLoading.value = true;
  try {
    members.value = await teamApi.members(team.id);
  } finally {
    memberLoading.value = false;
  }
}

function resetTeamForm() {
  Object.assign(teamForm, { name: "", description: "", status: "active" });
}

function openCreate() {
  editingTeam.value = null;
  resetTeamForm();
  drawerVisible.value = true;
}

function openEdit(team: Team) {
  editingTeam.value = team;
  Object.assign(teamForm, { name: team.name, description: team.description || "", status: team.status });
  drawerVisible.value = true;
}

async function saveTeam() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    if (editingTeam.value?.id) await teamApi.update(editingTeam.value.id, teamForm);
    else await teamApi.create(teamForm);
    drawerVisible.value = false;
    message.success("团队已保存");
    await loadTeams();
  } finally {
    saving.value = false;
  }
}

async function addMember() {
  if (!selectedTeam.value || !memberForm.username.trim()) return;
  memberSaving.value = true;
  try {
    await teamApi.addMember(selectedTeam.value.id, { username: memberForm.username.trim(), role: memberForm.role });
    memberForm.username = "";
    message.success("成员已添加");
    await selectTeam(selectedTeam.value);
    await loadTeams();
  } finally {
    memberSaving.value = false;
  }
}

async function updateMemberRole(member: TeamMember, role: string) {
  if (!selectedTeam.value || member.role === role) return;
  await teamApi.updateMember(selectedTeam.value.id, member.id, role);
  message.success("角色已更新");
  await selectTeam(selectedTeam.value);
}

function removeTeam(team: Team) {
  dialog.warning({
    title: "删除团队",
    content: `确认删除「${team.name}」？`,
    positiveText: "删除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await teamApi.remove(team.id);
      if (selectedTeam.value?.id === team.id) {
        selectedTeam.value = null;
        members.value = [];
      }
      message.success("团队已删除");
      await loadTeams();
    }
  });
}

function removeMember(member: TeamMember) {
  if (!selectedTeam.value) return;
  dialog.warning({
    title: "移除成员",
    content: `确认移除「${member.username}」？`,
    positiveText: "移除",
    negativeText: "取消",
    onPositiveClick: async () => {
      await teamApi.removeMember(selectedTeam.value!.id, member.id);
      message.success("成员已移除");
      await selectTeam(selectedTeam.value!);
      await loadTeams();
    }
  });
}

onMounted(loadTeams);
</script>

<style scoped>
.team-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(360px, 0.95fr);
  gap: 16px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-head h3 {
  margin: 0;
  font-size: 18px;
}

.section-head p {
  margin: 4px 0 0;
  color: #64748b;
}

.member-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px auto;
  gap: 10px;
  margin-bottom: 14px;
}

@media (max-width: 1100px) {
  .team-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-form {
    grid-template-columns: 1fr;
  }
}
</style>
