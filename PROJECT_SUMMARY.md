# 家庭情绪管理系统 - 项目总结

## 项目概况

本项目基于您原有的树莓派表情识别项目,重新设计为一个完整的**家庭情绪管理系统**。

### 核心变化

| 维度 | 原项目 | 新项目 |
|------|--------|--------|
| 后端框架 | Flask | Django 5.0 |
| 数据库 | SQLite (简单) | SQLite (完整关系型) |
| Web端 | 简单HTML | Django模板系统 |
| 移动端 | 无 | 鸿蒙原生App (REST API) |
| 用户系统 | 简单用户表 | 三级权限体系 |
| 功能范围 | 表情识别+人脸识别 | 打卡+情绪管理+通知系统 |

---

## 系统架构

### 1. 技术栈

```
后端: Django 5.0 + SQLite + Django REST Framework
AI模型: TensorFlow + OpenCV
  - 人脸识别: MobileFaceNet (TFLite)
  - 表情识别: FER CNN模型 (从旧项目继承)
任务调度: Celery + Redis
Web前端: Django Templates + Bootstrap 5
移动端: 鸿蒙原生App (通过REST API对接)
```

### 2. 应用模块

项目采用Django的应用化设计:

- **users**: 用户管理、认证、人脸注册
- **families**: 家庭管理、邀请码系统
- **checkins**: 打卡任务、打卡记录
- **emotions**: 表情识别、情绪记录
- **notifications**: 通知系统 (邮件/站内信)

---

## 数据库设计

### 核心表

1. **users** - 用户表
   - 支持三种角色: super_admin, family_admin, family_member
   - 关联家庭和邀请人
   - 人脸注册状态

2. **families** - 家庭表
   - 家庭名称和唯一邀请码
   - 关联管理员
   - 成员数量限制

3. **invite_codes** - 邀请码表
   - 每个邀请码指定用户名
   - 支持过期时间和使用次数限制
   - 状态管理 (active/used/expired/revoked)

4. **checkin_tasks** - 打卡任务表
   - 灵活的任务类型 (daily/weekly/custom)
   - JSON配置: 调度、提醒、情绪阈值
   - 支持指定目标成员

5. **checkin_records** - 打卡记录表
   - 关联任务、用户、家庭
   - 记录人脸验证和表情分析结果
   - 打卡状态 (on_time/late/missed)

6. **emotion_records** - 表情记录表
   - 7种表情分类
   - 完整的概率分布
   - 关联打卡记录(可选)
   - AI分析结果

7. **face_encodings** - 人脸特征表
   - 存储特征向量 (Binary + JSON)
   - 支持多张人脸照片
   - 主要特征标记

8. **notifications** - 通知表
   - 多种通知类型 (email/sms/push/in_app)
   - 发送状态追踪
   - 关联业务记录

---

## 核心业务流程

### 1. 用户注册流程

```
家庭管理员生成邀请码
    ↓
邀请码发送给家庭成员
    ↓
成员输入邀请码注册
    ↓
设置密码
    ↓
注册人脸 (拍摄3-5张照片)
    ↓
提取特征并存储
    ↓
注册完成,加入家庭
```

### 2. 打卡流程

```
系统定时发送打卡提醒
    ↓
成员收到通知 (邮件/App推送)
    ↓
打开App,调用摄像头拍照
    ↓
后端: 人脸识别验证身份
    ↓
后端: 表情识别分析情绪
    ↓
保存打卡记录和表情数据
    ↓
判断: 
  - 表情异常 → 邮件通知管理员
  - 未打卡 → 定时任务检测并通知
```

### 3. 情绪预警流程

```
表情识别完成
    ↓
计算情绪评分
    ↓
判断:
  - 负面情绪 + 高置信度 → 立即通知
  - 连续多天异常 → 周报通知
  - 未打卡超时 → 缺勤通知
```

---

## API接口设计

### 认证相关

```
POST /api/v1/auth/login/              # 登录
POST /api/v1/auth/register/           # 注册
POST /api/v1/auth/refresh/            # 刷新Token
GET  /api/v1/auth/me/                 # 获取当前用户
POST /api/v1/auth/face/register/      # 注册人脸
POST /api/v1/auth/face/verify/        # 验证人脸
```

### 打卡相关

```
GET  /api/v1/checkins/my-tasks/       # 我的任务列表
POST /api/v1/checkins/submit/         # 提交打卡
GET  /api/v1/checkins/records/        # 打卡记录
GET  /api/v1/checkins/statistics/     # 统计数据
```

### 表情相关

```
POST /api/v1/emotions/analyze/        # 分析表情
GET  /api/v1/emotions/records/        # 情绪记录
GET  /api/v1/emotions/trends/         # 情绪趋势
```

完整API文档见 `README.md`

---

## AI模型继承

### 从旧项目继承的模型

