<template>
  <div class="home">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="导入小说" name="import">
        <NovelImport @import-success="handleImportSuccess" />
      </el-tab-pane>
      <el-tab-pane label="章节管理" name="chapters">
        <!-- 原有的章节管理内容 -->
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import NovelImport from '../components/NovelImport.vue'

const activeTab = ref('import')

const handleImportSuccess = () => {
  // 导入成功后切换到章节管理标签页
  activeTab.value = 'chapters'
  // 刷新章节列表
  // ... 刷新章节列表的代码 ...
}
</script>

<style scoped>
.home {
  padding: 20px;
}
</style> 