<template>
  <div class="storyboard-process">

    <el-card class="scene-table-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('storyboardProcess.sceneList') }}</span>
        </div>
      </template>

      <!-- 设置区域 -->
      <div class="settings-container">
        <!-- 第一排：章节选择 -->
        <el-row class="settings-row">
          <el-col :span="24">
            <el-select v-model="chapterName" :placeholder="t('storyboardProcess.chapterList')" class="chapter-select"
                       @change="handleChapterChange">
              <el-option v-for="chapter in chapterList" :key="chapter.value" :label="chapter.label"
                         :value="chapter.value" />
            </el-select>
          </el-col>
        </el-row>

        <!-- 第二排：图像设置 -->
        <el-row :gutter="24" class="settings-row">
          <el-col :span="24">
            <div class="settings-group">
              <div class="settings-title">{{ t('storyboardProcess.imageSettings') }}</div>
              <el-row :gutter="12">
                <el-col :span="8">
                  <div class="input-with-label">
                    <span class="input-label">{{ t('storyboardProcess.imageWidth') }}</span>
                    <el-input-number v-model="imageSettings.width" :min="64" :max="2048" :step="64"
                                     controls-position="right" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="input-with-label">
                    <span class="input-label">{{ t('storyboardProcess.imageHeight') }}</span>
                    <el-input-number v-model="imageSettings.height" :min="64" :max="2048" :step="64"
                                     controls-position="right" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="input-with-label">
                    <span class="input-label">{{ t('storyboardProcess.imageStyle') }}</span>
                    <el-select v-model="imageSettings.style" class="style-select">
                      <el-option v-for="style in styleList" :key="style.value"
                                 :label="t(`storyboardProcess.style${style.value.charAt(0).toUpperCase() + style.value.slice(1)}`)"
                                 :value="style.value" />
                    </el-select>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>

        <!-- 第三排：音频设置 -->
        <el-row :gutter="24" class="settings-row">
          <el-col :span="24">
            <div class="settings-group">
              <div class="settings-title">{{ t('storyboardProcess.audioSettings') }}</div>
              <el-row :gutter="12">
                <el-col :span="16">
                  <div class="input-with-label">
                    <span class="input-label">{{ t('storyboardProcess.selectVoice') }}</span>
                    <el-select v-model="audioSettings.narrator" :placeholder="t('storyboardProcess.selectVoice')"
                               class="narrator-select">
                      <el-option v-for="voice in voiceList" :key="voice.value" :label="voice.label" :value="voice.value" />
                    </el-select>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="input-with-label">
                    <span class="input-label">{{ t('storyboardProcess.speakingRate') }}</span>
                    <el-input-number v-model="audioSettings.speakingRate" :min="-50" :max="50" :step="1"
                                     controls-position="right" />
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>

        <!-- 第四排：操作按钮 -->
        <el-row :gutter="24" class="settings-row">
          <el-col :span="24">
            <div class="action-buttons">
              <el-button type="primary" @click="convertSelectedPrompts(selectedRows)" :loading="loading"
                         :disabled="loading || selectedRows.length === 0">
                {{ t('storyboardProcess.convertSelectedPrompts') }}
              </el-button>
              <el-button type="primary" @click="generateSelectedImages(selectedRows)" :loading="generating"
                         :disabled="generatingAllAudio || selectedRows.length === 0">
                {{ t('storyboardProcess.generateSelectedImages') }}
              </el-button>
              <el-button type="primary" @click="generateSelectedAudio(selectedRows)" :loading="generatingAllAudio"
                         :disabled="generating || selectedRows.length === 0">
                {{ t('storyboardProcess.generateSelectedAudio') }}
              </el-button>
              <el-button type="primary" @click="handleSaveAll" :loading="saving">
                {{ t('storyboardProcess.saveAll') }}
              </el-button>
            </div>
          </el-col>
        </el-row>

        <!-- 第五排：进度显示 -->
        <el-row v-show="(generating || generatingAllAudio) && progress.taskId" :gutter="24"
                class="settings-row progress-row">
          <el-col :span="24">
            <div class="settings-group">
              <div class="settings-title">{{ t('storyboardProcess.generationProgress') }}</div>
              <div class="progress-container">
                <div class="progress-with-button">
                  <el-progress :percentage="Math.floor((progress.current / progress.total) * 100)"
                               :format="() => `${progress.current}/${progress.total}`"
                               :status="progress.status === 'error' ? 'exception' : progress.status === 'completed' ? 'success' : ''"
                               :indeterminate="progress.status === 'running' && progress.current === 0" :duration="1" />
                  <el-button type="danger" @click="stopGeneration" style="margin-left: 10px">
                    {{ t('storyboardProcess.stopGeneration') }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-table ref="tableRef" :data="currentPageData" style="width: 100%" 
                @selection-change="handleSelectionChange" @select-all="handleSelectAll" row-key="id">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="#" width="60" align="center">
          <template #default="{row}">
            {{ row.id }}
          </template>
        </el-table-column>

        <el-table-column :label="t('storyboardProcess.spanContent')" min-width="240" align="center">
          <template #default="{ row }">
            <div class="text-cell">
              <el-input v-model="row.span" type="textarea" :rows="4" :placeholder="t('storyboardProcess.spanContent')"
                        @input="handleSceneChange(row)" />
              <div class="button-group">
                <el-button type="primary" size="small" @click="generateSelectedAudio([row])"
                           :loading="generatingAudioScenes.has(row.id)" :disabled="generating || generatingAllAudio">
                  {{ t('storyboardProcess.generateAudio') }}
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="t('storyboardProcess.sceneDescription')" min-width="300" align="center">
          <template #default="{ row }">
            <div class="text-cell">
              <el-input v-model="row.scene" type="textarea" :rows="4" resize="none"
                        :placeholder="t('storyboardProcess.sceneDescription')" @input="handleSceneChange(row)" />

              <el-input v-model="row.base_scene" @input="handleSceneChange(row)">
                <template #prepend>
                  <i>{{ t('storyboardProcess.baseScene') }}</i>
                </template>
              </el-input>
              <div class=" button-group">
                <el-button v-if="row.scene" size="small" type="primary" :loading="row.translating"
                           @click="convertSelectedPrompts([row])" :disabled="loading">
                  {{ t('storyboardProcess.convertToPrompt') }}
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="t('storyboardProcess.prompt')" min-width="200" align="center">
          <template #default="{ row }">
            <div class="text-cell">
              <el-input v-model="row.prompt" type="textarea" :rows="4" :placeholder="t('storyboardProcess.prompt')"
                        @input="handleSceneChange(row)" />
              <div class="button-group">
                <el-button type="primary" size="small" @click="generateSelectedImages([row])"
                           :loading="generatingScenes.has(row.id)" :disabled="generating">
                  {{ t('storyboardProcess.generateImage') }}
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="t('storyboardProcess.image')" width="200" align="center">
          <template #default="{ row }">
            <div class="image-cell">
              <el-image v-if="row.image" :src="row.image" fit="contain" class="preview-image"
                        :preview-src-list="[row.image]" :initial-index="0" preview-teleported>
                <template #error>
                  <div class="no-image">
                    {{ t('common.loadError') }}
                  </div>
                </template>
              </el-image>
              <div v-else class="no-image">
                {{ t('common.noImage') }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column :label="t('storyboardProcess.voicing')" width="200" align="center">
          <template #default="{ row }">
            <div class="audio-cell">
              <audio v-if="row.audio" :src="row.audio" controls class="audio-player" :key="row.audio">
                <source :src="row.audio" type="audio/mpeg">
                {{ t('storyboardProcess.audioNotSupported') }}
              </audio>
              <div v-else class="no-audio">
                {{ t('storyboardProcess.noAudio') }}
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10]" :total="total"
                       layout="prev, pager, next" @size-change="handleSizeChange"
                       @current-change="handleCurrentChange" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElTable } from 'element-plus'
