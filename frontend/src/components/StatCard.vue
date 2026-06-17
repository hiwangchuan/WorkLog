<template>
  <div class="panel stat-card">
    <div class="label">{{ label }}</div>
    <div class="value" :style="{ color }">{{ value }}</div>
    <div v-if="hint" class="hint">{{ hint }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  hint?: string;
  color?: string;
}>();
</script>