1. **人脸识别模型**: `mobilefacenet.tflite`
   - 已从旧项目复制
   - 继续使用TFLite进行推理
   - 阈值: 0.55

2. **表情识别模型**: `fer.weights.h5` 或 `fer_model.h5`
   - 已从旧项目复制
   - 7种表情分类
   - 输入: 48x48灰度图

### 服务封装

创建了 `emotions/services.py`:

- `FaceRecognitionService`: 人脸识别服务
  - 特征提取
  - 人脸注册
  - 人脸匹配

- `EmotionRecognitionService`: 表情识别服务
  - 表情检测
  - 概率分布
  - AI分析文本生成

---

## 鸿蒙App对接

### 认证流程

1. 登录获取JWT Token
2. 后续请求携带Token
3. Token过期自动刷新

### 核心接口

1. **人脸注册**: `POST /api/v1/auth/face/register/`
   - 上传3-5张人脸照片
   - multipart/form-data

2. **打卡提交**: `POST /api/v1/checkins/submit/`
   - 上传照片
   - 返回人脸验证和表情分析结果

3. **任务列表**: `GET /api/v1/checkins/my-tasks/`
   - 获取今日打卡任务
   - 显示打卡状态

详细对接文档见 `README.md` 的"鸿蒙App对接说明"章节

---

## 邮件通知规则

系统会在以下情况发送邮件给家庭管理员:

1. **未打卡**: 超过计划时间30分钟未打卡
2. **表情异常**: 负面情绪且置信度>70%
3. **连续异常**: 连续3天表情不佳
4. **周报**: 每周一发送上周汇总

邮件配置:
- 使用Django内置邮件系统
- 支持SMTP (Gmail/QQ邮箱等)
- 模板位于 `templates/emails/`

---

## 项目文件结构

```
family-emotion-system/
├── config/                     # Django项目配置
│   ├── settings.py            # 核心配置 (已配置所有必要参数)
│   ├── urls.py                # 主路由
│   └── wsgi.py
├── users/                      # 用户应用
│   ├── models.py              # User模型 (三级权限)
│   ├── views.py               # Web视图
│   ├── api_views.py           # REST API视图 (需补充)
│   ├── urls.py                # Web路由
│   └── api_urls.py            # API路由
├── families/                   # 家庭应用
│   ├── models.py              # Family, InviteCode模型
│   ├── views.py               # (需创建)
│   ├── api_views.py           # (需创建)
│   ├── urls.py                # (需创建)
│   └── api_urls.py            # (需创建)
├── checkins/                   # 打卡应用
│   ├── models.py              # CheckinTask, CheckinRecord
│   ├── views.py               # (需创建)
│   ├── api_views.py           # (需创建)
│   ├── tasks.py               # Celery定时任务 (需创建)
│   ├── urls.py                # (需创建)
│   └── api_urls.py            # (需创建)
├── emotions/                   # 表情应用
│   ├── models.py              # EmotionRecord, FaceEncoding
│   ├── services.py            # AI服务 (已完成)
│   ├── views.py               # (需创建)
│   ├── api_views.py           # (需创建)
│   ├── urls.py                # (需创建)
│   └── api_urls.py            # (需创建)
├── notifications/              # 通知应用
│   ├── models.py              # Notification
│   ├── services.py            # 邮件发送服务 (需创建)
│   ├── tasks.py               # 异步通知任务 (需创建)
│   ├── views.py               # (需创建)
│   ├── urls.py                # (需创建)
│   └── api_urls.py            # (需创建)
├── templates/                  # Django模板
│   ├── base/
│   │   └── base.html          # 基础模板 (已创建)
│   ├── users/
│   │   ├── index.html         # 首页 (已创建)
│   │   ├── login.html         # (需创建)
│   │   ├── register.html      # (需创建)
│   │   └── profile.html       # (需创建)
│   ├── families/              # (需创建)
│   ├── checkins/              # (需创建)
│   └── emotions/              # (需创建)
├── static/                     # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── media/                      # 媒体文件
│   ├── faces_db/              # 人脸数据库
│   ├── emotion_photos/        # 表情照片
│   └── uploads/
├── ml_models/                  # AI模型
│   ├── mobilefacenet.tflite   # (已复制)
│   └── fer_model.h5           # (已复制)
├── manage.py
├── requirements.txt           # (已完成)
├── .env.example               # (已完成)
├── start.sh                   # 启动脚本 (已完成)
├── README.md                  # 完整文档 (已完成)
└── PROJECT_SUMMARY.md         # 本文档
```

---

## 当前完成度

### ✅ 已完成

1. **项目初始化**
   - Django项目创建
   - 所有应用创建 (users/families/checkins/emotions/notifications)
   - 虚拟环境和依赖配置

2. **配置文件**
   - `settings.py` 完整配置
   - REST Framework配置
   - JWT认证配置
   - CORS配置
   - 邮件配置
   - AI模型路径配置

