<template>
  <div class="video-output">
    <h3>视频输出</h3>
    <!-- 视频输出相关内容 -->
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import type { ProjectInfo } from '@/types/project'

const route = useRoute()
const projectName = route.params.name as string

// 这里添加视频输出相关的逻辑
</script>

<style scoped>
.video-output {
  padding: 20px;
}
</style>
