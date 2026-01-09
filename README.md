# 家庭情绪管理系统

基于Django + SQLite的家庭情绪管理系统，支持人脸识别、表情识别、打卡管理和邮件通知。

## 系统架构

- **后端**: Django 5.0 + SQLite
- **Web管理端**: Django模板
- **移动端**: 鸿蒙原生App (通过REST API对接)
- **AI模型**: 
  - 人脸识别: MobileFaceNet (TFLite)
  - 表情识别: FER CNN模型

## 用户体系

1. **超级管理员**: 管理整个系统,创建家庭
2. **家庭管理员**: 管理家庭成员,设置打卡任务,查看报表
3. **家庭成员**: 完成打卡任务,查看自己的情绪记录

## 核心功能

### 1. 用户管理
- 邀请码注册系统
- 人脸识别认证
- 三级权限管理

### 2. 家庭管理
- 家庭创建与配置
- 成员邀请与管理
- 家庭数据统计

### 3. 打卡系统
- 灵活的打卡任务配置(每日/每周/自定义)
- 人脸验证 + 表情识别
- 打卡提醒(邮件/站内信)
- 未打卡通知

### 4. 表情识别
- 7种表情识别(愤怒/厌恶/恐惧/快乐/悲伤/惊讶/中性)
- 表情历史记录
- 情绪趋势分析
- 异常情绪预警

### 5. 通知系统
- 邮件通知(未打卡/表情异常)
- 站内消息
- 定时任务调度

## 项目结构

```
family-emotion-system/
├── config/                  # Django项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                   # 用户管理应用
│   ├── models.py           # 用户模型
│   ├── views.py            # Web视图
│   ├── api_views.py        # API视图
│   ├── urls.py             # Web路由
│   └── api_urls.py         # API路由
├── families/                # 家庭管理应用
├── checkins/                # 打卡管理应用
├── emotions/                # 表情识别应用
│   └── services.py         # AI服务
├── notifications/           # 通知应用
├── templates/               # Django模板
│   ├── base/               # 基础模板
│   ├── users/              # 用户模板
│   ├── families/           # 家庭模板
│   └── checkins/           # 打卡模板
├── static/                  # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # 媒体文件
│   ├── faces_db/           # 人脸数据库
│   ├── emotion_photos/     # 表情照片
│   └── uploads/            # 其他上传
├── ml_models/               # AI模型文件
│   ├── mobilefacenet.tflite
│   └── fer_model.h5
├── manage.py
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# Python 3.9+
python3 --version

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑.env文件,配置必要参数
# SECRET_KEY, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD等
```

### 3. 初始化数据库

```bash
# 创建数据库迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
```

### 4. 准备AI模型

```bash
# 将以下模型文件放到 ml_models/ 目录:
# - mobilefacenet.tflite  (人脸识别)
# - fer_model.h5 或 fer.weights.h5  (表情识别)

# 如果没有模型文件,可以从旧项目复制:
cp /path/to/old/project/mobilefacenet.tflite ml_models/
cp /path/to/old/project/fer.weights.h5 ml_models/
```

### 5. 启动开发服务器

```bash
# 启动Django服务
python manage.py runserver 0.0.0.0:8000

# 访问地址:
# Web管理端: http://localhost:8000
# 管理后台: http://localhost:8000/admin
# API文档: http://localhost:8000/api/docs (如果安装了drf-spectacular)
```

### 6. (可选)启动Celery任务队列

```bash
# 启动Redis (用于Celery)
redis-server

# 启动Celery Worker
celery -A config worker -l info

# 启动Celery Beat (定时任务)
celery -A config beat -l info
```

## API接口

### 认证接口

```
POST /api/v1/auth/login/              # 登录
POST /api/v1/auth/register/           # 注册
POST /api/v1/auth/refresh/            # 刷新Token
POST /api/v1/auth/logout/             # 登出
GET  /api/v1/auth/me/                 # 获取当前用户信息
PUT  /api/v1/auth/me/update/          # 更新用户信息
POST /api/v1/auth/face/register/      # 注册人脸
POST /api/v1/auth/face/verify/        # 验证人脸
```

### 家庭接口

```
GET    /api/v1/families/              # 获取家庭列表
POST   /api/v1/families/              # 创建家庭
GET    /api/v1/families/{id}/         # 获取家庭详情
PUT    /api/v1/families/{id}/         # 更新家庭
DELETE /api/v1/families/{id}/         # 删除家庭
GET    /api/v1/families/{id}/members/ # 获取家庭成员
POST   /api/v1/families/invite/       # 生成邀请码
```

