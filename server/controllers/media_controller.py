from fastapi import APIRouter, Depends, HTTPException, Request, Response
from server.config.config import load_config
from server.services.image_service import ImageService
from server.services.audio_service import AudioService
from server.utils.response import make_response
import os
import datetime
import logging
from fastapi.responses import FileResponse

config = load_config()
router = APIRouter(prefix='/media')
image_service = ImageService()
audio_service = AudioService()
logger = logging.getLogger(__name__)

@router.post('/generate_images')
async def generate_images(request: Request):
    """生成图片的接口。"""
    try:
        data = await request.json()
        
        # 获取项目、章节和提示词信息
        project_name = data.get('project_name')
        chapter_name = data.get('chapter_name')
        prompts = data.get('prompts')
        image_settings = data.get('imageSettings')  # 暂存，等待后续开发
        
        if not all([project_name, chapter_name, prompts]):
            return make_response(status='error', msg='缺少必要参数：project_name, chapter_name, prompts')
        
        # 获取工作流和参数
        workflow = data.get('workflow', config.get('default_workflow', {}).get('name', 'default_workflow.json'))
        params = data.get('params', {})
        
        # 构建输出路径数组
        output_dirs = []
        for prompt_data in prompts:
            span_id = prompt_data.get('id')
            if span_id is None:
                return make_response(status='error', msg='prompts中缺少id字段')
                
            # 构建输出路径（确保与获取图片时的路径一致）
            span_path = os.path.join(config['projects_path'], project_name, chapter_name, str(span_id))
            output_dirs.append(span_path)
            
            # 确保目录存在
            os.makedirs(span_path, exist_ok=True)
            logger.info(f"Created output directory: {span_path}")
        
        # 提取所有提示词
        prompt_texts = [p.get('prompt') for p in prompts]
        if not all(prompt_texts):
            return make_response(status='error', msg='prompts中存在空的prompt字段')
        
        try:
            # 调用图像服务生成图片
            result = image_service.generate_images(
                prompts=prompt_texts,
                output_dirs=output_dirs,
                workflow=workflow,
                params=params
            )
            return make_response(
                data=result,
                msg='图片生成任务已提交'
            )
        except Exception as e:
            print(f"Error : {str(e)}")
            return make_response(status='error', msg=str(e))
            
    except Exception as e:
        return make_response(status='error', msg=f'处理请求时发生错误：{str(e)}')

@router.post('/generate-audio')
async def generate_audio(request: Request):
    """生成音频文件的接口。"""
    try:
        data = await request.json()
        
        # 获取项目、章节和提示词信息
        project_name = data.get('project_name')
        chapter_name = data.get('chapter_name')
        prompts = data.get('prompts')
        audio_settings = data.get('audioSettings', {})
        
        if not all([project_name, chapter_name, prompts]):
            return make_response(status='error', msg='缺少必要参数：project_name, chapter_name, prompts')
        
        # 构建输出路径数组
        output_dirs = []
        prompt_texts = []
        for prompt_data in prompts:
            span_id = prompt_data.get('id')
            if span_id is None:
                return make_response(status='error', msg='prompts中缺少id字段')
                
            # 构建输出路径
            span_path = os.path.join(config['projects_path'], project_name, chapter_name, str(span_id))
            output_dirs.append(span_path)
            
            # 提取提示词文本
            prompt_text = prompt_data.get('prompt')
            if not prompt_text:
                return make_response(status='error', msg='prompts中存在空的prompt字段')
            prompt_texts.append(prompt_text)
        
        try:
            # 调用音频服务生成音频
            result = await audio_service.generate_audio(
                prompts=prompt_texts,
                output_dirs=output_dirs,
                # voice=audio_settings.get('voice', 'zh-CN-XiaoxiaoNeural'),
                # rate=audio_settings.get('rate', '+0%')
            )
            return make_response(
                data=result,
                msg='音频生成任务已提交'
            )
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return make_response(status='error', msg=str(e))
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return make_response(status='error', msg=f'处理请求时发生错误：{str(e)}')

@router.get('/progress')
async def get_generation_progress(task_id: str):
    """获取生成任务的进度。"""
    try:
        if not task_id:
            return make_response(status='error', msg='缺少任务ID')
            
        # 获取任务进度
        if task_id.startswith('audio_'):
            progress = audio_service.get_generation_progress(task_id)
            progress['task_type'] = 'audio'
        else:
            progress = image_service.get_generation_progress(task_id)
            progress['task_type'] = 'image'
            
        return make_response(
            data=progress,
            msg='获取进度成功'
        )
    except ValueError as e:
        return make_response(status='error', msg=str(e))
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        return make_response(status='error', msg=f'获取进度时发生错误：{str(e)}')

@router.post('/cancel')
async def cancel_generation(task_id: str):
    """取消生成任务。"""
    try:
        # 根据任务ID的前缀判断是图片任务还是音频任务
        if task_id.startswith('audio_'):
            success = audio_service.cancel_generation(task_id)
        else:
            success = image_service.cancel_generation(task_id)
            
        if success:
            return make_response(msg='任务已取消')
        else:
            return make_response(status='error', msg='取消任务失败')
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        return make_response(status='error', msg=str(e))


@router.get('/workflows')
async def list_workflows():
    """列出所有可用的工作流。"""
    try:
        workflows = image_service.list_workflows()
        return make_response(
            data={'workflows': workflows},
            msg='获取工作流列表成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取工作流列表时发生错误：{str(e)}')

@router.get('/workflow/{workflow_name}')
async def get_workflow(workflow_name: str):
    """获取指定工作流的详细信息。"""
    try:
        workflow = image_service.get_workflow(workflow_name)
        if workflow is None:
            return make_response(status='error', msg='工作流不存在')
        return make_response(
            data={'workflow': workflow},
            msg='获取工作流成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取工作流时发生错误：{str(e)}')

@router.get('/get_image')
async def get_media_image(project_name: str, chapter_name: str, span_id: str):
    """获取指定项目章节span的图片。"""
    try:
        # 构建图片路径（与生成时的路径保持一致）
        image_path = os.path.join(config['projects_path'], project_name, chapter_name, str(span_id), 'image.png')
        logger.info(f"Trying to access image at: {image_path}")
            
        return FileResponse(image_path, media_type='image/png')
        
    except Exception as e:
        logger.error(f"Error accessing image: {str(e)}")
        return make_response(status='error', msg=str(e))

@router.get('/get_audio')
async def get_media_audio(project_name: str, chapter_name: str, span_id: str):
    """获取指定项目章节span的音频。"""
    try:
        # 构建音频路径
        audio_path = os.path.join(config['projects_path'], project_name, chapter_name, str(span_id), 'audio.mp3')
        
        if not os.path.exists(audio_path):
            return make_response(status='error', msg='音频不存在')
            
        return FileResponse(audio_path, media_type='audio/mpeg')
        
    except Exception as e:
        logger.error(f"Error accessing audio: {str(e)}")
        return make_response(status='error', msg=str(e))
