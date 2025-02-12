import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const NETWORK_ERROR = '网络请求异常,请稍后重试...'

// 创建一个axios实例对象
const service = axios.create({
    baseURL: "http://localhost:5000"
})

export interface ApiResponse<T = any> {
    status: string
    data: T
    message?: string
}

// 响应拦截器
service.interceptors.response.use(
    (res: AxiosResponse<ApiResponse>) => {
        
        const { status, data, message: msg } = res.data
        
        if (status === 'success') {
            // if (msg) {
            //     ElMessage.success(msg)
            // }
            return data
        } else {
            ElMessage.error(msg || NETWORK_ERROR)
            return Promise.reject(msg || NETWORK_ERROR)
        }
    },
    (error) => {
        // 处理401等错误
        if (error.response?.status === 401) {
            sessionStorage.removeItem('jwtToken')
            ElMessage.error('登录已过期，请重新登录')
        } else {
            ElMessage.error(error.message || NETWORK_ERROR)
        }
        return Promise.reject(error)
    }
)

// 核心请求函数
export interface RequestOptions extends AxiosRequestConfig {
    url: string
    method?: string
    data?: any
    params?: any
    headers?: Record<string, string>
}

const request = <T = any>(options: RequestOptions): Promise<T> => {
    options.method = options.method || 'get'
    if (options.method.toLowerCase() === 'get' && options.data && !options.params) {
        options.params = options.data
    }
    return service(options)
}

export type RequestFunction = typeof request
export default request