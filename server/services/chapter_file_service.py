import os
import json
from server.config.config import load_config
from typing import Dict, List
from .base_service import SingletonService
import logging

logger = logging.getLogger(__name__)

class ChapterFileService(SingletonService):
    def __init__(self):
        self.config = load_config()
        self.projects_path = self.config.get('projects_path', 'projects/')

    def get_chapter_content(self, project_name: str, chapter_name: str) -> str:
        """
        获取指定章节的content.txt文件内容
        
        参数:
            project_name (str): 项目名称
            chapter_name (str): 章节名称，例如 'chapter6'
            
        返回:
            str: 章节内容，如果文件不存在则返回空字符串
        """
        try:
            chapter_path = os.path.join(self.projects_path, project_name, chapter_name)
            content_path = os.path.join(chapter_path, 'content.txt')
            if os.path.exists(content_path):
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ''
        except Exception as e:
            logger.error(f"Error reading chapter content: {e}")
            return ''

    def get_latest_chapter(self, project_path: str) -> int:
        """获取最新章节编号"""
        if not os.path.exists(project_path):
            raise Exception(f"项目路径不存在: {project_path}")
            
        chapters = [d for d in os.listdir(project_path) 
                   if os.path.isdir(os.path.join(project_path, d)) 
                   and d.startswith("chapter")]
        if not chapters:
            return 1
            
        latest = max(int(ch.replace("chapter", "")) for ch in chapters)
        return latest

    def generate_span_files(self, project_name: str, chapter_name: str, spans_and_prompts: List[dict]) -> None:
        """
        为每个文本片段生成对应的文件

        Args:
            project_name: 项目名称
            chapter_name: 章节名称
            spans_and_prompts: 包含文本片段和场景描述的列表
            
        Raises:
            Exception: 当章节目录不存在时抛出
        """
        try:
            # 构建章节目录路径
            chapter_dir = os.path.join('projects', project_name,  chapter_name)
            
            # 如果章节目录不存在，直接返回
            if not os.path.exists(chapter_dir):
                raise Exception(f"章节目录不存在: {chapter_dir}")
            
            # 清空现有的子文件夹
            for item in os.listdir(chapter_dir):
                item_path = os.path.join(chapter_dir, item)
                if os.path.isdir(item_path) and item.isdigit():  # 只删除数字命名的文件夹
                    import shutil
                    shutil.rmtree(item_path)
            
            # 为每个片段创建文件
            for i, span in enumerate(spans_and_prompts):
                span_dir = os.path.join(chapter_dir, str(i+1))
                os.makedirs(span_dir, exist_ok=True)
                
                # 写入span.txt
                with open(os.path.join(span_dir, 'span.txt'), 'w', encoding='utf-8') as f:
                    f.write(span['content'])
                
                # 写入prompt.json
                prompt_data = {
                    'base_scene':span['base_scene'],
                    'scene': span['scene'],
                    'prompt': ''  # 默认为空
                }
                with open(os.path.join(span_dir, 'prompt.json'), 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, ensure_ascii=False, indent=2)
                    
            logging.info(f"已为章节 {chapter_name} 生成 {len(spans_and_prompts)} 个场景文件")
            
        except Exception as e:
            logging.error(f"生成场景文件时出错: {str(e)}")
            raise e
