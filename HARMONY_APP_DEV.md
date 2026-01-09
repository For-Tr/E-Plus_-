# 鸿蒙App开发指南 - 家庭情绪管理系统

## 项目概述

本文档指导开发者如何开发与家庭情绪管理系统后端API对接的鸿蒙原生App。

---

## API基础信息

### 服务器地址
- 开发环境: `http://localhost:8000`
- 生产环境: `https://your-domain.com`

### API版本
- v1: `/api/v1/`

### 认证方式
- JWT Token认证
- Header: `Authorization: Bearer <access_token>`

---

## 开发流程

### Phase 4.1: 创建鸿蒙项目

1. 使用DevEco Studio创建新项目
2. 选择Empty Ability模板
3. 配置项目信息:
   - 项目名称: FamilyEmotionApp
   - 包名: com.family.emotion
   - API版本: API 9+

### 项目结构建议

```
FamilyEmotionApp/
├── entry/
│   └── src/
│       └── main/
│           ├── ets/
│           │   ├── entryability/
│           │   ├── pages/
│           │   │   ├── Index.ets          # 首页
│           │   │   ├── Login.ets          # 登录页
│           │   │   ├── Register.ets       # 注册页
│           │   │   ├── FaceRegister.ets   # 人脸注册
│           │   │   ├── Checkin.ets        # 打卡页
│           │   │   ├── History.ets        # 历史记录
│           │   │   └── Profile.ets        # 个人资料
│           │   ├── services/
│           │   │   ├── ApiService.ets     # API服务
│           │   │   ├── AuthService.ets    # 认证服务
│           │   │   └── StorageService.ets # 本地存储
│           │   └── models/
│           │       ├── User.ets
│           │       ├── Task.ets
│           │       └── Record.ets
│           └── resources/
└── oh_modules/
```

---

## Phase 4.2: 登录功能

### 1. 创建API服务基类

**services/ApiService.ets:**

```typescript
import http from '@ohos.net.http';

export class ApiService {
  private baseUrl: string = 'http://your-server:8000';
  private accessToken: string = '';

  setAccessToken(token: string) {
    this.accessToken = token;
  }

  async request(method: string, endpoint: string, data?: any): Promise<any> {
    const httpRequest = http.createHttp();
    
    const options: http.HttpRequestOptions = {
      method: method as http.RequestMethod,
      header: {
        'Content-Type': 'application/json',
        'Authorization': this.accessToken ? `Bearer ${this.accessToken}` : ''
      },
      extraData: data ? JSON.stringify(data) : undefined
    };

    try {
      const response = await httpRequest.request(`${this.baseUrl}${endpoint}`, options);
      const result = JSON.parse(response.result.toString());
      httpRequest.destroy();
      return result;
    } catch (error) {
      httpRequest.destroy();
      throw error;
    }
  }

  async get(endpoint: string): Promise<any> {
    return this.request('GET', endpoint);
  }

  async post(endpoint: string, data: any): Promise<any> {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint: string, data: any): Promise<any> {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint: string): Promise<any> {
    return this.request('DELETE', endpoint);
  }
}

export const apiService = new ApiService();
```

### 2. 创建认证服务

**services/AuthService.ets:**

```typescript
import { apiService } from './ApiService';
import preferences from '@ohos.data.preferences';

export class AuthService {
  private preferences: preferences.Preferences | null = null;

  async initialize() {
    this.preferences = await preferences.getPreferences(
      getContext(this), 
      'AuthStorage'
    );
  }

  async login(username: string, password: string): Promise<any> {
    try {
      const result = await apiService.post('/api/v1/auth/login/', {
        username,
        password
      });

      // 保存token
      await this.saveToken(result.access, result.refresh);
      apiService.setAccessToken(result.access);

      return result;
    } catch (error) {
      throw new Error('登录失败');
    }
  }

  async saveToken(accessToken: string, refreshToken: string) {
    if (this.preferences) {
      await this.preferences.put('access_token', accessToken);
      await this.preferences.put('refresh_token', refreshToken);
      await this.preferences.flush();
    }
  }

  async getAccessToken(): Promise<string | null> {
    if (this.preferences) {
      return await this.preferences.get('access_token', '') as string;
    }
    return null;
  }

  async logout() {
    if (this.preferences) {
      await this.preferences.delete('access_token');
      await this.preferences.delete('refresh_token');
      await this.preferences.flush();
    }
  }

  async isLoggedIn(): Promise<boolean> {
    const token = await this.getAccessToken();
    return !!token;
  }
}

export const authService = new AuthService();
```