import { chapterApi } from '@/api/chapter_api'
import { mediaApi } from '@/api/media_api'
import { getResourcePath } from '@/utils/resourcePath'
import voices from '@/utils/voices'

interface ImageSettings {
  width: number
  height: number
  style: string
}

interface AudioSettings {
  narrator: string
  speakingRate: number
}

interface Scene {
  id: number    // 添加序号字段
  span: string
  base_scene:string
  scene: string
  prompt: string
  translating: boolean
  modified: boolean
  image: string
  audio: string  
  generatingAudio?: boolean  // 用于控制音频生成按钮的状态
}

const route = useRoute()
const { t } = useI18n()
const projectName = computed(() => route.params.name as string)

// 章节列表相关
const chapterList = ref<{ label: string; value: string }[]>([])
const chapterName = ref('')

// 图像设置
const imageSettings = ref<ImageSettings>({
  width: 512,
  height: 512,
  style: 'realistic'
})

// 音频设置
const audioSettings = ref<AudioSettings>({
  narrator: '',
  speakingRate: 0
})

// 画风列表
const styleList = ref([
  { label: '写实风格', value: 'realistic' },
  { label: '动漫风格', value: 'anime' },
  { label: '油画风格', value: 'oil-painting' }
])

// 音频设置
const voiceList = ref([
])

