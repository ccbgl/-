<template>
  <div class="spinner-container" v-if="loading">
    <el-skeleton :rows="rows" animated />
  </div>
  <slot v-else />
</template>

<script setup>
defineProps({
  loading: { type: Boolean, default: false },
  rows: { type: Number, default: 5 }
})
</script>

<style scoped>
.spinner-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>