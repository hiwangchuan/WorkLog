<template>
  <div class="page-title">
    <div>
      <h1>{{ title }}</h1>
      <div v-if="subtitle" class="muted">{{ subtitle }}</div>
    </div>
    <div class="toolbar">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();
</script>
