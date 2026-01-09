# 如何在DevEco Studio中打开项目

## 方法一：直接打开项目目录（推荐）

1. 启动 DevEco Studio
2. 点击菜单：**File → Open**
3. 选择本项目目录：`/Users/xiangbingzhou/nan/family-emotion-system/harmony_app`
4. 点击 **Open** 按钮

## 方法二：从欢迎页打开

1. 启动 DevEco Studio
2. 在欢迎页点击 **Open**
3. 导航到项目目录并选择
4. 点击 **Open**

## 首次打开后需要做的事情

### 1. 同步项目依赖
项目打开后，DevEco Studio 会自动检测并提示安装依赖：
- 等待 hvigor 依赖下载完成
- 如果没有自动开始，点击顶部的 **Sync Now** 按钮

### 2. 配置 SDK 路径
如果 `local.properties` 中的路径不正确，需要修改：
```properties
sdk.dir=/Applications/DevEco-Studio.app/Contents/sdk
nodejs.dir=/Applications/DevEco-Studio.app/Contents/tools/node
npm.dir=/Applications/DevEco-Studio.app/Contents/tools/node/lib/node_modules/npm
```

### 3. 配置后端 API 地址
编辑文件：`entry/src/main/ets/common/constants/AppConstants.ets`
```typescript
// 修改为你的后端地址
export const API_BASE_URL = 'http://你的电脑IP:8000';
```

### 4. 添加应用图标（可选）
替换以下占位符文件为真实图片：
- `AppScope/resources/base/media/app_icon.png` (应用图标)
- `entry/src/main/resources/base/media/icon.png` (模块图标)

推荐尺寸：256x256 像素

## 运行项目

### 使用模拟器
1. 点击顶部工具栏的设备选择器
2. 选择或创建一个 HarmonyOS 模拟器
3. 点击绿色 **Run** 按钮（▶）

### 使用真机
1. 开启手机的开发者模式和 USB 调试
2. 用数据线连接手机
3. 在设备选择器中选择你的设备
4. 点击 **Run** 按钮

## 常见问题

### Q: 提示 "Cannot resolve symbol"
**A:** 等待项目索引完成，或点击 **File → Invalidate Caches / Restart**

### Q: 提示 "SDK not found"
**A:** 检查 `local.properties` 中的 SDK 路径是否正确

### Q: hvigor 构建失败
**A:** 
1. 删除 `node_modules` 和 `oh_modules` 目录
2. 点击 **File → Sync** 重新同步

### Q: 运行时网络请求失败
**A:** 
1. 确保后端服务已启动（端口 8000）
2. 检查 AppConstants.ets 中的 API_BASE_URL 配置
3. 确保手机/模拟器与电脑在同一网络

## 项目结构说明

```
harmony_app/
├── AppScope/                    # 应用级配置
│   ├── app.json5               # 应用配置文件
│   └── resources/              # 应用级资源
├── entry/                      # 主模块
│   ├── src/main/
│   │   ├── ets/               # ArkTS 源码
│   │   │   ├── common/        # 通用工具和常量
│   │   │   ├── entryability/  # 应用入口
│   │   │   ├── models/        # 数据模型
│   │   │   └── pages/         # 页面组件
│   │   ├── module.json5       # 模块配置
│   │   └── resources/         # 资源文件
│   ├── build-profile.json5    # 模块构建配置
│   └── hvigorfile.ts          # 模块构建脚本
├── hvigor/                     # 构建工具配置
├── build-profile.json5         # 项目构建配置
├── hvigorfile.ts              # 项目构建脚本
└── oh-package.json5           # 依赖管理
```

## 下一步

项目成功运行后，可以：
1. 使用邀请码登录（从 Web 端生成）
2. 注册人脸信息
3. 进行情绪打卡
4. 查看历史记录