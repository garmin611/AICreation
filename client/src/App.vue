<script setup lang="ts">
import { ref } from 'vue'
import Header from './components/Header.vue'
import { useDark, useToggle } from '@vueuse/core'

const isDark = useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: 'light',
})
const toggleDark = useToggle(isDark)

const toggleTheme = (dark: boolean) => {
  toggleDark(dark)
}
</script>

<template>
  <el-container class="app-container">
    <el-header>
      <Header @theme-change="toggleTheme" />
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
html.dark {
  color-scheme: dark;
}

.app-container {
  min-height: 100vh;
}

.el-header {
  padding: 0;
  width: 100vw;
  height: 64px;
  background-color: var(--el-bg-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.el-main {
  min-height: calc(100vh - 64px);
  width: 100%;
  padding: 0;
}
</style>
