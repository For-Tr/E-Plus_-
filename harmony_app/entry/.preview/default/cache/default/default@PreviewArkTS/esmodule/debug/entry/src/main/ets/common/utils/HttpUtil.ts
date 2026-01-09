import http from "@ohos:net.http";
import { API_BASE_URL, API_TIMEOUT, StorageKeys } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import StorageUtil from "@bundle:com.family.emotion/entry/ets/common/utils/StorageUtil";
interface RequestOptions {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    headers?: object;
    body?: object | string;
    needAuth?: boolean;
}
interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
    status?: number;
}
class HttpUtil {
    private static instance: HttpUtil;
    private constructor() { }
    public static getInstance(): HttpUtil {
        if (!HttpUtil.instance) {
            HttpUtil.instance = new HttpUtil();
        }
        return HttpUtil.instance;
    }
    /**
     * 发送HTTP请求
     */
    async request<T = any>(url: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
        const { method = 'GET', headers = {}, body = null, needAuth = true } = options;
        try {
            // 创建HTTP请求
            const httpRequest = http.createHttp();
            // 构建完整URL
            const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
            // 构建请求头
            const requestHeaders = {
                'Content-Type': 'application/json',
                ...headers
            };
            // 如果需要认证,添加Token
            if (needAuth) {
                const token = await StorageUtil.getString(StorageKeys.ACCESS_TOKEN);
                if (token) {
                    requestHeaders['Authorization'] = `Bearer ${token}`;
                }
            }
            // 构建请求选项
            const requestOptions: http.HttpRequestOptions = {
                method: method as http.RequestMethod,
                header: requestHeaders,
                readTimeout: API_TIMEOUT,
                connectTimeout: API_TIMEOUT,
                extraData: body ? (typeof body === 'string' ? body : JSON.stringify(body)) : undefined
            };
            console.info(`[HttpUtil] Request: ${method} ${fullUrl}`);
            if (body) {
                console.info(`[HttpUtil] Body:`, JSON.stringify(body));
            }
            // 发送请求
            const response = await httpRequest.request(fullUrl, requestOptions);
            console.info(`[HttpUtil] Response status: ${response.responseCode}`);
            console.info(`[HttpUtil] Response data:`, JSON.stringify(response.result));
            // 销毁请求对象
            httpRequest.destroy();
            // 处理响应
            if (response.responseCode === 200 || response.responseCode === 201) {
                const data = typeof response.result === 'string'
                    ? JSON.parse(response.result)
                    : response.result;
                return {
                    success: true,
                    data: data as T,
                    status: response.responseCode
                };
            }
            else if (response.responseCode === 401) {
                // Token过期,尝试刷新
                console.warn('[HttpUtil] Token expired, trying to refresh...');
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // 重试原请求
                    return await this.request(url, options);
                }
                else {
                    return {
                        success: false,
                        error: '登录已过期,请重新登录',
                        status: 401
                    };
                }
            }
            else {
                const errorData = typeof response.result === 'string'
                    ? JSON.parse(response.result)
                    : response.result;
                return {
                    success: false,
                    error: errorData?.error || errorData?.message || '请求失败',
                    status: response.responseCode
                };
            }
        }
        catch (error) {
            console.error('[HttpUtil] Request failed:', JSON.stringify(error));
            return {
                success: false,
                error: '网络请求失败,请检查网络连接'
            };
        }
    }
    /**
     * GET请求
     */
    async get<T = any>(url: string, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: 'GET', needAuth });
    }
    /**
     * POST请求
     */
    async post<T = any>(url: string, body?: object, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: 'POST', body, needAuth });
    }
    /**
     * PUT请求
     */
    async put<T = any>(url: string, body?: object, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: 'PUT', body, needAuth });
    }
    /**
     * DELETE请求
     */
    async delete<T = any>(url: string, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: 'DELETE', needAuth });
    }
    /**
     * 刷新Token
     */
    async refreshToken(): Promise<boolean> {
        try {
            const refreshToken = await StorageUtil.getString(StorageKeys.REFRESH_TOKEN);
            if (!refreshToken) {
                return false;
            }
            const response = await this.post('/api/v1/auth/refresh/', {
                refresh: refreshToken
            }, false);
            if (response.success && response.data) {
                await StorageUtil.setString(StorageKeys.ACCESS_TOKEN, response.data.access);
                console.info('[HttpUtil] Token refreshed successfully');
                return true;
            }
            return false;
        }
        catch (error) {
            console.error('[HttpUtil] Refresh token failed:', JSON.stringify(error));
            return false;
        }
    }
    /**
     * 上传图片(Base64)
     */
    async uploadImage(url: string, imageBase64: string, fieldName: string = 'photo'): Promise<ApiResponse> {
        try {
            const token = await StorageUtil.getString(StorageKeys.ACCESS_TOKEN);
            const body = {};
            body[fieldName] = imageBase64;
            return await this.post(url, body, true);
        }
        catch (error) {
            console.error('[HttpUtil] Upload image failed:', JSON.stringify(error));
            return {
                success: false,
                error: '图片上传失败'
            };
        }
    }
}
export default HttpUtil.getInstance();