// 获取章节列表
const fetchChapterList = async () => {
  try {
    const data = await chapterApi.getChapterList(projectName.value)
    if (data) {
      chapterList.value = data.map((chapter: string) => ({
        label: chapter,
        value: chapter
      }))
      // 如果有章节，默认选择第一个
      if (chapterList.value.length > 0) {
        chapterName.value = chapterList.value[0].value
        fetchSceneList() // 获取第一个章节的场景列表
      }
    }
  } catch (error) {
    console.error('Failed to fetch chapter list:', error)
  }
}

// 监听章节变化
const handleChapterChange = () => {
  selectedRows.value = [] // 清空选中状态
  isAllSelected.value = false // 重置全选状态
  fetchSceneList() // 当选择的章节改变时，重新获取场景列表
}

// 进度设置
const progress = ref({
  current: 0,
  total: 0,
  status: '',
  taskId: '',
  errors: [] as string[]
})




const generating = ref(false)  // 用于生成所有图片按钮的loading状态
const generatingAllAudio = ref(false)  // 用于生成所有音频按钮的loading状态
const generatingScenes = ref(new Set<number>())  // 用于记录正在生成图片的单个场景
const generatingAudioScenes = ref(new Set<number>())  // 用于记录正在生成音频的单个场景

// 重置进度
const resetProgress = () => {
  // 清理定时器
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  
  // 重置进度状态
  progress.value = {
    current: 0,
    total: 0,
    status: '',
    taskId: '',
    errors: []
  }
  
  // 重置生成状态
  generating.value = false
  generatingScenes.value.clear()
  generatingAllAudio.value = false  // 重置生成所有音频按钮的状态
}

// 检查生成进度
const checkGenerationProgress = async () => {
  if (!progress.value.taskId || (!generating.value && !generatingAllAudio.value)) {
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    return
  }
  
  try {
    const response = await mediaApi.getProgress(progress.value.taskId)
    const { status, current, total, errors } = response

    if (current > progress.value.current) {//每完成一个，就更新一个
      // 如果是音频生成任务，更新音频路径
        if (generatingAllAudio.value) {
         
          generatingAudioScenes.value.forEach((sceneId) => {
            const scene = sceneList.value.find(s => s.id === sceneId)
            scene.audio=getResourcePath(projectName.value, chapterName.value, scene.id, 'audio')

          })
        }

        if (generating.value) {//生成的图片任务，更新图片路径
          generatingScenes.value.forEach((sceneId) => {
            const scene = sceneList.value.find(s => s.id === sceneId)
            scene.image=getResourcePath(projectName.value, chapterName.value, scene.id, 'image')

          })
        }
    }
    
    progress.value.current = current
    progress.value.total = total
    progress.value.status = status
    progress.value.errors = errors || []

    
    
    if (status === 'completed' || status === 'error' || status === 'cancelled' || status === 'not_found') {
      if (progressTimer) {
        clearInterval(progressTimer)
        progressTimer = null
      }

      
      
      if (status === 'completed') {
        progress.value.current = progress.value.total
        await new Promise(resolve => setTimeout(resolve, 300))
        
        
        
      }
      
      if (generating.value) {
        generating.value = false
        generatingScenes.value.clear()
      }
      if (generatingAllAudio.value) {
        generatingAllAudio.value = false
        generatingAudioScenes.value.clear()
      }
      
      if (status === 'completed') {
        ElMessage.success(t('common.success'))
      } else if (status === 'cancelled') {
        ElMessage.info(t('storyboardProcess.generationCancelled'))
      } else if (status === 'error') {
        ElMessage.error(errors?.join('\n') || t('common.error'))
      }
      
      resetProgress()
    }
  } catch (error) {
    console.error('Failed to check generation progress:', error)
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    generating.value = false
    generatingAllAudio.value = false
    generatingScenes.value.clear()
    generatingAudioScenes.value.clear()
    ElMessage.error(t('common.error'))
    resetProgress()
  }
}


