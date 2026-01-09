# REST API 文档

## 基础信息

- **Base URL**: `http://your-domain.com/api/v1`
- **认证方式**: JWT (JSON Web Token)
- **Content-Type**: `application/json`

---

## 认证流程

### 1. 登录
```http
POST /auth/login/
```

**Request Body**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response (200)**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "testuser",
    "display_name": "测试用户",
    "role": "family_member",
    "face_registered": false,
    "family": {
      "id": 1,
      "name": "测试家庭"
    }
  }
}
```

### 2. 刷新Token
```http
POST /auth/refresh/
```

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. 后续请求携带Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 用户相关API

### 注册用户
```http
POST /auth/register/
```

**Request Body**:
```json
{
  "invite_code": "ABC12345",
  "password": "password123"
}
```

### 获取当前用户信息
```http
GET /auth/me/
```

### 注册人脸
```http
POST /auth/face/register/
Content-Type: multipart/form-data
```

**Form Data**:
- `image1`: File (必须)
- `image2`: File (可选)
- `image3`: File (可选)
- `image4`: File (可选)
- `image5`: File (可选)

**Response**:
```json
{
  "message": "人脸注册成功，已注册3张照片",
  "face_count": 3
}
```

### 验证人脸
```http
POST /auth/face/verify/
Content-Type: multipart/form-data
```

**Form Data**:
- `image`: File

---

## 打卡相关API

### 获取我的打卡任务
```http
GET /checkins/my-tasks/
```

**Response**:
```json
{
  "tasks": [
    {
      "id": 1,
      "task_name": "每日打卡",
      "task_type": "daily",
      "checked_today": false,
      "last_checkin": {
        "time": "2026-01-09T09:00:00Z",
        "status": "on_time",
        "emotion": "happy"
      }
    }
  ],
  "total": 1
}
```

### 提交打卡
```http
POST /checkins/submit/
Content-Type: multipart/form-data
```

**Form Data**:
- `task_id`: 1
- `photo`: File
- `location` (可选): `{"latitude": 39.9, "longitude": 116.4}`

**Response**:
```json
{
  "message": "打卡成功",
  "record_id": 123,
  "checkin_time": "2026-01-10T09:05:00Z",
  "status": "on_time",
  "face_verified": true,
  "emotion": {
    "emotion": "happy",
    "emotion_cn": "快乐",
    "confidence": 0.92,
    "probabilities": {
      "happy": {"name_cn": "快乐", "value": 0.92},
      "neutral": {"name_cn": "中性", "value": 0.05}
    },
    "ai_analysis": "您看起来心情愉悦,继续保持这种状态!"
  }
}
```

### 获取打卡记录
```http
GET /checkins/records/?days=7&page=1&page_size=20
```

### 打卡统计
```http
GET /checkins/statistics/?days=30
```

---

## 表情相关API

### 分析表情
```http
POST /emotions/analyze/
Content-Type: multipart/form-data
```

**Form Data**:
- `image`: File
- `save_photo`: true/false (是否保存记录)

### 获取表情记录
```http
GET /emotions/records/?days=7&page=1
```

### 表情统计
```http
GET /emotions/statistics/?days=30
```

### 情绪趋势
```http
GET /emotions/trends/?days=30
```

---

## 家庭管理API

### 生成邀请码（仅管理员）
```http
POST /families/invite/generate/
```

**Request Body**:
```json
{
  "username": "newuser",
  "display_name": "新用户",
  "expires_days": 7
}
```

### 邀请码列表（仅管理员）
```http
GET /families/invite/list/
```

### 家庭成员列表
```http
GET /families/members/
```

### 家庭详情
```http
GET /families/detail/
```

---

## 错误响应格式

```json
{
  "error": "错误描述信息"
}
```

常见状态码:
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器错误