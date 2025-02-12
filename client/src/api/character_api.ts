import request from './request'

interface Character {
  name: string
  attributes: {
    role?: string
    description?: string
    [key: string]: any
  }
}

export interface CharacterAttributes {
  role?: string
  description?: string
  [key: string]: any
}

export interface UpdateCharacterParams {
  name: string
  attributes: CharacterAttributes
}

export const characterApi = {
  // 获取角色列表
  getCharacterList(projectName: string) {
    return request({
      url: '/character/list',
      method: 'get',
      params: { project_name: projectName }
    })
  },
  
  // 更新角色
  updateCharacter(projectName: string, params: UpdateCharacterParams) {
    return request({
      url: '/character/update',
      method: 'post',
      data: { 
        project_name: projectName,
        name: params.name,
        attributes: params.attributes
      }
    })
  },
  
  // 切换锁定状态
  toggleLock(projectName: string, entityName: string) {
    return request({
      url: '/character/toggle_lock',
      method: 'post',
      data: { 
        project_name: projectName,
        entity_name: entityName
      }
    })
  },

  // 删除角色
  deleteCharacter(projectName: string, entityName: string) {
    return request({
      url: `/character/entity/${entityName}`,
      method: 'delete',
      params: { project_name: projectName }
    })
  }
}
