
import { VideoSettings } from '@/types/video'
import request from './request'


export const videoApi = {
  // 生成视频
  generateVideo(
    data: VideoSettings  // 请求体
  ) {
    return request({
      url: 'video/generate_video',
      method: 'post',
        data:  data    // 请求体
    })
  },

}