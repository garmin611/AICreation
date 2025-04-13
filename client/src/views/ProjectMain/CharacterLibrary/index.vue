<template>
  <div class="character-library">
    <h3>{{ t('menu.characterLibrary') }}</h3>
    
    <!-- 搜索框 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        :placeholder="t('common.search')"
        :prefix-icon="Search"
        clearable
      />
    </div>

    <el-table
      v-loading="loading"
      :data="filteredCharacters"
      style="width: 100%"
      border
    >
      <el-table-column
        :label="t('entity.entityName')"
        prop="name"
        width="120"
        align="center"
      >
        <template #default="{ row }">
          <span class="entity-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column
        :label="t('entity.role')"
        width="150"
        align="center"
      >
        <template #default="{ row }">
          <el-input
            v-model="row.attributes.role"
            type="textarea"
            :rows="2"
            :placeholder="t('entity.role')"
            :disabled="isLocked(row.name)"
          />
        </template>
      </el-table-column>
      <el-table-column
        :label="t('entity.description')"
        min-width="240"
        align="center"
      >
        <template #default="{ row }">
          <el-input
            v-model="row.attributes.description"
            type="textarea"
            :rows="5"
            :placeholder="t('entity.description')"
            :disabled="isLocked(row.name)"
          />
        </template>
      </el-table-column>
      <el-table-column
        :label="t('common.operations')"
        width="360"
        align="center"
      >
        <template #default="{ row }">
          <div class="operation-buttons">
            <div class="button-row">
              <el-button
                :type="isLocked(row.name) ? 'warning' : 'primary'"
                @click="handleLockClick(row)"
              >
                {{ isLocked(row.name) ? t('entity.unlockPrompt') : t('entity.lockPrompt') }}
              </el-button>
              <!-- 暂时不实现反推功能 -->
              <!-- <el-button
                type="info"
                :disabled="isLocked(row.name)"
                @click="openReversePrompt(row)"
              >
                {{ t('entity.reversePrompt') }}
              </el-button> -->
            </div>
            <div class="button-row">
              <el-button
                type="success"
                :disabled="isLocked(row.name)"
                @click="savePrompt(row)"
              >
                {{ t('entity.savePrompt') }}
              </el-button>
              <el-button
                type="danger"
                :disabled="isLocked(row.name)"
                @click="deleteEntity(row)"
              >
                {{ t('entity.delete') }}
              </el-button>
            </div>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 反推提示词对话框 -->
    <el-dialog
      v-model="reversePromptVisible"
      :title="t('entity.reversePromptTitle')"
      width="600px"
    >
      <div class="reverse-prompt-dialog">
        <!-- 上传图片区域 -->
        <el-upload
          class="upload-area"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleImageChange"
        >
          <div class="upload-content">
            <el-icon class="upload-icon"><Upload /></el-icon>
            <div class="upload-text">{{ t('entity.uploadImage') }}</div>
            <img v-if="selectedImage" :src="selectedImage" class="preview-image" />
          </div>
        </el-upload>

        <!-- 文本显示区域 -->
        <div class="description-area">
          {{ reversePromptText }}
        </div>

        <!-- 按钮区域 -->
        <div class="dialog-footer">
          <el-button @click="reversePromptVisible = false">
            {{ t('entity.cancel') }}
          </el-button>
          <el-button type="primary" @click="confirmReversePrompt">
            {{ t('entity.confirm') }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import {  Search, Upload } from '@element-plus/icons-vue'
import { entityApi } from '@/api/entity_api'

const route = useRoute()
const { t } = useI18n()
const projectName = computed(() => route.params.name as string)

interface Character {
  name: string
  attributes: {
    role?: string
    description?: string
    [key: string]: any
  }
}

const loading = ref(false)
const characters = ref<Character[]>([])
const searchQuery = ref('')
const lockedEntities = ref<string[]>([])
const reversePromptVisible = ref(false)
const reversePromptText = ref('')
const selectedImage = ref('')
const currentCharacter = ref<Character | null>(null)

// 根据搜索词过滤角色列表
const filteredCharacters = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return characters.value
  
  return characters.value.filter(character => 
    character.name.toLowerCase().includes(query)
  )
})

