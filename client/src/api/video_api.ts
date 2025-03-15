import { VideoSettings } from '@/types/video'
import request from './request'

export const videoApi = {
  // 生成视频
  generateVideo(data: VideoSettings) {
    return request.post('video/generate_video', data)
  }
}