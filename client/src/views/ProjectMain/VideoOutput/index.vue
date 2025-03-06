<template>
  <div class="video-output">
    <h3>视频输出</h3>
    
    <!-- 章节选择 -->
    <div class="section">
      <el-select 
        v-model="selectedChapter" 
        placeholder="请选择章节"
        @change="handleChapterChange"
      >
        <el-option
          v-for="chapter in chapters"
          :key="chapter"
          :label="chapter"
          :value="chapter"
        />
      </el-select>
    </div>

    <!-- 视频配置表单 -->
    <div class="config-section">
      <el-form :model="videoSettings" label-width="120px">
        <el-form-item label="缩放系数">
          <el-input-number 
            v-model="videoSettings.zoom_factor" 
            :min="0.1" 
            :max="2" 
            :step="0.1"
          />
        </el-form-item>
        
        <el-form-item label="平移强度">
          <el-input-number 
            v-model="videoSettings.pan_intensity" 
            :min="0" 
            :max="10"
          />
        </el-form-item>

        <el-form-item label="字体名称">
          <el-input v-model="videoSettings.font_name" />
        </el-form-item>

        <el-form-item label="字体大小">
          <el-input-number v-model="videoSettings.font_size" :min="10" :max="72" />
        </el-form-item>

        <el-form-item label="分辨率">
          <el-input
  v-model="resolutionInput"
  placeholder="输入格式：1920,1080"
/>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮和视频区域 -->
    

    <div class="video-preview" v-if="videoUrl">
      <video 
        controls
        :src="videoUrl"
        class="video-player"
      >

        您的浏览器不支持视频播放
      </video>
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <div class="action-section">
      <el-button 
        type="primary" 
        :loading="isGenerating"
        @click="handleGenerateVideo"
      >
        生成视频
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { chapterApi } from '@/api/chapter_api'
import { videoApi } from '@/api/video_api'
import type { VideoSettings } from '@/types/video'
import { getResourcePath } from '@/utils/resourcePath'

const route = useRoute()
const projectName = route.params.name as string

// 章节相关
const chapters = ref<string[]>([])
const selectedChapter = ref('')

// 视频设置
const videoSettings = ref<VideoSettings>({
  project_name: projectName,
  chapter_name:'',
  zoom_factor: 1.0,
  pan_intensity: 5,
  font_name: 'Arial',
  font_size: 24,
  resolution:[1920,1080]
})

// 状态管理
const isGenerating = ref(false)
const videoUrl = ref('')
const errorMessage = ref('')

const resolutionInput = ref('')

// 获取章节列表
// 在组件中修改视频生成处理逻辑
const handleGenerateVideo = async () => {
  try {
    // 构造符合后端要求的参数结构
    videoSettings.value.resolution=resolutionInput.value
          ? (resolutionInput.value.split(',').map(Number) as [number, number])
          : [1920,1080]

    videoSettings.value.chapter_name = selectedChapter.value;
    // 清除空值字段

    isGenerating.value = true;
    const res=await videoApi.generateVideo(
      videoSettings .value 
    )
    if (res) {
      handleChapterChange();
      isGenerating.value = false;
    }
  } catch (error) {
    // 错误处理
    console.log(error)
    isGenerating.value = false;
  }
}

// 修改后的章节获取逻辑
const fetchChapters = async () => {
  try {
    const res = await chapterApi.getChapterList(projectName)
    
    chapters.value = res as unknown as string[]

    if (chapters.value.length > 0) {
      selectedChapter.value = chapters.value[0]
      videoUrl.value = getResourcePath(projectName, selectedChapter.value, 0, 'video')
    }
    
  } catch (error) {
    errorMessage.value = '获取章节列表失败'
  }
}

// 章节变更处理
const handleChapterChange = () => {
  videoUrl.value = getResourcePath(projectName, selectedChapter.value,0,'video')
}

// 初始化
onMounted(() => {
  fetchChapters()

})
</script>

<style scoped>
.video-output {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.section {
  margin-bottom: 24px;
}

.config-section {
  margin: 24px 0;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.video-preview {
  margin-top: 24px;
}

.video-player {
  width: 100%;
  max-width: 720px;
  border-radius: 4px;
  background: #000;
}

.error-message {
  color: #f56c6c;
  margin-top: 12px;
}

.action-section {
  margin: 16px 0;
}
</style>