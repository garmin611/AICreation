<template>
  <div class="not-found">
    <el-result
      icon="error"
      :title="t('notFound.title')"
      :sub-title="t('notFound.subTitle')"
    >
      <template #extra>
        <el-button type="primary" @click="router.push('/')">{{ t('common.backToHome') }}</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
</script>

<style scoped>
.not-found {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
</style>
