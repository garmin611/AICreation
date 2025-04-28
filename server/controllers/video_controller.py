from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional, Tuple
import os
from pathlib import Path
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from server.config.config import load_config
from server.services.video_service import VideoService
from server.utils.response import make_response, APIException
import logging

router = APIRouter(prefix='/video')
logger = logging.getLogger(__name__)

class VideoSettings(BaseModel):
    project_name:Optional[str] = None
    chapter_name:Optional[str] = None
    """视频效果配置模型"""
    fade_duration: Optional[float] = 1.2# 淡入淡出时长（秒）
    fps: Optional[float] = 15
    use_pan: Optional[bool] = True#是否使用平移效果
    pan_range: Optional[Tuple[float, float]] = (0.5, 0.5)# 横向移动原图可用范围的50%，纵向50%
    resolution: Optional[Tuple[int, int]] = (1920, 1080)

@router.post("/generate_video")
async def generate_video(
    settings: Optional[VideoSettings] = None
):
    """生成视频接口"""
    try:
        # 加载配置获取项目路径
        config = load_config()
        base_path = config.get('projects_path', 'projects/')
   
    
    
        # 构建章节路径
        chapter_path=os.path.join(base_path,settings.project_name,settings.chapter_name)
   

        logger.info(chapter_path)
        if not os.path.exists(chapter_path) :
            raise APIException(
                detail="Chapter not found",
                status="error"
            )

        # 调用视频服务（异步执行）
        video_service = VideoService()
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                video_service.generate_video,
                str(chapter_path),
                video_settings=settings.model_dump(exclude_unset=True) if settings else None
            )
            output_path = future.result()

        return make_response(
            data={"video_path": output_path},
            msg="Video generated successfully"
        )

    except APIException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/get_video")
async def get_video(project_name: str, chapter_name: str):
    """获取视频文件接口"""
    try:
        config = load_config()
        video_path = Path(config['projects_path']) / project_name / chapter_name / "video.mp4"
        
        if not video_path.exists():
            raise APIException(
                detail="Video not found",
                status="error"
            )
            
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{chapter_name}_video.mp4"
        )
    except APIException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )