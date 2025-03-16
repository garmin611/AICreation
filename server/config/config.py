import os
import yaml
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """从 config.yaml 加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 获取 server 目录的路径
    server_dir = os.path.dirname(os.path.dirname(__file__))
    
    # #如果没有设置绝对路径而是设置的相对路径，则解析相对路径
    if 'relative_projects_path' in config and 'projects_path' not in config:
        config['projects_path'] = os.path.abspath(os.path.join(server_dir, config['relative_projects_path']))

    if 'relative_prompts_path' in config and 'prompts_path' not in config:
        config['prompts_path'] = os.path.abspath(os.path.join(server_dir, config['relative_prompts_path']))

    if 'default_workflow' in config and 'file' in config['default_workflow']:
        config['default_workflow']['file'] = os.path.abspath(os.path.join(server_dir, config['default_workflow']['file']))
    
    
    if 'relative_workflow_path' in config and 'workflow_path' not in config:
        workflow_path = os.path.abspath(os.path.join(server_dir, config['relative_workflow_path']))
        config['workflow_path'] = workflow_path
    
    workflow_path = config['workflow_path']

    config['all_workflow'] = []
    # 读取 workflow 目录下的所有 json 文件
    if os.path.exists(workflow_path) and os.path.isdir(workflow_path):
        for file in os.listdir(workflow_path):
            if file.endswith('.json'):
                config['all_workflow'].append(file)
    
    return config

def save_config(config: Dict[str, Any]) -> None:
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    # 加载原始配置
    config = load_config()
    
    # 过滤掉计算得到的属性
    filtered_config = {
        k: v for k, v in config.items() 
        if k not in ['projects_path', 'prompts_path', 'workflow_path', 'all_workflow']
    }
    
    # 更新配置
    for key, value in updates.items():
        if '.' in key:
            # 处理嵌套的配置项
            keys = key.split('.')
            current = filtered_config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            # 处理顶层配置项
            filtered_config[key] = value
    
    # 保存配置
    save_config(filtered_config)
    return load_config()  # 返回完整的配置（包含计算属性）
