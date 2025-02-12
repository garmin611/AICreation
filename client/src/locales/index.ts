import { createI18n } from 'vue-i18n'
import enUS from './en-US'
import zhCN from './zh-CN'

export type Language = 'zh-CN' | 'en-US'

const messages = {
  'en-US': enUS,
  'zh-CN': zhCN
}

export const LOCALES = [
  {
    name: '中文',
    value: 'zh-CN' as Language
  },
  {
    name: 'English',
    value: 'en-US' as Language
  }
]

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages
})

export default i18n
