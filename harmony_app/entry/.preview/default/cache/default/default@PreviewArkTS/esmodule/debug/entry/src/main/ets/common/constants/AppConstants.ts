/**
 * 应用常量定义
 */
// API配置
export const API_BASE_URL = 'http://192.168.1.100:8000'; // 修改为你的服务器地址
export const API_TIMEOUT = 30000; // 30秒超时
// API端点
export class ApiEndpoints {
    // 认证相关
    static readonly INVITE_LOGIN = '/api/v1/auth/invite-login/';
    static readonly TOKEN_REFRESH = '/api/v1/auth/refresh/';
    static readonly LOGOUT = '/api/v1/auth/logout/';
    static readonly CURRENT_USER = '/api/v1/auth/me/';
    // 人脸相关
    static readonly FACE_REGISTER = '/api/v1/auth/face/register/';
    static readonly FACE_VERIFY = '/api/v1/auth/face/verify/';
    // 打卡相关
    static readonly CHECKIN_TASKS = '/api/v1/checkins/tasks/';
    static readonly CHECKIN_CREATE = '/api/v1/checkins/create/';
    static readonly CHECKIN_RECORDS = '/api/v1/checkins/records/';
    // 情绪相关
    static readonly EMOTION_RECORDS = '/api/v1/emotions/records/';
}
// 存储键名
export class StorageKeys {
    static readonly INVITE_CODE = 'invite_code';
    static readonly ACCESS_TOKEN = 'access_token';
    static readonly REFRESH_TOKEN = 'refresh_token';
    static readonly USER_INFO = 'user_info';
    static readonly IS_FACE_REGISTERED = 'is_face_registered';
}
// 用户角色
export enum UserRole {
    SUPER_ADMIN = "super_admin",
    FAMILY_ADMIN = "family_admin",
    FAMILY_MEMBER = "family_member"
}
// 打卡状态
export enum CheckinStatus {
    ON_TIME = "on_time",
    LATE = "late",
    MAKEUP = "makeup"
}
// 情绪类型
export enum EmotionType {
    HAPPY = "happy",
    SAD = "sad",
    ANGRY = "angry",
    FEAR = "fear",
    SURPRISE = "surprise",
    DISGUST = "disgust",
    NEUTRAL = "neutral"
}
// 情绪中文映射
export const EMOTION_NAMES = {
    'happy': '😊 开心',
    'sad': '😢 难过',
    'angry': '😠 生气',
    'fear': '😨 恐惧',
    'surprise': '😲 惊讶',
    'disgust': '🤢 厌恶',
    'neutral': '😐 平静'
};
// 错误消息
export class ErrorMessages {
    static readonly NETWORK_ERROR = '网络连接失败,请检查网络设置';
    static readonly SERVER_ERROR = '服务器错误,请稍后重试';
    static readonly INVALID_INVITE_CODE = '邀请码无效或已过期';
    static readonly LOGIN_FAILED = '登录失败,请重试';
    static readonly FACE_REGISTER_FAILED = '人脸注册失败,请重试';
    static readonly CHECKIN_FAILED = '打卡失败,请重试';
    static readonly PERMISSION_DENIED = '权限被拒绝,请在设置中授予权限';
    static readonly CAMERA_ERROR = '相机启动失败';
}
// 应用配置
export class AppConfig {
    static readonly APP_NAME = '家庭情绪管理';
    static readonly APP_VERSION = '1.0.0';
    static readonly DEFAULT_AVATAR = '/common/images/default_avatar.png';
    // 图片质量配置
    static readonly IMAGE_QUALITY = 80; // JPEG质量 0-100
    static readonly IMAGE_MAX_SIZE = 1024 * 1024; // 1MB
    // 页面路由
    static readonly PAGE_INDEX = 'pages/Index';
    static readonly PAGE_HOME = 'pages/Home';
    static readonly PAGE_FACE_REGISTER = 'pages/FaceRegister';
    static readonly PAGE_CHECKIN = 'pages/Checkin';
    static readonly PAGE_HISTORY = 'pages/History';
}
