from fastapi import APIRouter, Depends, HTTPException, Request
from server.config.config import load_config, update_config
from server.utils.response import make_response

router = APIRouter(prefix='/admin')

@router.get('/config')
async def get_config():
    """获取当前配置"""
    try:
        config = load_config()
        # 移除敏感信息
        if 'api_keys' in config:
            del config['api_keys']
        return make_response(
            data=config,
            msg='获取配置成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'获取配置时发生错误：{str(e)}')

@router.post('/config')
async def update_configuration(request: Request):
    """更新配置"""
    try:
        data = await request.json()
    except Exception:
        return make_response(status='error', msg='无效的 JSON 数据')
        
    if not data:
        return make_response(status='error', msg='配置数据不能为空')
        
    try:
        update_config(data)
        return make_response(
            data=data,
            msg='配置更新成功'
        )
    except Exception as e:
        return make_response(status='error', msg=f'更新配置时发生错误：{str(e)}')
