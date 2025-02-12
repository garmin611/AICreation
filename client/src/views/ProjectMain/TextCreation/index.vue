<template>
  <div class="text-creation">
    <!-- 章节列表栏 -->
    <div class="chapter-header">
      <el-select
        v-model="currentChapter"
        class="chapter-select"
        :placeholder="t('chapter.selectPlaceholder')"
        @change="handleChapterChange"
        :disabled="isOperating"
      >
        <el-option
          v-for="chapter in chapters"
          :key="chapter"
          :label="chapter"
          :value="chapter"
        />
      </el-select>
      <el-button type="primary" @click="handleAddChapter" :loading="adding" :disabled="isOperating">
        <el-icon><Plus /></el-icon>
        {{ t('textCreation.addChapter') }}
      </el-button>
    </div>

    <!-- 设置栏 -->
    <div class="settings-bar">
      <el-switch
        v-model="isContinueMode"
        :active-text="t('textCreation.continueMode')"
        :inactive-text="t('textCreation.createMode')"
      />
      <el-checkbox
        v-model="useLastChapter"
      >
        {{ t('textCreation.useLastChapter') }}
      </el-checkbox>
    </div>

    <!-- 文本内容栏 -->
    <el-input
      v-model="content"
      type="textarea"
      :rows="20"
      :placeholder="inputPlaceholder"
      resize="none"
    />

    <!-- 按钮栏 -->
    <div class="action-bar">
      <el-button
        type="primary"
        @click="handleSplitChapter"
        :disabled="!currentChapter || !content || isOperating"
        :loading="splitting"
      >
        <el-icon><ScaleToOriginal /></el-icon>
        {{ t('textCreation.splitChapter') }}
      </el-button>
      <el-button
        type="primary"
        @click="handleExtractCharacters"
        :disabled="!currentChapter || !content || isOperating"
        :loading="extracting"
      >
        <el-icon><User /></el-icon>
        {{ t('textCreation.extractCharacters') }}
      </el-button>
      <div class="right-buttons">
        <el-button
          type="primary"
          @click="()=>handleSave()"
          :loading="saving"
          :disabled="!canSave"
        >
          <el-icon><Check /></el-icon>
          {{ t('common.save') }}
        </el-button>
        <el-button
          type="primary"
          @click="handleGenerate"
          :loading="generating"
          :disabled="isOperating"
        >
          <el-icon><Plus /></el-icon>
          {{ t('textCreation.write')}}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, ScaleToOriginal, Check, User } from '@element-plus/icons-vue'
import { chapterApi } from '@/api/chapter_api'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const projectName = computed(() => route.params.name as string)

// 状态变量
const chapters = ref<string[]>([])  // 章节列表
const currentChapter = ref('')  // 当前选中的章节
const content = ref('')  // 当前章节内容
const isContinueMode = ref(false)  // 是否为续写模式
const useLastChapter = ref(true)  // 是否使用上一章内容作为上下文
const hasContentChanged = ref(false)  // 内容是否发生变化

// 加载状态
const saving = ref(false)  // 保存中
const adding = ref(false)  // 添加章节中
const generating = ref(false)  // 生成内容中
const splitting = ref(false)  // 分割章节中
const extracting = ref(false)  // 是否正在提取角色

// 自动保存定时器
let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

// 监听内容变化，5秒后触发自动保存
watch(content, (newValue) => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  
  // 标记内容已变化
  hasContentChanged.value = true
  
  // if (newValue.trim() && !isOperating.value) {
  //   autoSaveTimer = setTimeout(async () => {
  //     try {
  //       await handleSave(false)
  //     } catch (error) {
  //       console.error('Auto save failed:', error)
  //     }
  //   }, 5000)
  // }
})

// 计算属性
const isOperating = computed(() => {
  return saving.value || adding.value || generating.value || splitting.value || extracting.value
})

const canSave = computed(() => {//是否能够保存
  return !isOperating.value && content.value.trim() && hasContentChanged.value
})

const inputPlaceholder = computed(() => {
  return isContinueMode.value
    ? t('textCreation.continuePlaceholder')
    : t('textCreation.createPlaceholder')
})

