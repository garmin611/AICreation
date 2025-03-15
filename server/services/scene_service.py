import os
import json
from server.config.config import load_config
from typing import Dict, List
from .base_service import SingletonService
import logging

logger = logging.getLogger(__name__)

class SceneService(SingletonService):
    def __init__(self):
        self.config = load_config()
        self.scenes_cache={}

    def _get_scene_path(self, project_name: str) -> str:

        return os.path.join(self.config['projects_path'], project_name, 'scenes.json')

    def load_scenes(self, project_name: str) -> Dict[str, str]:
        """
        加载项目的场景信息。
        """
        if project_name in self.scenes_cache:
            return self.scenes_cache[project_name]

        scenes_path = self._get_scene_path(project_name)

        defalut_scenes={}

        if not os.path.exists(scenes_path):
            self.scenes_cache[project_name]=defalut_scenes
            return defalut_scenes

        with open(scenes_path, 'r', encoding='utf-8') as f:
            scenes = json.load(f)

        self.scenes_cache[project_name]=scenes
        return scenes

    def update_scenes(self, project_name: str, new_scenes: Dict[str, str],force_update=False) -> bool:
        """
        更新项目的场景信息。
        """
        try:
            scenes_path = self._get_scene_path(project_name)

            scenes=self.load_scenes(project_name)
            
            
            for scene_name,scene_desc in new_scenes.items():
                
                if scene_name !='':
                    if not force_update and scene_name in scenes:#实体已存在时是否需要更新
                        continue
                    scenes[scene_name]=scene_desc
                    logger.info(f"更新实体:{scene_name},{scene_desc}")

            self.scenes_cache[project_name]=scenes

            
            with open(scenes_path, 'w', encoding='utf-8') as f:
                json.dump(scenes, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"更新场景信息时发生错误：{str(e)}")
            raise e

    def delete_scenes(self, project_name: str, scene_names: List[str]) -> bool:
        """
        删除项目的场景信息。
        """
        try:
            scenes=self.load_scenes(project_name)

            for scene_name in scene_names:
                if scene_name in scenes:
                    del scenes[scene_name]

            self.scenes_cache[project_name]=scenes

            scenes_path = self._get_scene_path(project_name)

            with open(scenes_path, 'w', encoding='utf-8') as f:
                json.dump(scenes, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"删除场景信息时发生错误：{str(e)}")
            raise e

    def get_scene_names(self, project_name: str) -> List[str]:
        """
        获取项目的所有场景名称。
        """
        scenes = self.load_scenes(project_name)
        return list(scenes.keys())

    def get_scene_descs(self,project_name:str,scene_names:[str])->List[str]:
        """
        获取项目的多个场景描述。
        """
        scenes = self.load_scenes(project_name)
        return [scenes[scene_name] for scene_name in scene_names]

    def get_scene_dict(self,project_name:str,scene_names:[str])->Dict[str,str]:
        """
        获取项目的场景字典。
        """
        scenes = self.load_scenes(project_name)
        return {scene_name:scenes[scene_name] for scene_name in scene_names}