### 3. 创建登录页面

**pages/Login.ets:**

```typescript
import router from '@ohos.router';
import { authService } from '../services/AuthService';

@Entry
@Component
struct Login {
  @State username: string = '';
  @State password: string = '';
  @State isLoading: boolean = false;
  @State errorMessage: string = '';

  async handleLogin() {
    if (!this.username || !this.password) {
      this.errorMessage = '请输入用户名和密码';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    try {
      await authService.initialize();
      const result = await authService.login(this.username, this.password);
      
      // 登录成功,跳转到首页
      router.replaceUrl({
        url: 'pages/Index',
        params: { user: result.user }
      });
    } catch (error) {
      this.errorMessage = '登录失败,请检查用户名和密码';
    } finally {
      this.isLoading = false;
    }
  }

  build() {
    Column() {
      Text('家庭情绪管理系统')
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 40 })

      TextInput({ placeholder: '用户名' })
        .width('80%')
        .margin({ bottom: 20 })
        .onChange((value: string) => {
          this.username = value;
        })

      TextInput({ placeholder: '密码' })
        .width('80%')
        .type(InputType.Password)
        .margin({ bottom: 10 })
        .onChange((value: string) => {
          this.password = value;
        })

      if (this.errorMessage) {
        Text(this.errorMessage)
          .fontSize(14)
          .fontColor(Color.Red)
          .margin({ bottom: 20 })
      }

      Button(this.isLoading ? '登录中...' : '登录')
        .width('80%')
        .height(45)
        .margin({ top: 20 })
        .enabled(!this.isLoading)
        .onClick(() => {
          this.handleLogin();
        })

      Row() {
        Text('还没有账号? ')
          .fontSize(14)
        Text('注册')
          .fontSize(14)
          .fontColor('#007AFF')
          .onClick(() => {
            router.pushUrl({ url: 'pages/Register' });
          })
      }
      .margin({ top: 20 })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#F5F5F5')
  }
}
```

---

## Phase 4.3: 人脸注册

### 1. 请求相机权限

**module.json5中添加权限:**

```json
{
  "requestPermissions": [
    {
      "name": "ohos.permission.CAMERA",
      "reason": "用于拍摄人脸照片"
    },
    {
      "name": "ohos.permission.WRITE_MEDIA",
      "reason": "用于保存照片"
    }
  ]
}
```

### 2. 创建人脸注册页面

**pages/FaceRegister.ets:**

```typescript
import camera from '@ohos.multimedia.camera';
import image from '@ohos.multimedia.image';
import { apiService } from '../services/ApiService';

@Entry
@Component
struct FaceRegister {
  @State photoCount: number = 0;
  @State photos: string[] = [];
  @State isRegistering: boolean = false;
  private surfaceId: string = '';

  async capturePhoto() {
    // 拍照逻辑
    // 此处需要实现相机拍照功能
    this.photoCount++;
    // 保存照片到photos数组
  }

  async registerFaces() {
    if (this.photos.length < 3) {
      // 提示至少需要3张照片
      return;
    }

    this.isRegistering = true;

    try {
      // 将照片转换为base64
      const formData = new FormData();
      this.photos.forEach((photo, index) => {
        formData.append(`image${index + 1}`, photo);
      });

      const result = await apiService.post(
        '/api/v1/auth/face/register/',
        formData
      );

      // 注册成功,跳转到首页
      router.replaceUrl({ url: 'pages/Index' });
    } catch (error) {
      // 显示错误信息
    } finally {
      this.isRegistering = false;
    }
  }

  build() {
    Column() {
      Text('人脸注册')
        .fontSize(24)
        .margin({ bottom: 20 })

      Text(`已拍摄: ${this.photoCount}/5张`)
        .fontSize(16)
        .margin({ bottom: 20 })

      // 相机预览区域
      XComponent({
        id: 'componentId',
        type: 'surface'
      })
        .width('80%')
        .height('60%')
        .margin({ bottom: 20 })

      Row() {
        Button('拍照')
          .width('40%')
          .margin({ right: 10 })
          .onClick(() => {
            this.capturePhoto();
          })

        Button('完成注册')
          .width('40%')
          .enabled(this.photoCount >= 3 && !this.isRegistering)
          .onClick(() => {
            this.registerFaces();
          })
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## Phase 4.4: 打卡功能

### 1. 获取打卡任务列表

**pages/Index.ets:**

```typescript
import { apiService } from '../services/ApiService';

interface Task {
  id: number;
  task_name: string;
  checked_today: boolean;
}

@Entry
@Component
struct Index {
  @State tasks: Task[] = [];
  @State isLoading: boolean = true;

  async aboutToAppear() {
    await this.loadTasks();
  }

  async loadTasks() {
    try {
      const result = await apiService.get('/api/v1/checkins/my-tasks/');
      this.tasks = result.tasks;
    } catch (error) {
      // 处理错误
    } finally {
      this.isLoading = false;
    }
  }