// 获取章节列表
const fetchChapterList = async () => {
  try {
    const response = await chapterApi.getChapterList(projectName.value)
    chapters.value = response
    if (chapters.value.length > 0) {
      currentChapter.value = chapters.value[chapters.value.length - 1]
      await fetchChapterContent()
    }
  } catch (error: any) {
    ElMessage.error(error.message || t('error.fetchChapterListFailed'))
  }
}

// 获取当前章节内容
const fetchChapterContent = async () => {
  if (!currentChapter.value) return
  
  try {
    const response = await chapterApi.getChapterContent(
      projectName.value,
      currentChapter.value
    )
    content.value = response.content
    // 重置内容变化标记
    hasContentChanged.value = false
  } catch (error: any) {
    ElMessage.error(error.message || t('error.fetchChapterContentFailed'))
  }
}

// 章节选择变更处理
const handleChapterChange = async () => {
  await fetchChapterContent()
}

// 添加新章节
const handleAddChapter = async () => {
  try {
    adding.value = true
    const data = await chapterApi.createChapter(projectName.value)
    
    // 刷新章节列表
    await fetchChapterList()
    
    // 切换到新章节
    currentChapter.value = data.chapter
    await fetchChapterContent()
    
    // 清空内容
    content.value = ''
    
    ElMessage.success(t('textCreation.chapterCreated'))
  } catch (error: any) {
    ElMessage.error(error.message || t('common.operationFailed'))
  } finally {
    adding.value = false
  }
}

// 保存章节内容，showMessage为true时显示保存成功提示
const handleSave = async (showMessage = true) => {
  if (!currentChapter.value || !content.value.trim()) return
  
  try {
    saving.value = true
    await chapterApi.saveChapterContent({
      project_name: projectName.value,
      chapter_name: currentChapter.value,
      content: content.value
    })
    // 重置内容变化标记
    hasContentChanged.value = false
    if (showMessage) {
      ElMessage.success(t('success.saved'))
    }
  } catch (error: any) {
    ElMessage.error(error.message || t('error.saveFailed'))
  } finally {
    saving.value = false
  }
}

// 使用AI生成或续写文本内容
const handleGenerate = async () => {
  if (!content.value.trim()) {
    ElMessage.warning(t('error.contentRequired'))
    return
  }

  try {
    generating.value = true
    const data = await chapterApi.generateChapter({
      project_name: projectName.value,
      chapter_name: currentChapter.value,
      prompt: content.value,
      is_continuation: isContinueMode.value,
      use_last_chapter: useLastChapter.value
    })
    if(isContinueMode.value){
      content.value = content.value+"\n"+data
    }else{
      content.value = data
    }
    // 标记内容已变化
    hasContentChanged.value = true
  } catch (error: any) {
    ElMessage.error(error.message || t('error.generateFailed'))
  } finally {
    generating.value = false
  }
}

// 将当前章节分割为多个span
const handleSplitChapter = async () => {
  if (!currentChapter.value || !content.value) return
  
  try {
    splitting.value = true
    await chapterApi.splitChapter(projectName.value, currentChapter.value)
    ElMessage.success(t('textCreation.splitChapterSuccess'))
    router.push(`/project/${projectName.value}/storyboard-process`)
  } catch (error: any) {
    ElMessage.error(error.message || t('textCreation.splitChapterError'))
  } finally {
    splitting.value = false
  }
}

// 提取章节中的角色
const handleExtractCharacters = async () => {
  if (!currentChapter.value || !content.value) return
  
  extracting.value = true
  try {
    const res = await chapterApi.extractCharacters(projectName.value, currentChapter.value)
    if (res.status === 'success') {
      ElMessage.success(t('textCreation.extractSuccess'))
      // 这里可以根据需要处理提取到的角色信息，比如显示在对话框中
      console.log('提取到的角色信息：', res.data)
    } 
  } catch (error) {
    console.error('提取角色失败：', error)
    ElMessage.error(t('common.error'))
  } finally {
    extracting.value = false
  }
}

// 组件挂载时加载章节列表
onMounted(() => {
  fetchChapterList()
})
</script>

<style lang="scss" scoped>
.text-creation {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

.chapter-header {
  display: flex;
  gap: 10px;

  .chapter-select {
  flex: 1;
}

  button{
    width: 120px;
  }
}



.settings-bar {
  display: flex;
  gap: 20px;
  align-items: center;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.right-buttons {
  display: flex;
  gap: 10px;
}
</style>