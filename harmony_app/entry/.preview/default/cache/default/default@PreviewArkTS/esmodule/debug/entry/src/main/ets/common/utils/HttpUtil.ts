import http from "@ohos:net.http";
import { API_BASE_URL, API_TIMEOUT, StorageKeys, USE_MOCK_DATA } from "@bundle:com.family.emotion/entry/ets/common/constants/AppConstants";
import StorageUtil from "@bundle:com.family.emotion/entry/ets/common/utils/StorageUtil";
import MockData from "@bundle:com.family.emotion/entry/ets/common/utils/MockData";
// 定义请求头类型
class RequestHeaders {
    'Content-Type': string = 'application/json';
    'Authorization'?: string;
}
// 定义请求选项接口
interface RequestOptions {
    method?: http.RequestMethod;
    headers?: Record<string, string>;
    body?: any;
    needAuth?: boolean;
}
// 定义API响应接口
interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    status?: number;
}
// 定义响应数据接口
interface ResponseData {
    access?: string;
    error?: string;
    message?: string;
}
class HttpUtil {
    private static instance: HttpUtil | null = null;
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
    async request<T>(url: string, options: RequestOptions): Promise<ApiResponse<T>> {
        const method = options.method ?? http.RequestMethod.GET;
        const headers = options.headers ?? {};
        const body: any | null = options.body ?? null;
        const needAuth = options.needAuth ?? true;
        // 如果启用Mock模式,直接返回Mock数据
        if (USE_MOCK_DATA) {
            console.info('[HttpUtil] ========== USING MOCK DATA ==========');
            console.info(`[HttpUtil] Mock Request: ${method} ${url}`);
            console.info(`[HttpUtil] Mock Body: ${JSON.stringify(body)}`);
            const methodStr = this.getMethodString(method);
            const mockResult = await MockData.getMockData(url, methodStr, body ?? undefined) as ApiResponse<T>;
            console.info(`[HttpUtil] Mock Response: ${JSON.stringify(mockResult)}`);
            return mockResult;
        }
        try {
            // 创建HTTP请求
            const httpRequest = http.createHttp();
            // 构建完整URL
            const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
            // 构建请求头
            const requestHeaders: Record<string, string> = {
                'Content-Type': 'application/json'
            };
            // 合并自定义头
            Object.keys(headers).forEach((key: string) => {
                requestHeaders[key] = headers[key];
            });
            // 如果需要认证,添加Token
            if (needAuth) {
                const token = await StorageUtil.getString(StorageKeys.ACCESS_TOKEN);
                if (token) {
                    requestHeaders['Authorization'] = `Bearer ${token}`;
                }
            }
            // 构建请求选项
            const requestOptions: http.HttpRequestOptions = {
                method: method,
                header: requestHeaders,
                readTimeout: API_TIMEOUT,
                connectTimeout: API_TIMEOUT,
                extraData: body ? JSON.stringify(body) : undefined
            };
            console.info(`[HttpUtil] Request: ${method} ${fullUrl}`);
            // 发送请求
            const response = await httpRequest.request(fullUrl, requestOptions);
            console.info(`[HttpUtil] Response status: ${response.responseCode}`);
            // 销毁请求对象
            httpRequest.destroy();
            // 处理响应
            if (response.responseCode === 200 || response.responseCode === 201) {
                const data: T = typeof response.result === 'string'
                    ? JSON.parse(response.result as string) as T
                    : response.result as T;
                return {
                    success: true,
                    data: data,
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
                const errorData: ResponseData = typeof response.result === 'string'
                    ? JSON.parse(response.result as string) as ResponseData
                    : response.result as ResponseData;
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
    async get<T>(url: string, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: http.RequestMethod.GET, needAuth: needAuth });
    }
    /**
     * POST请求
     */
    async post<T>(url: string, body: any, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: http.RequestMethod.POST, body: body, needAuth: needAuth });
    }
    /**
     * PUT请求
     */
    async put<T>(url: string, body: any, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: http.RequestMethod.PUT, body: body, needAuth: needAuth });
    }
    /**
     * DELETE请求
     */
    async delete<T>(url: string, needAuth: boolean = true): Promise<ApiResponse<T>> {
        return await this.request<T>(url, { method: http.RequestMethod.DELETE, needAuth: needAuth });
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
            const body: any = {
                'refresh': refreshToken
            };
            const response = await this.post<ResponseData>('/api/v1/auth/refresh/', body, false);
            if (response.success && response.data && response.data.access) {
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
    async uploadImage(url: string, imageBase64: string, fieldName: string = 'photo'): Promise<ApiResponse<any>> {
        try {
            const body: any = {};
            body[fieldName] = imageBase64;
            return await this.post<any>(url, body, true);
        }
        catch (error) {
            console.error('[HttpUtil] Upload image failed:', JSON.stringify(error));
            return {
                success: false,
                error: '图片上传失败'
            };
        }
    }
    /**
     * 将HTTP方法枚举转为字符串
     */
    private getMethodString(method: http.RequestMethod): string {
        switch (method) {
            case http.RequestMethod.GET:
                return 'GET';
            case http.RequestMethod.POST:
                return 'POST';
            case http.RequestMethod.PUT:
                return 'PUT';
            case http.RequestMethod.DELETE:
                return 'DELETE';
            default:
                return 'GET';
        }
    }
}
export default HttpUtil.getInstance();
