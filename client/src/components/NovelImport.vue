<template>
  <div class="novel-import">
    <el-card class="import-card">
      <template #header>
        <div class="card-header">
          <span>导入小说</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="章节匹配模式">
          <el-input v-model="form.chapterPattern" placeholder="例如：第[零一二三四五六七八九十百千万\\d]+章.*?\\n">
            <template #append>
              <el-tooltip content="使用正则表达式匹配章节标题，默认为：第[零一二三四五六七八九十百千万\\d]+章.*?\\n">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="选择文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".txt"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传txt格式的小说文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleImport" :loading="loading">
            开始导入
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, QuestionFilled } from '@element-plus/icons-vue'
import { chapterApi } from '@/api/chapter_api'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(false)
const form = reactive({
  chapterPattern: '',
  file: null as File | null
})

const handleFileChange = (file: any) => {
  form.file = file.raw
}

const handleImport = async () => {
  const projectName = route.params.name as string
  
  if (!projectName) {
    ElMessage.error('无法获取项目名称')
    return
  }
  
  if (!form.file) {
    ElMessage.error('请选择要上传的文件')
    return
  }
  
  loading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', form.file)
    formData.append('project_name', projectName)
    if (form.chapterPattern) {
      formData.append('chapter_pattern', form.chapterPattern)
    }
    
    const response = await chapterApi.importNovel(formData)
    
    if (response.status === 'success') {
      ElMessage.success(`导入成功，共导入 ${response.data.total_chapters} 个章节`)
      form.file = null
      form.chapterPattern = ''
      emit('import-success')
    } else {
      ElMessage.error(response.msg || '导入失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    loading.value = false
  }
}

const emit = defineEmits(['import-success'])
</script>

<style scoped>
.novel-import {
  max-width: 800px;
  margin: 20px auto;
}

.import-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 7px;
}
</style> 