3. **数据库模型**
   - ✅ User模型 (三级权限)
   - ✅ Family模型
   - ✅ InviteCode模型
   - ✅ CheckinTask模型
   - ✅ CheckinRecord模型
   - ✅ EmotionRecord模型
   - ✅ FaceEncoding模型
   - ✅ Notification模型

4. **AI服务**
   - ✅ FaceRecognitionService
   - ✅ EmotionRecognitionService
   - ✅ 模型文件复制

5. **路由配置**
   - ✅ 主路由 (config/urls.py)
   - ✅ 用户路由 (users/urls.py, users/api_urls.py)

6. **Web视图**
   - ✅ 用户视图 (登录/注册/资料等)

7. **模板**
   - ✅ 基础模板
   - ✅ 首页模板

8. **文档**
   - ✅ README.md (完整使用文档)
   - ✅ PROJECT_SUMMARY.md (本文档)
   - ✅ .env.example (环境变量示例)

9. **启动脚本**
   - ✅ start.sh

### ⬜ 待完成

1. **Web视图和模板** (优先级: 中)
   - families的views和templates
   - checkins的views和templates
   - emotions的views和templates
   - notifications的views和templates

2. **REST API视图** (优先级: 高 - 鸿蒙App需要)
   - users/api_views.py 补充完整
   - families/api_views.py
   - checkins/api_views.py
   - emotions/api_views.py
   - notifications/api_views.py

3. **定时任务** (优先级: 高)
   - checkins/tasks.py - 打卡提醒和检测
   - notifications/tasks.py - 邮件发送
   - Celery配置文件

4. **Admin后台** (优先级: 低)
   - 各个模型的admin注册
   - 自定义admin界面

5. **测试** (优先级: 中)
   - 单元测试
   - API测试

6. **部署配置** (优先级: 低)
   - Dockerfile
   - docker-compose.yml
   - Nginx配置

---

## 下一步工作建议

### 阶段1: 完成核心API (1-2天)

让鸿蒙App能够对接:

1. 完成 `users/api_views.py`
   - LoginAPIView
   - RegisterAPIView
   - RegisterFaceAPIView
   - VerifyFaceAPIView

2. 完成 `checkins/api_views.py`
   - MyTasksAPIView
   - SubmitCheckinAPIView
   - CheckinRecordsAPIView

3. 完成 `emotions/api_views.py`
   - AnalyzeEmotionAPIView
   - EmotionRecordsAPIView

### 阶段2: 完成定时任务 (1天)

实现打卡提醒和通知:

1. `checkins/tasks.py`
   - 打卡提醒任务
   - 未打卡检测任务

2. `notifications/services.py`
   - 邮件发送服务
   - 模板渲染

### 阶段3: 完成Web管理界面 (2-3天)

给家庭管理员使用:

1. 家庭管理页面
   - 成员列表
   - 邀请码管理
   - 打卡任务配置

2. 数据报表页面
   - 成员情绪趋势
   - 打卡统计
   - 异常记录

### 阶段4: 测试和优化 (1-2天)

1. API测试
2. 人脸识别准确率测试
3. 表情识别准确率测试
4. 性能优化

---

## 技术亮点

1. **三级权限体系**: 灵活的角色管理
2. **邀请码系统**: 安全的用户注册流程
3. **AI服务封装**: 模块化的ML模型管理
4. **前后端分离**: Django Templates + REST API
5. **异步任务**: Celery实现定时提醒和通知
6. **多端支持**: Web管理端 + 鸿蒙移动端

---

## 注意事项

### 1. AI模型文件

确保以下文件存在:
- `ml_models/mobilefacenet.tflite`
- `ml_models/fer_model.h5` 或 `fer.weights.h5`

如果缺失,从旧项目复制:
```bash
cp /path/to/old/project/mobilefacenet.tflite ml_models/
cp /path/to/old/project/fer.weights.h5 ml_models/
```

### 2. 环境变量

生产环境务必修改:
- `SECRET_KEY`: 使用随机生成的密钥
- `DEBUG`: 设置为False
- `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`: 配置真实邮箱
- `ALLOWED_HOSTS`: 添加域名

### 3. 数据库迁移

首次运行:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. 静态文件收集

生产环境部署:
```bash
python manage.py collectstatic
```

---

## 总结

本项目在您原有表情识别系统的基础上,扩展为一个完整的**家庭情绪管理平台**。

**核心优势**:
- 完整的用户体系和权限管理
- 灵活的打卡任务配置
- 智能的情绪预警机制
- 多端支持 (Web + 鸿蒙App)
- 继承原有的AI模型能力

**适用场景**:
- 家庭心理健康监护
- 老人/儿童情绪关怀
- 企业员工心理健康管理

项目框架已搭建完成,后续只需按照上述"下一步工作建议"完善各个模块即可投入使用。

---

**创建时间**: 2026-01-10  
**版本**: v1.0