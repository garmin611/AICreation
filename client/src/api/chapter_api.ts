import request, { streamRequest } from './request'

interface GenerateChapterParams {
  project_name: string
  chapter_name: string
  prompt: string
  is_continuation: boolean
  use_last_chapter: boolean
}

interface SaveChapterParams {
  project_name: string
  chapter_name: string
  content: string
}

interface ChapterContent {
  content: string
}

interface ChapterResponse {
  chapter: string
}

export const chapterApi = {
  // 获取章节列表
  getChapterList(projectName: string) {
    return request<string[]>({
      url: '/chapter/list',
      method: 'get',
      params: { project_name: projectName }
    })
  },

  // 获取章节内容
  getChapterContent(projectName: string, chapterName: string) {
    return request<ChapterContent>({
      url: '/chapter/content',
      method: 'get',
      params: {
        project_name: projectName,
        chapter_name: chapterName
      }
    })
  },

  // 生成章节内容
 generateChapter(params: GenerateChapterParams& { signal?: AbortSignal }) {
  return streamRequest({
    url: '/chapter/generate',
      method: 'post',
      data: params,
      signal: params.signal
  })
},

  // 保存章节内容
  saveChapterContent(params: SaveChapterParams) {
    return request({
      url: '/chapter/save',
      method: 'post',
      data: params
    })
  },

  // 创建新章节
  createChapter(projectName: string) {
    return request<ChapterResponse>({
      url: '/chapter/create',
      method: 'post',
      data: { project_name: projectName }
    })
  },

  /**
   * 分割章节内容并生成提示词
   */
  splitChapter(projectName: string, chapterName: string) {
    return request({
      url:'/chapter/split_text',
      method: 'post',
      data:{
        project_name: projectName,
        chapter_name: chapterName
      }
  })
  },

  // 提取章节中的角色
  extractCharacters(projectName: string, chapterName: string) {
    return request({
      url: '/chapter/extract_characters',
      method: 'post',
      data: {
        project_name: projectName,
        chapter_name: chapterName
      }
    })
  },

  /**
   * 获取章节场景列表
   */
  getChapterSceneList(projectName: string, chapterName: string) {
    return request({
      url: '/chapter/scene_list',
      method: 'get',
      params: {
        project_name: projectName,
        chapter_name: chapterName
      }
    })
  },
  // 保存场景修改
  saveScenes(projectName: string, chapterName: string, scenes: any[]){
    return request({
      url:'/chapter/save_scenes',
      method: 'post',
      data: {
        project_name: projectName,
        chapter_name: chapterName,
        scenes
      }
    })
  },
  translatePrompt(projectName: string, prompts: string[]){
    return request<string[]>({
      url:'/chapter/translate_prompt',
      method: 'post',
      data:{
      project_name: projectName,
      prompts
    }})
}
}

