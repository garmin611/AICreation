<template>
  <div class="video-output">
    <h3>{{ t('videoOutput.title') }}</h3>
    
    <!-- 章节选择 -->
    <div class="section">
      <el-select 
        v-model="selectedChapter" 
        :placeholder="t('videoOutput.chapterSelect')"
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
      <el-form :model="videoSettings" label-width="180px">
        <!-- 淡入淡出设置 -->
        <el-form-item :label="t('videoOutput.fadeDuration')">
          <el-input-number 
            v-model="videoSettings.fade_duration" 
            :min="0" 
            :max="2"
          />
        </el-form-item>
        <!-- 画面平移设置 -->
        <el-form-item :label="t('videoOutput.usePan')">
          <el-switch v-model="videoSettings.use_pan" />
        </el-form-item>
        
        <template v-if="videoSettings.use_pan">
          <el-form-item :label="t('videoOutput.panRangeX')">
            <el-slider 
              v-model="videoSettings.pan_range[0]" 
              :min="0" 
              :max="1" 
              :step="0.1" 
            />
          </el-form-item>
          
          <el-form-item :label="t('videoOutput.panRangeY')">
            <el-slider 
              v-model="videoSettings.pan_range[1]" 
              :min="0" 
              :max="1" 
              :step="0.1" 
            />
          </el-form-item>
        </template>

        <!-- 帧率设置 -->
        <el-form-item :label="t('videoOutput.fps')">
          <el-input-number 
            v-model="videoSettings.fps" 
            :min="1" 
            :max="60"
          />
        </el-form-item>

        <!-- 分辨率设置 -->
        <el-form-item :label="t('videoOutput.resolution')">
          <el-input-number 
            v-model="videoSettings.resolution[0]" 
            :min="480" 
            :max="3840"
            :step="16"
            :placeholder="t('videoOutput.width')"
            style="margin-right: 10px"
          />
          <el-input-number 
            v-model="videoSettings.resolution[1]" 
            :min="360" 
            :max="2160"
            :step="16"
            :placeholder="t('videoOutput.height')"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮和视频区域 -->
    <div class="action-section">
      <el-button 
        type="primary" 
        :loading="isGenerating"
        @click="handleGenerateVideo"
      >
        {{ t('videoOutput.generateVideo') }}
      </el-button>
    </div>

    <div class="video-preview" v-if="videoUrl">
      <video 
        controls
        :src="videoUrl"
        class="video-player"
      >
        {{ t('videoOutput.browserNotSupport') }}
      </video>
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
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
import { useI18n } from 'vue-i18n'

const route = useRoute()
const projectName = route.params.name as string

const { t } = useI18n()

// 章节相关
const chapters = ref<string[]>([])
const selectedChapter = ref('')

// 视频设置
const videoSettings = ref<VideoSettings>({
  project_name: projectName,
  chapter_name:'',
  fade_duration:1.2,
  use_pan: true,
  pan_range: [0.5, 0.5],
  fps: 15,
  resolution:[1024,1024]
})

// 状态管理
const isGenerating = ref(false)
const videoUrl = ref('')
const errorMessage = ref('')



// 获取章节列表
// 在组件中修改视频生成处理逻辑
const handleGenerateVideo = async () => {
  try {
  
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
  max-width: 70vw;
  margin: 0 auto;
}

.section {
  margin-bottom: 24px;
}

.config-section {
  margin: 24px 0;
  padding: 20px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.video-preview {
  margin-top: 24px;
}

.video-player {
  width: 100%;
  max-width: 70vw;
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