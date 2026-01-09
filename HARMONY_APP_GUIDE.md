# 鸿蒙App开发指南

## 项目创建

### 1. 使用DevEco Studio创建工程

1. 打开DevEco Studio
2. 新建项目 → 选择"Empty Ability"模板
3. 项目信息:
   - 项目名: FamilyEmotionApp
   - Bundle name: com.family.emotion
   - 开发语言: ArkTS
   - Minimum API: 9

### 2. 项目结构

```
FamilyEmotionApp/
├── entry/src/main/
│   ├── ets/
│   │   ├── entryability/
│   │   │   └── EntryAbility.ts
│   │   ├── pages/
│   │   │   ├── Login.ets          # 登录页
│   │   │   ├── Register.ets       # 注册页
│   │   │   ├── FaceRegister.ets   # 人脸注册页
│   │   │   ├── Home.ets           # 首页(任务列表)
│   │   │   ├── Checkin.ets        # 打卡页
│   │   │   ├── Records.ets        # 历史记录
│   │   │   └── Profile.ets        # 个人中心
│   │   ├── common/
│   │   │   ├── utils/
│   │   │   │   ├── HttpUtil.ets   # HTTP请求工具
│   │   │   │   └── StorageUtil.ets # 存储工具
│   │   │   └── constants/
│   │   │       └── ApiConfig.ets  # API配置
│   │   └── models/
│   │       ├── User.ets
│   │       ├── Task.ets
│   │       └── CheckinRecord.ets
│   └── resources/
└── oh-package.json5
```

---

## 核心代码示例

### 1. API配置 (ApiConfig.ets)

```typescript
export class ApiConfig {
  // 后端服务地址
  static readonly BASE_URL = 'http://your-domain.com/api/v1';
  
  // API端点
  static readonly LOGIN = '/auth/login/';
  static readonly REGISTER = '/auth/register/';
  static readonly FACE_REGISTER = '/auth/face/register/';
  static readonly MY_TASKS = '/checkins/my-tasks/';
  static readonly SUBMIT_CHECKIN = '/checkins/submit/';
  static readonly EMOTION_RECORDS = '/emotions/records/';
}
```

### 2. HTTP工具类 (HttpUtil.ets)

```typescript
import http from '@ohos.net.http';
import { ApiConfig } from '../constants/ApiConfig';
import { StorageUtil } from './StorageUtil';

export class HttpUtil {
  // GET请求
  static async get(url: string): Promise<any> {
    const token = await StorageUtil.getToken();
    
    let httpRequest = http.createHttp();
    let response = await httpRequest.request(
      ApiConfig.BASE_URL + url,
      {
        method: http.RequestMethod.GET,
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    httpRequest.destroy();
    return JSON.parse(response.result as string);
  }
  
  // POST请求
  static async post(url: string, data: any): Promise<any> {
    const token = await StorageUtil.getToken();
    
    let httpRequest = http.createHttp();
    let response = await httpRequest.request(
      ApiConfig.BASE_URL + url,
      {
        method: http.RequestMethod.POST,
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        extraData: JSON.stringify(data)
      }
    );
    
    httpRequest.destroy();
    return JSON.parse(response.result as string);
  }
  
  // 上传文件
  static async uploadFile(url: string, filePath: string, fieldName: string = 'image'): Promise<any> {
    const token = await StorageUtil.getToken();
    
    let httpRequest = http.createHttp();
    let response = await httpRequest.request(
      ApiConfig.BASE_URL + url,
      {
        method: http.RequestMethod.POST,
        header: {
          'Authorization': `Bearer ${token}`
        },
        multiFormDataList: [
          {
            name: fieldName,
            contentType: 'image/jpeg',
            filePath: filePath
          }
        ]
      }
    );
    
    httpRequest.destroy();
    return JSON.parse(response.result as string);
  }
}
```

### 3. 存储工具类 (StorageUtil.ets)

```typescript
import dataPreferences from '@ohos.data.preferences';

export class StorageUtil {
  private static preferences: dataPreferences.Preferences;
  
  // 初始化
  static async init(context: Context) {
    this.preferences = await dataPreferences.getPreferences(context, 'app_storage');
  }
  
  // 保存Token
  static async saveToken(accessToken: string, refreshToken: string) {
    await this.preferences.put('access_token', accessToken);
    await this.preferences.put('refresh_token', refreshToken);
    await this.preferences.flush();
  }
  
  // 获取Token
  static async getToken(): Promise<string> {
    return await this.preferences.get('access_token', '') as string;
  }
  
  // 清除Token
  static async clearToken() {
    await this.preferences.delete('access_token');
    await this.preferences.delete('refresh_token');
    await this.preferences.flush();
  }
  
  // 保存用户信息
  static async saveUser(user: any) {
    await this.preferences.put('user', JSON.stringify(user));
    await this.preferences.flush();
  }
  
  // 获取用户信息
  static async getUser(): Promise<any> {
    const userStr = await this.preferences.get('user', '') as string;
    return userStr ? JSON.parse(userStr) : null;
  }
}
```

### 4. 登录页面 (Login.ets)

