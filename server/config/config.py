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
    
    # 解析相对路径
    if 'projects_path' in config:
        config['projects_path'] = os.path.abspath(os.path.join(server_dir, config['projects_path']))
    if 'prompts_path' in config:
        config['prompts_path'] = os.path.abspath(os.path.join(server_dir, config['prompts_path']))
    if 'default_workflow' in config and 'file' in config['default_workflow']:
        config['default_workflow']['file'] = os.path.abspath(os.path.join(server_dir, config['default_workflow']['file']))
    
    return config

def save_config(config: Dict[str, Any]) -> None:
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:

    config = load_config()
    
    for key, value in updates.items():
        if '.' in key:
            # 处理嵌套的配置项
            keys = key.split('.')
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            # 处理顶层配置项
            config[key] = value
    
    save_config(config)
    return config
