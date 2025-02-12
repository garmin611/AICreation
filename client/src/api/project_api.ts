import request from './request'
import type { ProjectInfo } from '@/types/project'

export default {
    // 获取项目列表
    getProjectList() {
        return request<string[]>({
            url: '/project/list',
            method: 'get'
        })
    },

    // 创建新项目
    createProject(projectName: string) {
        return request<{project_name:string}>({
            url: '/project/create',
            method: 'post',
            data: { project_name: projectName }
        })
    },

    // 更新项目
    updateProject(oldName: string, newName: string) {
        return request<{project_name:string}>({
            url: '/project/update',
            method: 'put',
            data: { 
                old_name: oldName,
                new_name: newName
            }
        })
    },

    // 删除项目
    deleteProject(projectName: string) {
        return request<void>({
            url: `/project/delete/${projectName}`,
            method: 'delete'
        })
    },

    // 获取项目详情
    getProjectInfo(projectName: string) {
        return request<ProjectInfo>({
            url: '/project/info',
            method: 'get',
            params: { project_name: projectName }
        })
    }
}