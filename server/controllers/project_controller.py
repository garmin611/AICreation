from fastapi import APIRouter, Depends, HTTPException, Request
import os
from server.config.config import load_config
import json
from datetime import datetime
from server.utils.response import make_response
import shutil

router = APIRouter(prefix='/project')

@router.post('/create')
async def create_project(request: Request):
    """创建新项目"""
    try:
        data = await request.json()
        project_name = data.get('project_name')
        
        if not project_name:
            return make_response(status='error', msg='项目名称不能为空')
            
        config = load_config()
        projects_path = config.get('projects_path', 'projects/')
        
        # 创建项目目录
        project_path = os.path.join(projects_path, project_name)
        if os.path.exists(project_path):
            return make_response(status='error', msg='项目已存在')
            
        os.makedirs(project_path)
        
        # 创建空的知识图谱文件
        kg_path = os.path.join(project_path, 'kg.json')
        with open(kg_path, 'w', encoding='utf-8') as f:
            json.dump({
                'locked_entities': [],
                'relationships': [],
                'entities': []
            }, f, ensure_ascii=False, indent=2)
            
        # 自动创建第一个章节
        first_chapter = 'chapter1'
        first_chapter_path = os.path.join(project_path, first_chapter)
        
        # 创建新章节目录和content.txt文件
        os.makedirs(first_chapter_path, exist_ok=True)
        content_file = os.path.join(first_chapter_path, 'content.txt')
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write('')
            
        return make_response(
            data={
                'project_name': project_name,
                'first_chapter': first_chapter
            },
            msg='项目创建成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'创建项目时发生错误：{str(e)}')

@router.get('/info')
async def get_project_info(project_name: str):
    """获取项目信息"""
    if not project_name:
        return make_response(status='error', msg='项目ID不能为空')
        
    config = load_config()
    projects_path = config.get('projects_path', 'projects/')
    
    # 构建项目路径
    project_path = os.path.join(projects_path, project_name)
    if not os.path.exists(project_path):
        return make_response(status='error', msg='项目不存在')
        
    try:
        
        # 获取章节列表
        chapters = []
        for chapter_dir in sorted(os.listdir(project_path)):
            if chapter_dir.startswith('chapter'):
                chapter_path = os.path.join(project_path, chapter_dir)
                if os.path.isdir(chapter_path):
                    # 获取章节信息
                    spans = []
                    for span_dir in sorted(os.listdir(chapter_path)):
                        span_path = os.path.join(chapter_path, span_dir)
                        if os.path.isdir(span_path):
                            # 获取span信息
                            span_info = {
                                'id': span_dir,
                                'has_content': os.path.exists(os.path.join(span_path, 'span.txt')),
                                'has_prompt': os.path.exists(os.path.join(span_path, 'prompt.txt')),
                                'images': [f for f in os.listdir(span_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
                                'audios': [f for f in os.listdir(span_path) if f.lower().endswith('.wav')]
                            }
                            spans.append(span_info)
                    
                    chapters.append({
                        'id': chapter_dir,
                        'spans': spans
                    })
                    
        # 获取知识图谱
        kg_path = os.path.join(project_path, 'kg.json')
        with open(kg_path, 'r', encoding='utf-8') as f:
            knowledge_graph = json.load(f)
                
        return make_response(
            data={
                'project_name': project_name,
                'chapters': chapters,
                'knowledge_graph': knowledge_graph
            },
            msg='获取项目信息成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取项目信息时发生错误：{str(e)}')

@router.get('/kg')
async def get_knowledge_graph(project_name: str):
    """获取项目知识图谱"""
    if not project_name:
        return make_response(status='error', msg='项目ID不能为空')
        
    config = load_config()
    projects_path = config.get('projects_path', 'projects/')
    
    # 构建知识图谱文件路径
    kg_path = os.path.join(projects_path, project_name, 'kg.json')
    if not os.path.exists(kg_path):
        return make_response(status='error', msg='知识图谱不存在')
        
    try:
        with open(kg_path, 'r', encoding='utf-8') as f:
            knowledge_graph = json.load(f)
            
        return make_response(
            data={
                'project_name': project_name,
                'knowledge_graph': knowledge_graph
            },
            msg='获取知识图谱成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取知识图谱时发生错误：{str(e)}')

@router.get('/list')
async def get_project_list():
    """获取所有项目列表"""
    try:
        config = load_config()
        projects_path = config.get('projects_path', 'projects/')
        
        # 确保项目目录存在
        if not os.path.exists(projects_path):
            return make_response(status='error', msg='项目目录不存在')
            
        # 获取所有项目名称（即目录名）
        project_names = [name for name in os.listdir(projects_path) 
                        if os.path.isdir(os.path.join(projects_path, name))]
            
        return make_response(
            data=project_names,
            msg='获取项目列表成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取项目列表时发生错误：{str(e)}')

@router.put('/update')
async def update_project(request: Request):
    """更新项目名称"""
    try:
        data = await request.json()
        old_name = data.get('old_name')
        new_name = data.get('new_name')
        
        if not all([old_name, new_name]):
            return make_response(status='error', msg='项目名称不能为空')
            
        config = load_config()
        projects_path = config.get('projects_path', 'projects/')
        
        # 检查原项目是否存在
        old_project_path = os.path.join(projects_path, old_name)
        if not os.path.exists(old_project_path):
            return make_response(status='error', msg='项目不存在')
            
        # 检查新名称是否已存在
        new_project_path = os.path.join(projects_path, new_name)
        if os.path.exists(new_project_path):
            return make_response(status='error', msg='新项目名称已存在')
            
        # 重命名项目目录
        os.rename(old_project_path, new_project_path)
        
        return make_response(
            data={'project_name': new_name},
            msg='项目更新成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'更新项目时发生错误：{str(e)}')

@router.delete('/delete/{project_name}')
async def delete_project(project_name: str):
    """删除项目"""
    try:
        config = load_config()
        projects_path = config.get('projects_path', 'projects/')
        
        # 构建项目路径
        project_path = os.path.join(projects_path, project_name)
        if not os.path.exists(project_path):
            return make_response(status='error', msg='项目不存在')
            
        # 删除项目目录及其内容
        shutil.rmtree(project_path)
        
        return make_response(msg='项目删除成功')
    except Exception as e:
        return make_response(status='error', msg=f'删除项目时发生错误：{str(e)}')
