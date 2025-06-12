import request from './request'

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
    return request.get<string[]>('/chapter/list', { project_name: projectName })
  },

  // 获取章节内容
  getChapterContent(projectName: string, chapterName: string) {
    return request.get<ChapterContent>('/chapter/content', {
      project_name: projectName,
      chapter_name: chapterName
    })
  },

  // 生成章节内容
  generateChapter(params: GenerateChapterParams & { signal?: AbortSignal }) {
    return request.stream('/chapter/generate', params, {
      signal: params.signal
    })
  },

  // 保存章节内容
  saveChapterContent(params: SaveChapterParams) {
    return request.post('/chapter/save', params)
  },

  // 创建新章节
  createChapter(projectName: string) {
    return request.post<ChapterResponse>('/chapter/create', { project_name: projectName })
  },

  /**
   * 分割章节内容并生成提示词
   */
  splitChapter(projectName: string, chapterName: string) {
    return request.post('/chapter/split_text', {
      project_name: projectName,
      chapter_name: chapterName
    })
  },

  // 提取章节中的角色
  extractCharacters(projectName: string, chapterName: string) {
    return request.post('/chapter/extract_characters', {
      project_name: projectName,
      chapter_name: chapterName
    }, { raw: true })
  },

  /**
   * 获取章节场景列表
   */
  getChapterSceneList(projectName: string, chapterName: string) {
    return request.get('/chapter/scene_list', {
      project_name: projectName,
      chapter_name: chapterName
    })
  },

  // 保存场景修改
  saveScenes(projectName: string, chapterName: string, scenes: any[]) {
    return request.post('/chapter/save_scenes', {
      project_name: projectName,
      chapter_name: chapterName,
      scenes
    })
  },

  translatePrompt(projectName: string, prompts: string[]) {
    return request.post<string[]>('/chapter/translate_prompt', {
      project_name: projectName,
      prompts
    })
  },

  // 导入小说
  importNovel(formData: FormData) {
    return request.post('/chapter/import_novel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

