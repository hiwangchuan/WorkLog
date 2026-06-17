<template>
  <n-empty :description="description">
    <template #extra>
      <slot />
    </template>
  </n-empty>
</template>

<script setup lang="ts">
defineProps<{ description: string }>();
</script>
