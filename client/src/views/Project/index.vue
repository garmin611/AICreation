# 将原有的Project.vue内容复制到这里
<template>
  <div class="project-container">
    <el-row :gutter="20">
      <!-- 项目卡片列表 -->
      <el-col v-for="project in projects" :key="project" :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
        <el-card class="project-card" shadow="hover">
          <div class="project-content" @click="handleCardClick(project)">
            <h3>{{ project }}</h3>
          </div>
          <template #footer>
            <div class="project-actions">
              <el-button type="primary" size="small" @click.stop="handleEdit(project)">
                <el-icon><Edit /></el-icon>
                {{ t('project.edit') }}
              </el-button>
              <el-button type="danger" size="small" @click.stop="handleDelete(project)">
                <el-icon><Delete /></el-icon>
                {{ t('project.delete') }}
              </el-button>
            </div>
          </template>
        </el-card>
      </el-col>

      <!-- 新增项目卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
        <el-card class="project-card add-project-card" shadow="hover" @click="showCreateDialog">
          <div class="add-project-content">
            <el-icon :size="40"><Plus /></el-icon>
            <span>{{ t('project.create') }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="t('project.createTitle')"
      width="30%"
      :close-on-click-modal="false"
      @keydown.enter="handleCreate"
      @close="createForm.projectName = ''"
    >
      <el-form :model="createForm" :rules="rules" ref="createFormRef">
        <el-form-item :label="t('project.name')" prop="projectName">
          <el-input v-model="createForm.projectName" :placeholder="t('project.namePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="handleCreate" :loading="creating">
            {{ t('common.confirm') }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑项目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="t('project.editTitle')"
      width="30%"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="rules" ref="editFormRef">
        <el-form-item :label="t('project.name')" prop="projectName">
          <el-input v-model="editForm.projectName" :placeholder="t('project.namePlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="handleEditSubmit" :loading="editing">
            {{ t('common.confirm') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, Plus } from '@element-plus/icons-vue'
import projectApi from '@/api/project_api'
import type { FormInstance } from 'element-plus'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()

// 数据
const projects = ref<string[]>([])
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const creating = ref(false)
const editing = ref(false)
const createForm = ref({
  projectName: ''
})
const editForm = ref({
  projectName: '',
  oldName: ''
})

// 表单规则
const rules = {
  projectName: [
    { required: true, message: t('project.nameRequired'), trigger: 'blur' },
    { min: 2, max: 50, message: t('project.nameLength'), trigger: 'blur' }
  ]
}

const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 获取项目列表
const fetchProjects = async () => {
  try {
    const data = await projectApi.getProjectList()
    console.log(data)
    projects.value = data
  } catch (error) {
    ElMessage.error(t('project.fetchError'))
  }
}

// 创建项目
const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        creating.value = true
        await projectApi.createProject(createForm.value.projectName)
        ElMessage.success(t('project.createSuccess'))
        createDialogVisible.value = false
        createForm.value.projectName = ''
        await fetchProjects()
      } catch (error) {
        ElMessage.error(t('project.createError'))
      } finally {
        creating.value = false
      }
    }
  })
}

// 显示创建对话框
const showCreateDialog = () => {
  createDialogVisible.value = true
}

// 编辑项目
const handleEdit = (projectName: string) => {
  editForm.value.projectName = projectName
  editForm.value.oldName = projectName
  editDialogVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        editing.value = true
        await projectApi.updateProject(editForm.value.oldName, editForm.value.projectName)
        ElMessage.success(t('project.editSuccess'))
        editDialogVisible.value = false
        await fetchProjects()
      } catch (error) {
        ElMessage.error(t('project.editError'))
      } finally {
        editing.value = false
      }
    }
  })
}

// 处理卡片点击
const handleCardClick = (projectName: string) => {
  router.push(`/project/${projectName}`)
}

// 删除项目
const handleDelete = (projectName: string) => {
  ElMessageBox.confirm(
    t('project.deleteConfirm'),
    t('common.warning'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(async () => {
    try {
      await projectApi.deleteProject(projectName)
      ElMessage.success(t('project.deleteSuccess'))
      await fetchProjects()
    } catch (error) {
      ElMessage.error(t('project.deleteError'))
    }
  })
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.project-container {
  padding: 20px 5vw;
  width: 100%;
}

.project-card {
  margin-bottom: 20px;
  height: 180px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.3s;
}

.project-card:hover {
  transform: translateY(-5px);
}

/* 确保卡片内容不会挤压footer */
:deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 15px;
  min-height: 0; /* 允许内容区域收缩 */
}

/* 固定footer高度和样式 */
:deep(.el-card__footer) {
  padding: 12px;
  height: 52px; /* 固定footer高度 */
  box-sizing: border-box;
  flex-shrink: 0; /* 防止footer被压缩 */
}

.project-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.project-content h3 {
  margin: 0;
  text-align: center;
  word-break: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3; /* 最多显示3行 */
  -webkit-box-orient: vertical;
  font-size: 14px;
  line-height: 1.5;
}

.project-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.add-project-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
