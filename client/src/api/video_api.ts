import { VideoSettings } from '@/types/video'
import request from './request'

export const videoApi = {
  // 生成视频
  generateVideo(data: VideoSettings) {
    return request.post('video/generate_video', data)
  },
  
  // 获取视频生成进度
  getGenerationProgress() {
    return request.get('video/generation_progress')
  },
  
  // 取消视频生成
  cancelGeneration() {
    return request.post('video/cancel_generation')
  }
}