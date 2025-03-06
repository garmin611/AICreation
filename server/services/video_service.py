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


            # 检查每个片段是否有效
            for clip in clips:
                if clip is None:
                    raise ValueError("One of the video clips is None")
                if not hasattr(clip, 'get_frame'):
                    raise ValueError(f"Invalid clip object: {clip}")

            # 合并视频片段
            final_clip = concatenate_videoclips(clips, method="compose")
            if final_clip is None or not hasattr(final_clip, 'get_frame'):
                raise ValueError("Failed to concatenate clips: final_clip is invalid")



            # 输出路径
            output_path = os.path.join(chapter_path, "video.mp4")

            logger.info("准备输出")
            final_clip.write_videofile(
                output_path,
                fps=24,
                threads=4
            )
            logger.info("输出完成")
            return output_path
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")

            raise

    def _create_clip(self, subdir_path, settings):
        audio_clip = None
        try:
            # 加载资源文件
            resources = {
                'image': os.path.join(subdir_path, "image.png"),
                'audio': os.path.join(subdir_path, "audio.mp3")
            }

            # 检查音频文件
            if not os.path.exists(resources['audio']):
                raise FileNotFoundError(f"音频文件不存在: {resources['audio']}")
            if os.path.getsize(resources['audio']) == 0:
                raise ValueError(f"音频文件为空: {resources['audio']}")

            # 加载音频文件
            audio_clip = AudioFileClip(resources['audio'])
            if audio_clip.reader is None:
                raise ValueError("音频文件加载失败：reader 为 None")
            duration = audio_clip.duration

            # 加载图片文件
            img_clip = ImageClip(resources['image']).set_duration(duration)
            img_clip = resize(img_clip, newsize=settings['resolution'])

            # 应用动态效果
            final_clip = self._apply_effects(img_clip, duration, settings)

            # 合成最终片段
            return CompositeVideoClip([final_clip]).set_audio(audio_clip)
        except Exception as e:
            if audio_clip is not None:
                audio_clip.close()
            logger.error(f"创建视频片段失败: {str(e)}")
            raise

    def _apply_effects(self, clip, duration, settings):
        """应用动态效果"""
        if clip is None:
            raise ValueError("Input clip is None")

        # 缩放效果
        def zoom_effect(t):
            if t < duration/3:
                return 1 + (settings['zoom_factor']-1)*(t/(duration/3))
            return settings['zoom_factor'] - (settings['zoom_factor']-1)*((t-duration/3)/(2*duration/3))
        
        # 平移效果
        def pan_effect(get_frame, t):
            img = get_frame(t)
            if img is None:
                # 如果 get_frame 返回 None，返回一个空帧或处理错误
                return np.zeros((settings['resolution'][1], settings['resolution'][0], 3), dtype=np.uint8)
            offset = int(settings['pan_intensity'] * abs(np.sin(0.5*t)))
            return img[:, offset:offset+img.shape[1]-40]
        
        # 确保返回有效的视频片段
        try:
            final_clip = clip.resize(lambda t: zoom_effect(t)).fl(pan_effect)
            if final_clip is None:
                raise ValueError("Failed to apply effects")
            return final_clip
        except Exception as e:
            logger.error(f"Failed to apply effects: {str(e)}")
            raise

    def _read_text(self, subdir_path):
        """读取字幕文件"""
        text_path = os.path.join(subdir_path, "span.txt")
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read().strip()