  build() {
    Column() {
      Text('我的打卡任务')
        .fontSize(24)
        .margin({ top: 20, bottom: 20 })

      if (this.isLoading) {
        LoadingProgress()
          .width(50)
          .height(50)
      } else {
        List() {
          ForEach(this.tasks, (task: Task) => {
            ListItem() {
              Row() {
                Column() {
                  Text(task.task_name)
                    .fontSize(18)
                }
                .layoutWeight(1)

                if (task.checked_today) {
                  Text('已打卡')
                    .fontSize(14)
                    .fontColor(Color.Green)
                } else {
                  Button('去打卡')
                    .onClick(() => {
                      router.pushUrl({
                        url: 'pages/Checkin',
                        params: { taskId: task.id }
                      });
                    })
                }
              }
              .width('90%')
              .padding(15)
              .backgroundColor(Color.White)
              .borderRadius(10)
            }
            .margin({ bottom: 10 })
          })
        }
        .width('100%')
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

### 2. 打卡页面

**pages/Checkin.ets:**

```typescript
import camera from '@ohos.multimedia.camera';
import { apiService } from '../services/ApiService';

@Entry
@Component
struct Checkin {
  @State taskId: number = 0;
  @State isSubmitting: boolean = false;
  @State photo: string = '';

  async captureAndSubmit() {
    // 拍照
    // 实现相机拍照逻辑

    this.isSubmitting = true;

    try {
      const formData = new FormData();
      formData.append('task_id', this.taskId.toString());
      formData.append('photo', this.photo);

      const result = await apiService.post(
        '/api/v1/checkins/submit/',
        formData
      );

      // 显示打卡结果
      AlertDialog.show({
        title: '打卡成功',
        message: `情绪: ${result.emotion?.emotion_cn}\n置信度: ${(result.emotion?.confidence * 100).toFixed(1)}%`,
        confirm: {
          value: '确定',
          action: () => {
            router.back();
          }
        }
      });
    } catch (error) {
      // 处理错误
    } finally {
      this.isSubmitting = false;
    }
  }

  build() {
    Column() {
      Text('打卡拍照')
        .fontSize(24)
        .margin({ bottom: 20 })

      // 相机预览
      XComponent({
        id: 'cameraId',
        type: 'surface'
      })
        .width('80%')
        .height('60%')
        .margin({ bottom: 20 })

      Button(this.isSubmitting ? '提交中...' : '拍照打卡')
        .width('80%')
        .height(50)
        .enabled(!this.isSubmitting)
        .onClick(() => {
          this.captureAndSubmit();
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## Phase 4.5: 历史记录

**pages/History.ets:**

```typescript
import { apiService } from '../services/ApiService';

interface CheckinRecord {
  id: number;
  task: { name: string };
  checkin_time: string;
  status: string;
  emotion: {
    emotion: string;
    confidence: number;
  };
}

@Entry
@Component
struct History {
  @State records: CheckinRecord[] = [];
  @State isLoading: boolean = true;

  async aboutToAppear() {
    await this.loadHistory();
  }

  async loadHistory() {
    try {
      const result = await apiService.get('/api/v1/checkins/records/?days=7');
      this.records = result.records;
    } catch (error) {
      // 处理错误
    } finally {
      this.isLoading = false;
    }
  }

  build() {
    Column() {
      Text('打卡历史')
        .fontSize(24)
        .margin({ top: 20, bottom: 20 })

      if (this.isLoading) {
        LoadingProgress()
      } else {
        List() {
          ForEach(this.records, (record: CheckinRecord) => {
            ListItem() {
              Column() {
                Row() {
                  Text(record.task.name)
                    .fontSize(16)
                    .fontWeight(FontWeight.Bold)
                  Blank()
                  Text(record.status)
                    .fontSize(14)
                    .fontColor(this.getStatusColor(record.status))
                }
                .width('100%')
                .margin({ bottom: 10 })

                Row() {
                  Text(`时间: ${record.checkin_time}`)
                    .fontSize(14)
                }
                .width('100%')
                .margin({ bottom: 5 })

                if (record.emotion) {
                  Row() {
                    Text(`情绪: ${record.emotion.emotion} (${(record.emotion.confidence * 100).toFixed(1)}%)`)
                      .fontSize(14)
                  }
                  .width('100%')
                }
              }
              .width('90%')
              .padding(15)
              .backgroundColor(Color.White)
              .borderRadius(10)
            }
            .margin({ bottom: 10 })
          })
        }
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  getStatusColor(status: string): ResourceColor {
    switch (status) {
      case 'on_time':
        return Color.Green;
      case 'late':
        return Color.Orange;
      case 'missed':
        return Color.Red;
      default:
        return Color.Grey;
    }
  }
}
```

---

## API接口列表

### 认证API
- `POST /api/v1/auth/login/` - 登录
- `POST /api/v1/auth/register/` - 注册
- `POST /api/v1/auth/face/register/` - 注册人脸
- `POST /api/v1/auth/face/verify/` - 验证人脸
- `GET /api/v1/auth/me/` - 获取当前用户信息

### 打卡API
- `GET /api/v1/checkins/my-tasks/` - 获取我的任务
- `POST /api/v1/checkins/submit/` - 提交打卡
- `GET /api/v1/checkins/records/` - 获取打卡记录
- `GET /api/v1/checkins/statistics/` - 获取统计数据

### 表情API
- `POST /api/v1/emotions/analyze/` - 分析表情
- `GET /api/v1/emotions/records/` - 获取表情记录
- `GET /api/v1/emotions/statistics/` - 获取统计数据

---

## 注意事项

1. **权限申请**: 必须在module.json5中声明相机权限
2. **网络配置**: 在module.json5中配置网络权限
3. **HTTPS**: 生产环境必须使用HTTPS
4. **Token刷新**: 实现自动刷新accessToken的机制
5. **错误处理**: 统一处理网络错误和业务错误
6. **本地缓存**: 合理使用本地缓存减少网络请求

---

## 测试建议

1. 使用模拟器测试基本流程
2. 真机测试相机功能
3. 测试网络异常情况
4. 测试Token过期处理
5. 性能测试(图片上传速度)

---

**祝开发顺利!完整API文档请参考API_DOCUMENTATION.md**