import logging
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor,as_completed,wait
from PIL import Image
from moviepy.editor import ImageSequenceClip, AudioFileClip
import subprocess
import threading
from server.utils.image_effect import ImageEffects
import gc
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class VideoService:
    """视频生成服务）"""
    
    def __init__(self):
        self.default_settings = {
            'resolution': (1920, 1080),
            'fps': 24,
            'threads': min(2, os.cpu_count()/1.5 or 4),
            'use_cuda': True,
            'codec': 'h264_nvenc',
            'batch_size': 5,
            'temp_dir': None,
            'fade_duration': 1.5,  # 淡入淡出时长（秒）
            'pan_range': (0.5, 0),  # 横向移动原图可用范围的50%，纵向0%
            'shake_intensity': 4  # 抖动强度（像素）
        }
        self.stop_flag = threading.Event()
        self._check_hardware()

    def _check_hardware(self):
        """检查硬件编码支持"""
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True)
            self.cuda_available = 'h264_nvenc' in result.stdout
     
            if not self.cuda_available:
                logger.warning("NVENC不可用，切换至CPU模式")
                self.default_settings.update({
                    'use_cuda': False,
                    'codec': 'libx264',
    
                })
        except Exception as e:
            logger.error("硬件检测失败: %s", str(e))
            self.cuda_available = False

    def _load_resources(self, subdir_path: str) -> tuple:
        """加载图片和音频资源"""
        image_path = os.path.join(subdir_path, "image.png")
        audio_path = os.path.join(subdir_path, "audio.mp3")

        # 验证文件有效性
        for path in [image_path, audio_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"文件不存在: {path}")
            if os.path.getsize(path) < 1024:
                raise ValueError(f"文件过小: {path}")

        # 加载图片
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image = img.resize(self.default_settings['resolution'], Image.LANCZOS)

        # 加载音频
        audio = AudioFileClip(audio_path)
        return image, audio

    def _process_segment(self, subdir: str, temp_dir: str, settings: Dict) -> Optional[str]:
        """处理单个视频片段"""
        logger.info("开始处理片段: %s", subdir)
        temp_file = os.path.join(temp_dir, f"vid_{subdir}_{os.getpid()}.mp4")
        start_time = time.time()
        frames = []  # 提前初始化frames
        
        try:
            # 加载资源
            image, audio = self._load_resources(
                os.path.join(settings['chapter_path'], subdir)
            )
            duration = audio.duration
            total_frames = int(duration * settings['fps'])
            
            # 生成帧数据
            for i in range(total_frames):
                if self.stop_flag.is_set():
                    break
                
                # 应用特效
                frame = self._apply_effects(
                    image.copy(), 
                    i/settings['fps'], 
                    duration, 
                    settings
                )
                frames.append(np.array(frame))
                frame.close()

            # 写入临时文件
            self._write_temp_video(frames, audio, temp_file, settings)
            
            logger.info("完成片段 %s | 耗时: %.1fs | 大小: %s",subdir, time.time()-start_time,self._format_size(os.path.getsize(temp_file)))

            return temp_file
            
        except Exception as e:
            logger.error("处理失败 [%s]: %s", subdir, str(e))
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return None
        finally:
            # 释放资源
            if 'image' in locals(): image.close()
            if 'audio' in locals(): audio.close()
            del frames
            gc.collect()

    def _write_temp_video(self, frames: list, audio: AudioFileClip, 
                         output_path: str, settings: Dict):
        """安全写入视频片段"""
        with ImageSequenceClip(frames, fps=settings['fps']) as clip:
            clip = clip.set_audio(audio)
            
            # 设置编码参数
            ffmpeg_params = []
            
            if settings['use_cuda'] and self.cuda_available:
                # GPU 相关参数
                ffmpeg_params.extend([
                    '-c:v', 'h264_nvenc',     # 明确指定NVENC编码器
                    '-preset', 'medium',         # NVENC支持的预设：fast, medium, slow, hp, hq, bd, ll, llhq, llhp
                    '-gpu', '0',
                     
            
                ])
            else:
                # CPU 相关参数
                ffmpeg_params.extend([
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23'
                ])
            
            
            clip.write_videofile(
                output_path,
                codec=None,                   # 让ffmpeg_params完全控制编码器
                audio_codec='aac',
                threads=settings['threads'],
                ffmpeg_params=ffmpeg_params,
                logger=None,
                verbose=False
            )

    def generate_video(self, chapter_path: str, video_settings: Dict = None) -> str:
        """生成视频主流程"""
        self.stop_flag.clear()
        final_settings = {**self.default_settings, **(video_settings or {})}
        final_settings['chapter_path'] = chapter_path
        output_path = os.path.join(chapter_path, "video.mp4")
        temp_files = []
        
        try:
            # 获取待处理片段列表
            subdirs = sorted([
                d for d in os.listdir(chapter_path)
                if os.path.isdir(os.path.join(chapter_path, d)) and d.isdigit()
            ], key=lambda x: int(x))
            
            if not subdirs:
                raise ValueError("无有效视频片段")


            logger.info("发现 %d 个待处理片段", len(subdirs))

            # 并行处理片段
            with ThreadPoolExecutor(max_workers=final_settings['threads']) as executor:
                futures = []
                for batch in self._chunk_list(subdirs, final_settings['batch_size']):
                    futures.extend(
                        executor.submit(self._process_segment, subdir,chapter_path, final_settings)
                        for subdir in batch
                    )

                # 收集结果
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        temp_files.append(result)
                        logger.info("进度: %d/%d", len(temp_files), len(subdirs))

            # 合并临时文件
            if not temp_files:
                raise ValueError("没有生成有效视频片段")
            return self._merge_videos(temp_files, output_path, final_settings)

        except Exception as e:
            logger.error("视频生成失败: %s", str(e))
            raise
        finally:
            self._cleanup_temp_files(temp_files)

    def _merge_videos(self, temp_files: List[str], output_path: str, settings: Dict) -> str:
        """合并视频片段"""
        concat_list = os.path.join(os.path.dirname(output_path), "concat.txt")
       
        try:
            # 生成合并列表，使用UTF-8编码写入
            with open(concat_list, 'w', encoding='utf-8') as f:
                for file in temp_files:
                    file_path = os.path.abspath(file)
                    # 替换反斜杠为正斜杠，避免转义问题
                    file_path = file_path.replace('\\', '/')
                    f.write(f"file '{file_path}'\n")
            
            # 构建FFmpeg命令
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                '-movflags', '+faststart',
                '-y', output_path
            ]
            if settings.get('use_cuda', False):
                cmd[1:1] = ['-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda']
      
            # 执行命令
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("视频合并成功: %s", output_path)
            return output_path
            
        except subprocess.CalledProcessError as e:
            # 根据系统编码解码错误信息
            import locale
            encoding = locale.getpreferredencoding()
            error_msg = e.stderr.decode(encoding, errors='replace')
            logger.error("合并失败: %s", error_msg)
            raise
        finally:
            if os.path.exists(concat_list):
                os.remove(concat_list)

    def _apply_effects(self, image: Image.Image, time_val: float, 
                      duration: float, settings: Dict) -> Image.Image:
        """应用所有视频特效"""
        try:
            effect_params = {
                'output_size': self.default_settings['resolution'],
                'fade_duration': settings.get('fade_duration', 1.0),
                'pan_range': settings.get('pan_range', (0.5, 0)),
            }
            
            return ImageEffects.apply_effects(
                image, time_val, duration, effect_params
            )
        except Exception as e:
            logger.error("特效处理失败: %s", str(e))
            raise


    def _cleanup_temp_files(self, files: List[str]):
        """清理临时文件"""
        for f_path in files:
            try:
                if os.path.exists(f_path):
                    os.remove(f_path)
                    logger.debug("已清理: %s", f_path)
            except Exception as e:
                logger.warning("清理失败 %s: %s", f_path, str(e))

    @staticmethod
    def _chunk_list(items: List, size: int):
        """列表分块"""
        for i in range(0, len(items), size):
            yield items[i:i + size]

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"