// 添加选中行的状态
const selectedRows = ref<Scene[]>([])
const isAllSelected = ref(false)  // 用于跟踪是否全选

// 全选状态的计算属性
const allChecked = computed({
  get() {
    return isAllSelected.value
  },
  set(newValue) {
    isAllSelected.value = newValue
    if (newValue) {
      // 全选时，将所有数据添加到选中列表
      selectedRows.value = [...sceneList.value]
    } else {
      // 取消全选时，清空选中列表
      selectedRows.value = []
    }
    // 更新当前页的选中状态
    nextTick(() => {
      currentPageData.value.forEach(row => {
        tableRef.value?.toggleRowSelection(row, newValue)
      })
    })
  }
})

// 处理全选
const handleSelectAll = (selection: Scene[]) => {
  // 判断是全选还是取消全选
  const isSelectAll = selection.length === currentPageData.value.length
  allChecked.value = isSelectAll
}

// 处理选择变化
const handleSelectionChange = (selection: Scene[]) => {
  if (!isAllSelected.value) {
    // 如果不是全选状态，正常更新选中行
    selectedRows.value = selection
  }
}

// 页码改变
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 恢复选中状态
  nextTick(() => {
    if (isAllSelected.value) {
      // 如果是全选状态，选中当前页所有行
      currentPageData.value.forEach(row => {
        tableRef.value?.toggleRowSelection(row, true)
      })
    } else {
      // 否则，只选中已选中的行
      currentPageData.value.forEach(row => {
        const isSelected = selectedRows.value.some(selected => selected.id === row.id)
        tableRef.value?.toggleRowSelection(row, isSelected)
      })
    }
  })
}

// 每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

// 批量操作方法
const convertSelectedPrompts = async (selectedRows:Scene[]) => {
  try {
    if (selectedRows.length === 0) {
      ElMessage.warning(t('storyboardProcess.noSelection'))
      return
    }
  
    loading.value = true
    
    const scenesToConvert = selectedRows.filter(row => row.scene)
    if (scenesToConvert.length === 0) {
      return
    }

    // 获取所有需要转换的场景描述
    const descriptions = scenesToConvert.map(row =>row.base_scene+","+row.scene)
    scenesToConvert.forEach(row => {
      row.translating = true//设置为正在转换
    })
    // 批量转换
    const results = await chapterApi.translatePrompt(projectName.value, descriptions)
    
    // 更新场景的提示词
    scenesToConvert.forEach((row:Scene, index) => {
      row.prompt = results[index]
      row.modified = true
      row.translating = false//设置为转换完成
    })
    
    ElMessage.success(t('common.success'))
  } catch (error) {
    ElMessage.error(t('common.error'))
    console.error('批量转换提示词失败:', error)
  } finally {
    loading.value = false
  }
}

