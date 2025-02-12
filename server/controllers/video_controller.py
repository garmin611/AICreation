from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional
import os
from pathlib import Path
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from server.services.video_service import VideoService
from server.utils.response import make_response, APIException

router = APIRouter(tags=["Video API"])

class VideoSettings(BaseModel):
    """视频效果配置模型"""
    zoom_factor: Optional[float] = None
    pan_intensity: Optional[int] = None
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    resolution: Optional[tuple[int, int]] = None

@router.post("/generate-video")
async def generate_video(
    project_name: str,
    chapter_name: str,
    settings: Optional[VideoSettings] = None
):
    """生成视频接口"""
    try:
        # 加载配置获取项目路径
        config = load_config()
        base_path = config['projects_path']
        
        # 构建章节路径
        chapter_path = Path(base_path) / project_name / chapter_name
        if not chapter_path.exists():
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
                video_settings=settings.dict(exclude_unset=True) if settings else None
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

@router.get("/get-video")
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