### 打卡接口

```
GET  /api/v1/checkins/tasks/          # 获取打卡任务
POST /api/v1/checkins/tasks/          # 创建打卡任务
GET  /api/v1/checkins/my-tasks/       # 获取我的任务
POST /api/v1/checkins/submit/         # 提交打卡
GET  /api/v1/checkins/records/        # 获取打卡记录
GET  /api/v1/checkins/statistics/     # 打卡统计
```

### 表情接口

```
POST /api/v1/emotions/analyze/        # 分析表情
GET  /api/v1/emotions/records/        # 获取表情记录
GET  /api/v1/emotions/statistics/     # 表情统计
GET  /api/v1/emotions/trends/         # 情绪趋势
```

## 鸿蒙App对接说明

### 1. 认证流程

```typescript
// 1. 登录获取Token
POST /api/v1/auth/login/
Body: {
  "username": "string",
  "password": "string"
}
Response: {
  "access": "jwt_token",
  "refresh": "refresh_token",
  "user": { ... }
}

// 2. 后续请求携带Token
Headers: {
  "Authorization": "Bearer <access_token>"
}

// 3. Token过期刷新
POST /api/v1/auth/refresh/
Body: {
  "refresh": "refresh_token"
}
```

### 2. 人脸注册

```typescript
POST /api/v1/auth/face/register/
Content-Type: multipart/form-data
Body:
  - image1: File (人脸照片1)
  - image2: File (人脸照片2)
  - image3: File (人脸照片3)

Response: {
  "success": true,
  "message": "人脸注册成功",
  "face_count": 3
}
```

### 3. 打卡提交

```typescript
POST /api/v1/checkins/submit/
Content-Type: multipart/form-data
Body:
  - task_id: number
  - photo: File (打卡照片)
  - location: JSON (可选,位置信息)

Response: {
  "success": true,
  "record_id": 123,
  "face_verified": true,
  "emotion": {
    "emotion": "happy",
    "emotion_cn": "快乐",
    "confidence": 0.92,
    "probabilities": { ... }
  }
}
```

## 邮件通知规则

系统会在以下情况发送邮件通知给家庭管理员:

1. **未打卡提醒**: 超过计划时间30分钟未打卡
2. **表情异常警报**: 检测到负面情绪(悲伤/愤怒等)且置信度>70%
3. **连续异常**: 连续3天表情状态不佳
4. **每周汇总**: 每周一发送上周情绪报告

## 开发说明

### 添加新的打卡任务类型

1. 在 `checkins/models.py` 的 `CheckinTask.TYPE_CHOICES` 添加新类型
2. 在 `checkins/tasks.py` 添加对应的调度逻辑
3. 在Web模板和API中支持新类型

### 自定义表情分析

修改 `emotions/services.py` 中的 `EmotionRecognitionService._generate_analysis` 方法

### 修改邮件模板

邮件模板位于 `templates/emails/` 目录

## 部署

### 生产环境配置

```bash
# 1. 设置环境变量
export DEBUG=False
export SECRET_KEY=<your-secret-key>
export ALLOWED_HOSTS=yourdomain.com

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 使用Gunicorn运行
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# 4. 使用Nginx反向代理
# 配置文件示例见 deployment/nginx.conf
```

### Docker部署

```bash
# 构建镜像
docker build -t family-emotion-system .

# 运行容器
docker run -d -p 8000:8000 \
  -v ./media:/app/media \
  -v ./db.sqlite3:/app/db.sqlite3 \
  --env-file .env \
  family-emotion-system
```

## 故障排查

### 1. 模型加载失败

```
错误: [WARNING] 人脸识别模型未加载
解决: 确保ml_models/目录下有模型文件,检查文件路径配置
```

### 2. 邮件发送失败

```
错误: SMTPAuthenticationError
解决: 检查EMAIL_HOST_USER和EMAIL_HOST_PASSWORD配置
      Gmail需要使用应用专用密码而非账户密码
```

### 3. 静态文件404

```
错误: 静态文件无法加载
解决: 运行 python manage.py collectstatic
      检查STATIC_ROOT和STATIC_URL配置
```

## 许可证

MIT License

## 联系方式

如有问题,请提Issue或联系开发团队。

---

**最后更新**: 2026-01-10