# image_effects.py
import numpy as np
from PIL import Image, ImageEnhance, ImageChops
import random
from typing import Dict

class ImageEffects:
    @staticmethod
    def fade_effect(image: Image.Image, time_val: float, duration: float, params: Dict) -> Image.Image:
        """淡入淡出效果"""
        if params.get('fade_duration', 0) <= 0:
            return image
            
        fade_duration = params['fade_duration']
        alpha = 1.0
        
        # 淡入阶段
        if time_val < fade_duration:
            alpha = time_val / fade_duration
        # 淡出阶段
        elif duration - time_val < fade_duration:
            alpha = (duration - time_val) / fade_duration
            
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        alpha_layer = Image.new('L', image.size, int(255 * alpha))
        image.putalpha(alpha_layer)
        return image

    @staticmethod
    def pan_effect(image: Image.Image, time_val: float, duration: float, params: Dict) -> Image.Image:
        """自动调整图片尺寸的平移效果"""
        output_w, output_h = params['output_size']
        pan_range = params.get('pan_range', (0.3, 0))  # 横向移动30%的图片范围
        
        # 自动缩放图片（保证可移动范围）
        scaled_img = ImageEffects._auto_scale(image, output_w, output_h, pan_range)
        
        # 计算移动进度（0.0~1.0）
        progress = time_val / duration
        
        # 计算裁剪位置（确保始终有效）
        x_offset = int((scaled_img.width - output_w) * progress)
        y_offset = int((scaled_img.height - output_h) * 0)  # 垂直方向无移动
        
        # 安全裁剪
        return scaled_img.crop((
            x_offset, 
            y_offset,
            x_offset + output_w,
            y_offset + output_h
        ))

    @staticmethod
    def _auto_scale(orig_img: Image.Image, target_w: int, target_h: int, pan_range: tuple) -> Image.Image:
        """智能缩放算法（保证可移动空间）"""
        # 计算需要的最小缩放比例
        scale_x = (target_w * (1 + pan_range[0])) / orig_img.width
        scale_y = (target_h * (1 + pan_range[1])) / orig_img.height
        scale = max(scale_x, scale_y)
        
        # 保持宽高比缩放
        new_width = int(orig_img.width * scale)
        new_height = int(orig_img.height * scale)
        return orig_img.resize((new_width, new_height), Image.LANCZOS)


    @classmethod
    def apply_effects(cls, image: Image.Image, time_val: float, duration: float, params: Dict) -> Image.Image:
        """应用所有特效"""
        # 效果执行顺序
        effect_chain = [
            cls.fade_effect,
        ]
        if params.get('use_pan', True):
            effect_chain.append(cls.pan_effect)
        
        processed_image = image.copy()
        for effect in effect_chain:
            processed_image = effect(processed_image, time_val, duration, params)
            # 保持图像边界
            processed_image = processed_image.crop((0, 0, *params['output_size']))
        
        return processed_image