```typescript
import router from '@ohos.router';
import { HttpUtil } from '../common/utils/HttpUtil';
import { StorageUtil } from '../common/utils/StorageUtil';
import { ApiConfig } from '../common/constants/ApiConfig';

@Entry
@Component
struct Login {
  @State username: string = '';
  @State password: string = '';
  @State loading: boolean = false;
  
  async onLogin() {
    if (!this.username || !this.password) {
      promptAction.showToast({ message: '请输入用户名和密码' });
      return;
    }
    
    this.loading = true;
    
    try {
      const response = await HttpUtil.post(ApiConfig.LOGIN, {
        username: this.username,
        password: this.password
      });
      
      // 保存Token和用户信息
      await StorageUtil.saveToken(response.access, response.refresh);
      await StorageUtil.saveUser(response.user);
      
      promptAction.showToast({ message: '登录成功' });
      
      // 跳转到首页
      router.replaceUrl({ url: 'pages/Home' });
      
    } catch (error) {
      promptAction.showToast({ message: '登录失败: ' + error });
    } finally {
      this.loading = false;
    }
  }
  
  build() {
    Column() {
      Text('家庭情绪管理')
        .fontSize(32)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 100, bottom: 50 })
      
      TextInput({ placeholder: '用户名' })
        .width('80%')
        .height(50)
        .onChange((value) => { this.username = value; })
      
      TextInput({ placeholder: '密码' })
        .width('80%')
        .height(50)
        .type(InputType.Password)
        .margin({ top: 20 })
        .onChange((value) => { this.password = value; })
      
      Button(this.loading ? '登录中...' : '登录')
        .width('80%')
        .height(50)
        .margin({ top: 30 })
        .enabled(!this.loading)
        .onClick(() => this.onLogin())
      
      Text('还没有账号？使用邀请码注册')
        .fontSize(14)
        .fontColor(Color.Blue)
        .margin({ top: 20 })
        .onClick(() => {
          router.pushUrl({ url: 'pages/Register' });
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

### 5. 打卡页面 (Checkin.ets)

```typescript
import camera from '@ohos.multimedia.camera';
import image from '@ohos.multimedia.image';
import { HttpUtil } from '../common/utils/HttpUtil';
import { ApiConfig } from '../common/constants/ApiConfig';

@Entry
@Component
struct Checkin {
  @State taskId: number = 0;
  @State photoPath: string = '';
  @State analyzing: boolean = false;
  
  private cameraManager: camera.CameraManager;
  private cameraInput: camera.CameraInput;
  
  async takePhoto() {
    try {
      // 调用摄像头拍照
      let context = getContext(this) as common.UIAbilityContext;
      this.cameraManager = camera.getCameraManager(context);
      
      // 创建相机输入
      let cameras = this.cameraManager.getSupportedCameras();
      this.cameraInput = this.cameraManager.createCameraInput(cameras[0]);
      
      // 拍照并保存
      // ... 相机API调用代码 ...
      
      // 提交打卡
      await this.submitCheckin();
      
    } catch (error) {
      promptAction.showToast({ message: '拍照失败: ' + error });
    }
  }
  
  async submitCheckin() {
    this.analyzing = true;
    
    try {
      const response = await HttpUtil.uploadFile(
        ApiConfig.SUBMIT_CHECKIN + `?task_id=${this.taskId}`,
        this.photoPath,
        'photo'
      );
      
      // 显示结果
      AlertDialog.show({
        title: '打卡成功',
        message: `
          状态: ${response.status}
          人脸验证: ${response.face_verified ? '通过' : '未通过'}
          表情: ${response.emotion?.emotion_cn}
          置信度: ${(response.emotion?.confidence * 100).toFixed(1)}%
          AI分析: ${response.emotion?.ai_analysis}
        `,
        confirm: {
          value: '确定',
          action: () => {
            router.back();
          }
        }
      });
      
    } catch (error) {
      promptAction.showToast({ message: '打卡失败: ' + error });
    } finally {
      this.analyzing = false;
    }
  }
  
  build() {
    Column() {
      Text('打卡')
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 20 })
      
      // 相机预览区域
      XComponent({
        id: 'camera_preview',
        type: 'surface',
        controller: this.xComponentController
      })
        .width('100%')
        .height('60%')
        .margin({ top: 20 })
      
      Button(this.analyzing ? '分析中...' : '拍照打卡')
        .width('80%')
        .height(50)
        .margin({ top: 30 })
        .enabled(!this.analyzing)
        .onClick(() => this.takePhoto())
    }
    .width('100%')
    .height('100%')
  }
}
```

---

## 权限配置

在 `module.json5` 中添加:

```json
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.CAMERA"
      },
      {
        "name": "ohos.permission.WRITE_MEDIA"
      },
      {
        "name": "ohos.permission.READ_MEDIA"
      }
    ]
  }
}
```

---

## 测试清单

### 功能测试
- [ ] 登录功能
- [ ] 邀请码注册
- [ ] 人脸注册(3-5张照片)
- [ ] 任务列表加载
- [ ] 拍照打卡
- [ ] 人脸验证
- [ ] 表情识别
- [ ] 历史记录查看
- [ ] Token刷新

### 性能测试
- [ ] 网络请求耗时
- [ ] 图片上传速度
- [ ] AI分析响应时间

### 兼容性测试
- [ ] 不同鸿蒙版本
- [ ] 不同设备分辨率
- [ ] 网络异常处理

---

## 常见问题

### 1. 网络请求跨域问题
后端已配置CORS,确保Django settings中:
```python
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境
```

### 2. 图片上传大小限制
后端限制: 10MB  
建议压缩后上传

### 3. Token过期处理
收到401错误时,使用refresh token刷新access token

---

祝开发顺利！🎉