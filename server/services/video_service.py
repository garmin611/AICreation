import logging
import os
from moviepy.editor import *
from moviepy.video.fx.all import resize
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from .base_service import SingletonService

logger = logging.getLogger(__name__)

class VideoService(SingletonService):
    """视频生成服务（单例）"""
    
    def _initialize(self):
        """初始化默认视频配置"""
        self.default_settings = {
            'zoom_factor': 1.04,
            'pan_intensity': 20,
            'font_name': 'Arial-Unicode-ms',
            'font_size': 24,
            'resolution': (1920, 1080)
        }
        logger.info("VideoService initialized with default settings")

    async def generate_video_async(self, chapter_path, video_settings=None):
        """异步生成视频"""
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                self.generate_video,
                chapter_path,
                video_settings
            )
            return future.result()

    def generate_video(self, chapter_path, video_settings=None):
        """生成视频主方法（支持多线程）"""
        settings = {**self.default_settings, **(video_settings or {})}
        
        try:
            clips = []
            # 遍历排序后的子文件夹
            subdirs = sorted([
                d for d in os.listdir(chapter_path) 
                if os.path.isdir(os.path.join(chapter_path, d))
            ], key=lambda x: int(x))  # 按数字顺序排序

            # 使用线程池并行处理每个子文件夹
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self._create_clip, os.path.join(chapter_path, subdir), settings)
                    for subdir in subdirs
                ]
                clips = [future.result() for future in futures]

            # 合并视频片段
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # 输出路径
            output_path = os.path.join(chapter_path, "video.mp4")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                threads=4,
                preset='slow',
                ffmpeg_params=['-crf', '20']
            )
            return output_path
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise

    def _create_clip(self, subdir_path, settings):
        """创建单个视频片段"""
        # 加载资源文件
        resources = {
            'image': os.path.join(subdir_path, "image.png"),
            'audio': os.path.join(subdir_path, "audio.mp3"),
            'text': self._read_text(subdir_path)
        }

        # 验证文件存在
        for typ, path in resources.items():
            if typ == 'text': continue
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing {typ} file: {path}")

        # 创建带效果的片段
        audio_clip = AudioFileClip(resources['audio'])
        duration = audio_clip.duration
        audio_clip.close()

        # 基础剪辑
        img_clip = ImageClip(resources['image']).set_duration(duration)
        img_clip = resize(img_clip, newsize=settings['resolution'])

        # 应用动态效果
        final_clip = self._apply_effects(img_clip, duration, settings)
        
        # 添加字幕
        txt_clip = TextClip(
            resources['text'],
            font=settings['font_name'],
            fontsize=settings['font_size'],
            color='white',
            bg_color='rgba(0,0,0,0.3)',
            size=(img_clip.w * 0.9, None)
        ).set_position(('center', 'bottom')).set_duration(duration)
        
        # 合成最终片段
        return CompositeVideoClip([final_clip, txt_clip]).set_audio(audio_clip)

    def _apply_effects(self, clip, duration, settings):
        """应用动态效果"""
        # 缩放效果
        def zoom_effect(t):
            if t < duration/3:
                return 1 + (settings['zoom_factor']-1)*(t/(duration/3))
            return settings['zoom_factor'] - (settings['zoom_factor']-1)*((t-duration/3)/(2*duration/3))
        
        # 平移效果
        def pan_effect(get_frame, t):
            img = get_frame(t)
            offset = int(settings['pan_intensity'] * abs(np.sin(0.5*t)))
            return img[:, offset:offset+img.shape[1]-40]
        
        return clip.resize(lambda t: zoom_effect(t)).fl(pan_effect)

    def _read_text(self, subdir_path):
        """读取字幕文件"""
        text_path = os.path.join(subdir_path, "span.txt")
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read().strip()