const isLocked = (name: string) => {
  return lockedEntities.value.includes(name)
}

const fetchCharacters = async () => {
  loading.value = true
  try {
    const data = await entityApi.getCharacterList(projectName.value)
    console.log(data)
    characters.value = data.characters
    lockedEntities.value = data.locked_entities
  } catch (error) {
    ElMessage.error(String(error))
  } finally {
    loading.value = false
  }
}

const handleLockClick = async (row: Character) => {
  if (!isLocked(row.name)) {
    ElMessageBox.confirm(
      t('entity.lockConfirmContent'),
      t('entity.lockConfirmTitle'),
      {
        confirmButtonText: t('entity.confirm'),
        cancelButtonText: t('entity.cancel'),
        type: 'warning',
      }
    )
      .then(() => {
        toggleLock(row)
      })
      .catch(() => {
        // 用户取消操作
      })
  } else {
    // 解锁不需要确认
    toggleLock(row)
  }
}

const toggleLock = async (row: Character) => {
  try {
    const response = await entityApi.toggleLock(projectName.value, row.name)
    if (response.is_locked) {
      ElMessage.success(t('entity.lockSuccess'))
      if (!lockedEntities.value.includes(row.name)) {
        lockedEntities.value.push(row.name)
      }
    } else {
      ElMessage.success(t('entity.unlockSuccess'))
      lockedEntities.value = lockedEntities.value.filter(name => name !== row.name)
    }
  } catch (error) {
    ElMessage.error(t('entity.operationFailed'))
  }
}

const openReversePrompt = (row: Character) => {
  currentCharacter.value = row
  reversePromptText.value = ''
  selectedImage.value = ''
  reversePromptVisible.value = true
}

const handleImageChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    selectedImage.value = URL.createObjectURL(uploadFile.raw)
  }
}

const confirmReversePrompt = () => {
  if (currentCharacter.value && reversePromptText.value) {
    currentCharacter.value.attributes.description = reversePromptText.value
    reversePromptVisible.value = false
    // 自动保存更新后的描述
    savePrompt(currentCharacter.value)
  }
}

const savePrompt = async (row: Character) => {
  try {
    const data = await entityApi.updateCharacter(projectName.value, {
      name: row.name,
      attributes: row.attributes
    })
    if(data)
      ElMessage.success(t('entity.updateSuccess'))
  } catch (error) {
    ElMessage.error(String(error))
  }
}

const deleteEntity = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      t('entity.deleteConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('entity.confirm'),
        cancelButtonText: t('entity.cancel'),
        type: 'warning',
      }
    )
    
    const res = await entityApi.deleteCharacter(projectName.value, row.name)
    if (res) {
      ElMessage.success(t('entity.deleteSuccess'))
      await fetchCharacters()
    } else {
      ElMessage.error(res.data.message || t('entity.deleteError'))
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('entity.operationFailed'))
    }
  }
}

onMounted(() => {
  fetchCharacters()
})
</script>

<style scoped>
.character-library {
  padding: 20px;
}

.search-container {
  margin-bottom: 20px;
  max-width: 300px;
}

.operation-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.button-row {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.button-row .el-button {
  flex: 1;
  min-width: 110px;
}

.entity-name {
  display: inline-block;
  line-height: 40px;
  height: 40px;
}

.is-locked {
  background-color: #909399;
  border-color: #909399;
}

.is-locked:hover {
  background-color: #a6a9ad;
  border-color: #a6a9ad;
}

.reverse-prompt-dialog {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-area {
  width: 100%;
  height: 200px;
  border: 2px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.upload-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--el-text-color-secondary);
}

.upload-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
}

.preview-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.description-area {
  min-height: 100px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

:deep(.el-table__cell) {
  padding: 8px 0;
}

:deep(.el-table .cell) {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

:deep(.el-table__header .cell) {
  font-weight: bold;
}
</style>
@/api/entity_api