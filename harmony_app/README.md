# 家庭情绪管理系统 - 鸿蒙App

## 项目说明

本项目是家庭情绪管理系统的鸿蒙原生客户端,使用ArkTS开发。

## 功能特性

- ✅ 邀请码直接登录(无需账号密码)
- ✅ 人脸注册
- ✅ 人脸打卡
- ✅ 情绪识别
- ✅ 历史记录查看

## 开发环境

- DevEco Studio 4.0+
- HarmonyOS API 9+
- ArkTS

## 项目结构

```
harmony_app/
├── entry/src/main/
│   ├── ets/
│   │   ├── entryability/
│   │   │   └── EntryAbility.ets          # 应用入口
│   │   ├── pages/
│   │   │   ├── Index.ets                  # 首页(邀请码登录)
│   │   │   ├── Home.ets                   # 主页(打卡入口)
│   │   │   ├── FaceRegister.ets           # 人脸注册
│   │   │   ├── Checkin.ets                # 打卡页面
│   │   │   └── History.ets                # 历史记录
│   │   ├── common/
│   │   │   ├── constants/
│   │   │   │   └── AppConstants.ets       # 常量定义
│   │   │   └── utils/
│   │   │       ├── HttpUtil.ets           # HTTP工具类
│   │   │       ├── StorageUtil.ets        # 存储工具类
│   │   │       └── CameraUtil.ets         # 相机工具类
│   │   └── models/
│   │       ├── User.ets                   # 用户模型
│   │       ├── CheckinTask.ets            # 打卡任务模型
│   │       └── CheckinRecord.ets          # 打卡记录模型
│   ├── resources/                         # 资源文件
│   └── module.json5                       # 模块配置
└── build-profile.json5                     # 构建配置
```

## 快速开始

### 1. 使用DevEco Studio创建项目

1. 打开DevEco Studio
2. 选择 "Create Project"
3. 选择 "Empty Ability"
4. 配置项目信息:
   - Project name: FamilyEmotionApp
   - Bundle name: com.family.emotion
   - Save location: 选择此目录
   - Compile SDK: API 9
   - Model: Stage

### 2. 复制代码文件

将本目录下的代码文件复制到DevEco Studio创建的项目中。

### 3. 配置API地址

修改 `ets/common/constants/AppConstants.ets` 中的API地址:

```typescript
export const API_BASE_URL = 'http://your-server-ip:8000'
```

### 4. 配置权限

在 `module.json5` 中已配置所需权限:
- ohos.permission.INTERNET
- ohos.permission.CAMERA
- ohos.permission.READ_MEDIA
- ohos.permission.WRITE_MEDIA

### 5. 运行应用

1. 连接HarmonyOS设备或启动模拟器
2. 点击 Run 按钮
3. 应用将安装并运行

## API接口说明

### 邀请码登录

```
POST /api/v1/auth/invite-login/
Content-Type: application/json

{
  "invite_code": "ABC12345"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user_FAMILY001_20260110120000",
    "display_name": "小明",
    "face_registered": false,
    "family": {
      "id": 1,
      "name": "张家"
    }
  },
  "invite_code": "ABC12345"
}
```

### 其他API

详见 `HARMONY_APP_DEV.md` 文档。

## 使用流程

### 1. 管理员生成邀请码

1. 管理员登录Web管理界面
2. 进入"家庭管理" > "邀请码管理"
3. 点击"生成新邀请码"
4. 填写家庭成员姓名(例如:小明)
5. 选择有效期(默认7天)
6. 系统自动生成邀请码(例如:ABC12345)

### 2. 家庭成员使用App

1. 安装鸿蒙App
2. 打开App,输入邀请码:ABC12345
3. 点击"登录",自动完成注册和登录
4. 首次登录提示"请先注册人脸"
5. 进入人脸注册页面,拍照注册人脸
6. 注册成功后,可以开始打卡

### 3. 日常打卡

1. 打开App,自动使用邀请码登录
2. 点击"开始打卡"
3. 摄像头自动拍照
4. 系统验证人脸并识别情绪
5. 显示打卡成功和当前情绪
6. 可查看历史打卡记录

## 技术特点

1. **无密码登录**: 使用邀请码直接登录,简化使用流程
2. **自动登录**: 本地保存邀请码,下次自动登录
3. **人脸识别**: 使用HarmonyOS相机API采集人脸
4. **情绪识别**: 后端AI模型分析情绪
5. **离线提示**: 网络异常时友好提示

## 注意事项

1. 邀请码请妥善保管,不要泄露给他人
2. 首次使用需要注册人脸
3. 打卡时需要正对摄像头
4. 确保网络连接正常
5. 授予相机和存储权限

## 故障排除

### 无法登录

- 检查邀请码是否正确
- 检查网络连接
- 检查API地址配置
- 检查邀请码是否过期

### 人脸注册失败

- 确保光线充足
- 正对摄像头
- 保持面部清晰可见
- 授予相机权限

### 打卡失败

- 检查是否已注册人脸
- 检查网络连接
- 检查打卡任务是否存在

## 开发计划

- [x] 邀请码登录
- [x] 人脸注册
- [x] 人脸打卡
- [x] 情绪识别
- [x] 历史记录
- [ ] 消息通知
- [ ] 情绪统计图表
- [ ] 离线缓存

## 联系方式

如有问题,请联系系统管理员。