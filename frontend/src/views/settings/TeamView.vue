<template>
  <div class="page">
    <PageHeader title="团队管理" subtitle="第一版以个人空间为主，团队角色、成员和审批能力已在数据结构中预留" />
    <section class="panel panel-pad">
      <n-alert type="info">当前空间：个人空间。后续可扩展成员邀请、角色权限、加班审批和团队周报。</n-alert>
      <n-descriptions bordered :column="2" style="margin-top: 16px">
        <n-descriptions-item label="预留角色">管理员、负责人、普通成员、只读成员</n-descriptions-item>
        <n-descriptions-item label="数据范围">仅自己、项目成员、团队、管理员</n-descriptions-item>
        <n-descriptions-item label="审批能力">加班提交、通过、驳回字段已预留</n-descriptions-item>
        <n-descriptions-item label="团队统计">成员工作量排行和团队工时接口可扩展</n-descriptions-item>
      </n-descriptions>
    </section>
  </div>
</template>

<script setup lang="ts">
import PageHeader from "@/components/PageHeader.vue";
</script>
