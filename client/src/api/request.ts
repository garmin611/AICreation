import type { AxiosResponse, AxiosRequestConfig } from 'axios'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import config from '@/config'

const NETWORK_ERROR = '网络请求异常,请稍后重试...'

// 创建一个axios实例对象
const service = axios.create({
    baseURL: config.baseApi
})

// 请求参数接口
export interface RequestOptions extends Omit<AxiosRequestConfig, 'url' | 'method'> {
    headers?: Record<string, string>
    raw?: boolean // 是否返回完整响应
}

// 流式请求参数接口
export interface StreamRequestOptions extends RequestOptions {
    signal?: AbortSignal
}

// API响应类型
export interface ApiResponse<T = any> {
    status: string
    data: T
    message?: string
}

// 响应拦截器
service.interceptors.response.use(
    (res: AxiosResponse<ApiResponse>) => {
        const { status, data, message: msg } = res.data;
        const config = res.config as AxiosRequestConfig & RequestOptions;

        if (status === 'success') {
            // 如果设置了raw，返回完整响应，否则只返回data
            return Promise.resolve(config.raw ? res.data : data);
        } else {
            // 如果后端返回了错误信息，显示后端的信息
            ElMessage.error(msg || NETWORK_ERROR);
            return Promise.reject(res.data); // 返回完整的响应数据
        }
    },
    (error) => {
        if (error.response) {
            // 如果后端返回了错误响应（如 500），显示后端的具体错误信息
            const errorMessage = error.response.data?.message || error.message;
            ElMessage.error(errorMessage || NETWORK_ERROR);
        } else {
            // 如果是网络错误或其他错误，显示通用错误信息
            ElMessage.error(error.message || NETWORK_ERROR);
        }
        return Promise.reject(error);
    }
);

// HTTP请求方法
class HttpClient {
    // GET请求
    get<T=any, O extends RequestOptions = RequestOptions>(url: string, params: any = null, options: O = {} as O): Promise<O extends { raw: true } ? ApiResponse<T> : T> {
        return service({
            url,
            method: 'get',
            params,
            ...options
        });
    }

    // POST请求
    post<T=any, O extends RequestOptions = RequestOptions>(url: string, data: any = null, options: O = {} as O): Promise<O extends { raw: true } ? ApiResponse<T> : T> {
        return service({
            url,
            method: 'post',
            data,
            ...options
        });
    }

    // PUT请求
    put<T=any, O extends RequestOptions = RequestOptions>(url: string, data: any = null, options: O = {} as O): Promise<O extends { raw: true } ? ApiResponse<T> : T> {
        return service({
            url,
            method: 'put',
            data,
            ...options
        });
    }

    // DELETE请求
    delete<T=any, O extends RequestOptions = RequestOptions>(url: string, params: any = null, options: O = {} as O): Promise<O extends { raw: true } ? ApiResponse<T> : T> {
        return service({
            url,
            method: 'delete',
            params,
            ...options
        });
    }

    // PATCH请求
    patch<T=any, O extends RequestOptions = RequestOptions>(url: string, data: any = null, options: O = {} as O): Promise<O extends { raw: true } ? ApiResponse<T> : T> {
        return service({
            url,
            method: 'patch',
            data,
            ...options
        });
    }

    // 流式请求
    stream<T = ReadableStream>(url: string, data?: any, options: StreamRequestOptions = {}): Promise<T> {
        return fetch(`${service.defaults.baseURL}${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
                ...options.headers
            },
            body: data ? JSON.stringify(data) : undefined,
            signal: options.signal
        }).then(response => {
            if (!response.ok) throw new Error(`HTTP错误: ${response.status}`);
            if (!response.body) throw new Error('无效的流式响应');
            return response.body as unknown as T;
        });
    }
}

const request = new HttpClient();
export default request;