// 生成图片
const generateSelectedImages = async (selectedRows:Scene[]) => {
  if (selectedRows.length === 0) {
    ElMessage.warning(t('storyboardProcess.noSelection'))
    return
  }

  const scenes = selectedRows.filter(scene => scene.prompt)
  if (scenes.length === 0) {
    ElMessage.warning(t('storyboardProcess.noPrompts'))
    return
  }

  if (generating.value) {
    ElMessage.warning(t('storyboardProcess.generationInProgress'))
    return
  }

  try {
    generating.value = true
    // 将选中的场景添加到生成集合中
    scenes.forEach(scene => generatingScenes.value.add(scene.id))
    
    const params = {
      project_name: projectName.value,
      chapter_name: chapterName.value,
      imageSettings: imageSettings.value,
      prompts: scenes.map(scene => ({
        id: scene.id,
        prompt: scene.prompt
      }))
    }
    
    const data = await mediaApi.generateImages(params)
    progress.value.taskId = data.task_id
    progress.value.total = data.total
    progress.value.current = 0
    progress.value.status = data.status
    progress.value.errors = data.errors || []
    
    // 开始定时检查进度
    if (progressTimer) clearInterval(progressTimer)
    progressTimer = setInterval(checkGenerationProgress, 1000)
    
  } catch (error) {

    ElMessage.error(t('common.operationFailed'))
    generating.value = false
    generatingScenes.value.clear()
    resetProgress()
  }
}

// 生成音频
const generateSelectedAudio = async (selectedRows:Scene[]) => {
  if (selectedRows.length === 0) {
    ElMessage.warning(t('storyboardProcess.noSelection'))
    return
  }

  const scenes = selectedRows.filter(scene => scene.span)
  if (scenes.length === 0) {
    ElMessage.warning(t('storyboardProcess.noContent'))
    return
  }

  try {
    generatingAllAudio.value = true
    const params = {
      project_name: projectName.value,
      chapter_name: chapterName.value,
      audioSettings: {
        voice: audioSettings.value.narrator,
        rate: `${audioSettings.value.speakingRate}%`
      },
      prompts: scenes.map(scene => ({
        id: scene.id,
        prompt: scene.span
      }))
    }
    scenes.forEach(scene => generatingAudioScenes.value.add(scene.id))
    const data = await mediaApi.generateAudio(params)
    progress.value.taskId = data.task_id
    progress.value.total = data.total
    progress.value.current = 0
    progress.value.status = data.status
    progress.value.errors = data.errors || []
    
    // 开始定时检查进度
    if (progressTimer) clearInterval(progressTimer)
    progressTimer = setInterval(checkGenerationProgress, 1000)
    
  } catch (error) {
    console.error('Failed to generate all audio:', error)
    ElMessage.error(t('common.operationFailed'))
    generatingAllAudio.value = false
    resetProgress()
  }
}


const stopGeneration = async () => {
  try {
    if (!progress.value.taskId) {
      ElMessage.info(t('storyboardProcess.noTaskToStop'))
      return
    }

    await mediaApi.cancelTask(progress.value.taskId)
    

    // 根据任务ID判断是音频还是图片任务
    const isAudioTask = progress.value.taskId.startsWith('audio_')
    
    // 重置相关状态
    if (isAudioTask) {
      // 重置所有场景的音频生成状态
      sceneList.value.forEach(scene => {
        if (scene.generatingAudio) {
          scene.generatingAudio = false
        }
      })
      generatingAllAudio.value = false
    } else {
      // 重置图片生成状态
      generatingScenes.value.clear()
    }

    resetProgress()
    generating.value = false
    ElMessage.success(t('storyboardProcess.stopGenerationSuccess'))
  } catch (error) {
    console.error('Failed to stop generation:', error)
    ElMessage.error(t('common.error'))
  }
}

const loading = ref(false)
const sceneList = ref<Scene[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 当前页的数据
const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sceneList.value.slice(start, end)
})

// 更新分页信息
const updatePagination = () => {
  total.value = sceneList.value.length
  currentPage.value = 1 // 重置到第一页
}

