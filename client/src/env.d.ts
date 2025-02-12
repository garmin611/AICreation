/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vue-i18n' {
  import { DefineComponent, Plugin } from 'vue'
  
  export const createI18n: (options: any) => {
    install: (app: any) => void
    global: {
      t: (key: string) => string
      locale: {
        value: string
      }
    }
  }
  
  export const useI18n: () => {
    t: (key: string) => string
    locale: {
      value: string
    }
  }
}
