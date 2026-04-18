<template>
  <el-tag
    :type="tagType"
    :effect="effect"
    :class="{ 'status-running': status === 'running' }"
    size="small"
  >
    {{ statusText }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: v => ['pending', 'running', 'success', 'failed'].includes(v)
  },
  effect: {
    type: String,
    default: 'dark'
  }
})

const statusMap = {
  pending: { text: '排队中', type: 'info' },
  running: { text: '执行中', type: 'warning' },
  success: { text: '执行完成', type: 'success' },
  failed: { text: '执行失败', type: 'danger' }
}

const tagType = computed(() => statusMap[props.status]?.type || 'info')
const statusText = computed(() => statusMap[props.status]?.text || props.status)
</script>

<style scoped>
.status-running {
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.75; }
}
</style>