import config from '@/config'

/**
 * 生成资源访问路径
 * @param projectName 项目名称
 * @param chapterName 章节名称
 * @param spanIndex span索引
 * @param type 资源类型 ('image' | 'audio')
 * @returns 完整的资源访问路径
 */
export const getResourcePath = (
  projectName: string,
  chapterName: string,
  spanId: number,
  type: 'image' | 'audio' = 'image'
): string => {
  const timestamp = Date.now()
  const endpoint = type === 'image' ? 'media/get_image' : 'media/get_audio'
  return `${config.baseApi}${endpoint}?project_name=${projectName}&chapter_name=${chapterName}&span_id=${spanId}&_t=${timestamp}`
}
