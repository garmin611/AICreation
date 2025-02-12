import request from './request'

interface GenerateImageParams {
  project_name: string
  chapter_name: string
  imageSettings: {
    width: number
    height: number
    style: string
  }
  prompts: {
    id: number
    prompt: string
  }[]
}

interface GenerateAudioParams {
  project_name: string
  chapter_name: string
  audioSettings: {
    voice: string
    rate: string
  }
  prompts: {
    id: number
    prompt: string
  }[]
}

interface GenerationProgressResponse {
  status: string
  current: number
  total: number
  errors: string[]
}

export const mediaApi = {
  generateImages(params: GenerateImageParams) {
    return request({
      url: '/media/generate_images',
      method: 'post',
      data: params
    })
  },

  generateAudio(params: GenerateAudioParams) {
    return request({
      url: '/media/generate-audio',
      method: 'post',
      data: params
    })
  },

  getProgress(taskId: string) {
    return request<GenerationProgressResponse>({
      url: '/media/progress',
      method: 'get',
      params: { task_id: taskId }
    })
  },

  cancelTask(taskId: string) {
    return request({
      url: '/media/cancel',
      method: 'post',
      params: { task_id: taskId }
    })
  }
}

export default mediaApi