// 获取场景列表
const fetchSceneList = async () => {
  if (!chapterName.value) return
  
  loading.value = true
  try {
    const data = await chapterApi.getChapterSceneList(projectName.value, chapterName.value)
    
    if (data) {
      sceneList.value = data.map((scene: any) => ({
        id: scene.id,
        base_scene:scene.base_scene,
        scene: scene.scene,
        span: scene.content,
        prompt: scene.prompt,
        image: getResourcePath(projectName.value, chapterName.value, scene.id, 'image'),
        audio: getResourcePath(projectName.value, chapterName.value, scene.id, 'audio'),
        translating: false,
        modified: false,
        generatingAudio: false
      }))
      console.log('Scene list with audio paths:', sceneList.value)
      updatePagination()
    }
  } catch (error) {
    console.error('Failed to fetch scene list:', error)
  } finally {
    loading.value = false
  }
}

// 处理场景内容变化
const handleSceneChange = (row: Scene) => {
  console.log('Scene changed:', row)
  row.modified = true
}

// 转换为提示词
// const handleTranslatePrompt = async (row: Scene) => {
//   try {
//     row.translating = true

//     const prompt = await chapterApi.translatePrompt(projectName.value, [row.base_scene+","+row.scene])
//     row.prompt = prompt[0]
//     row.modified = true
//     ElMessage.success('转换成功')
//   } catch (error: any) {
//     ElMessage.error(error.message || '转换失败')
//     console.error('转换提示词失败:', error)
//   } finally {
//     row.translating = false
//   }
// }

// 保存所有修改
const handleSaveAll = async () => {
  try {
    saving.value = true
    // 过滤出被修改的场景
    const modifiedScenes = sceneList.value.filter(scene => scene.modified)
    if (modifiedScenes.length === 0) {
      ElMessage.info(t('common.noDataToProcess'))
      return
    }

    // 调用保存接口
    await chapterApi.saveScenes(projectName.value, chapterName.value, modifiedScenes)
    
    // 重置修改标记
    modifiedScenes.forEach(scene => {
      scene.modified = false
    })
    
    ElMessage.success(t('common.success'))
  } catch (error: any) {
    ElMessage.error(error.message || t('common.error'))
  } finally {
    saving.value = false
  }
}


const saving = ref(false)

// 定时器
let progressTimer: ReturnType<typeof setInterval> | null = null

// 添加表格引用
const tableRef = ref<InstanceType<typeof ElTable>>()

onMounted(() => {
  console.log(projectName.value)
  for(const voice in voices){
    voiceList.value.push({ label: voice+" - "+voices[voice], value: voice })
  }
  audioSettings.value.narrator=voiceList.value[0].value
  fetchChapterList() // 组件加载时获取章节列表
})

onBeforeUnmount(() => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
})
</script>

<style lang="scss" scoped>
.storyboard-process {
  padding: 20px;
  
  .scene-table-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .settings-container {
    .settings-row {
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .settings-group {
        background-color: var(--el-fill-color-light);
        border-radius: 4px;
        padding: 16px;
        
        .settings-title {
          font-size: 14px;
          color: var(--el-text-color-primary);
          margin-bottom: 16px;
          font-weight: bold;
        }
        
        .input-with-label {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .input-label {
            white-space: nowrap;
            color: var(--el-text-color-regular);
          }
          
          .el-input-number {
            width: 120px;
          }
          
          .style-select,
          .narrator-select {
            width: 100%;
          }
        }
      }
      
      &.progress-row {
        .progress-container {
          .progress-with-button {
            display: flex;
            align-items: center;
            
            .el-progress {
              flex: 1;
            }
            
            .el-button {
              flex-shrink: 0;
            }
          }
        }
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
  }
  
  .text-cell {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .button-group {
      display: flex;
      justify-content: center;
      gap: 8px;

      .el-button {
        width: 120px;  /* 添加固定宽度 */
      }
    }
  }
  
  .el-pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
  
  .chapter-select {
    width: 100%;
  }
}

.audio-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50px;
  
  .audio-player {
    width: 100%;
    max-width: 180px;
  }
  
  .no-audio {
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }
}
</style>
