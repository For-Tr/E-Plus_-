/**
 * Mock数据工具类 - 用于预览器调试
 */
import { ApiEndpoints, UserRole, CheckinStatus, EmotionType } from '../constants/AppConstants'
import { User, LoginResponse, Family } from '../../models/User'
import { CheckinTask, CheckinTaskListResponse } from '../../models/CheckinTask'
import { CheckinRecord, CheckinRecordListResponse } from '../../models/CheckinRecord'

// Mock响应接口
interface MockResponse {
  success: boolean
  data?: ESObject
  error?: string
  status?: number
}

class MockData {
  private static instance: MockData | null = null

  private constructor() {}

  public static getInstance(): MockData {
    if (!MockData.instance) {
      MockData.instance = new MockData()
    }
    return MockData.instance
  }

  /**
   * 获取Mock数据
   */
  async getMockData(url: string, method: string, body?: ESObject): Promise<MockResponse> {
    console.info(`[MockData] ${method} ${url}`)
    
    // 模拟网络延迟
    await this.delay(300)

    // 根据URL返回对应的Mock数据
    if (url.includes(ApiEndpoints.INVITE_LOGIN)) {
      return this.mockInviteLogin(body)
    } else if (url.includes(ApiEndpoints.CURRENT_USER)) {
      return this.mockCurrentUser()
    } else if (url.includes(ApiEndpoints.FACE_REGISTER)) {
      return this.mockFaceRegister()
    } else if (url.includes(ApiEndpoints.FACE_VERIFY)) {
      return this.mockFaceVerify()
    } else if (url.includes(ApiEndpoints.CHECKIN_TASKS)) {
      return this.mockCheckinTasks()
    } else if (url.includes(ApiEndpoints.CHECKIN_CREATE)) {
      return this.mockCheckinCreate(body)
    } else if (url.includes(ApiEndpoints.CHECKIN_RECORDS)) {
      return this.mockCheckinRecords()
    } else if (url.includes(ApiEndpoints.EMOTION_RECORDS)) {
      return this.mockEmotionRecords()
    }

    return {
      success: false,
      error: 'Mock数据未定义',
      status: 404
    }
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, ms)
    })
  }

  /**
   * Mock邀请码登录
   */
  private mockInviteLogin(body?: ESObject): MockResponse {
    const inviteCode = body?.['invite_code'] as string || ''
    
    if (inviteCode === 'FAMILY2024' || inviteCode.length > 0) {
      const mockFamily: Family = {
        id: 1,
        name: '张家'
      }
      
      const mockUser: User = {
        id: 1,
        username: 'zhangsan',
        display_name: '张三',
        email: 'zhangsan@example.com',
        role: UserRole.FAMILY_MEMBER,
        face_registered: true,
        family: mockFamily
      }
      
      const loginResponse: LoginResponse = {
        access: 'mock_access_token_' + Date.now(),
        refresh: 'mock_refresh_token_' + Date.now(),
        user: mockUser,
        invite_code: inviteCode
      }
      
      return {
        success: true,
        data: loginResponse as ESObject,
        status: 200
      }
    } else {
      return {
        success: false,
        error: '邀请码无效',
        status: 400
      }
    }
  }

  /**
   * Mock获取当前用户
   */
  private mockCurrentUser(): MockResponse {
    const mockFamily: Family = {
      id: 1,
      name: '张家'
    }
    
    const mockUser: User = {
      id: 1,
      username: 'zhangsan',
      display_name: '张三',
      email: 'zhangsan@example.com',
      role: UserRole.FAMILY_MEMBER,
      face_registered: true,
      family: mockFamily
    }
    
    return {
      success: true,
      data: mockUser as ESObject,
      status: 200
    }
  }

  /**
   * Mock人脸注册
   */
  private mockFaceRegister(): MockResponse {
    const response: ESObject = {
      'message': '人脸注册成功',
      'face_id': 'mock_face_' + Date.now()
    }
    
    return {
      success: true,
      data: response,
      status: 200
    }
  }

  /**
   * Mock人脸验证
   */
  private mockFaceVerify(): MockResponse {
    const response: ESObject = {
      'verified': true,
      'confidence': 0.95,
      'user_id': 1,
      'username': '张三'
    }
    
    return {
      success: true,
      data: response,
      status: 200
    }
  }

  /**
   * Mock打卡任务列表
   */
  private mockCheckinTasks(): MockResponse {
    const scheduleConfig1: ESObject = {
      'start_time': '07:00:00',
      'end_time': '09:00:00',
      'repeat_days': [1, 2, 3, 4, 5, 6, 7]
    }
    
    const scheduleConfig2: ESObject = {
      'start_time': '20:00:00',
      'end_time': '22:00:00',
      'repeat_days': [1, 2, 3, 4, 5, 6, 7]
    }
    
    const reminderConfig: ESObject = {
      'enabled': true
    }
    
    const task1: CheckinTask = {
      id: 1,
      task_name: '早安打卡',
      task_type: 'daily',
      family: 1,
      is_active: true,
      schedule_config: scheduleConfig1,
      reminder_config: reminderConfig,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
    
    const task2: CheckinTask = {
      id: 2,
      task_name: '晚安打卡',
      task_type: 'daily',
      family: 1,
      is_active: true,
      schedule_config: scheduleConfig2,
      reminder_config: reminderConfig,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
    
    const tasks: CheckinTask[] = [task1, task2]
    
    const response: CheckinTaskListResponse = {
      count: 2,
      results: tasks
    }
    
    return {
      success: true,
      data: response as ESObject,
      status: 200
    }
  }

  /**
   * Mock创建打卡记录
   */
  private mockCheckinCreate(body?: ESObject): MockResponse {
    const taskId = body?.['task_id'] as number || 1
    
    // 随机选择一个情绪
    const emotions: string[] = ['happy', 'sad', 'angry', 'neutral', 'surprise']
    const randomIndex = Math.floor(Math.random() * emotions.length)
    const randomEmotion = emotions[randomIndex] as EmotionType
    
    const emotionDetail: ESObject = {
      'type': randomEmotion,
      'confidence': 0.85 + Math.random() * 0.15
    }
    
    const record: CheckinRecord = {
      id: Date.now(),
      user: 1,
      task: taskId,
      family: 1,
      checkin_time: new Date().toISOString(),
      status: CheckinStatus.ON_TIME,
      face_photo: '/media/checkins/mock_photo.jpg',
      face_verified: true,
      emotion: randomEmotion,
      emotion_confidence: 0.85 + Math.random() * 0.15,
      emotion_detail: emotionDetail,
      created_at: new Date().toISOString()
    }
    
    return {
      success: true,
      data: record as ESObject,
      status: 201
    }
  }

  /**
   * Mock打卡记录列表
   */
  private mockCheckinRecords(): MockResponse {
    const records: CheckinRecord[] = []
    const emotions: EmotionType[] = [
      EmotionType.HAPPY,
      EmotionType.SAD,
      EmotionType.ANGRY,
      EmotionType.NEUTRAL,
      EmotionType.SURPRISE,
      EmotionType.FEAR,
      EmotionType.DISGUST
    ]
    const statuses: CheckinStatus[] = [
      CheckinStatus.ON_TIME,
      CheckinStatus.LATE,
      CheckinStatus.MAKEUP
    ]
    
    // 生成20条mock记录
    for (let i = 0; i < 20; i++) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      const emotionDetail: ESObject = {
        'type': emotions[i % emotions.length],
        'confidence': 0.75 + Math.random() * 0.25
      }
      
      const record: CheckinRecord = {
        id: 100 + i,
        user: 1,
        task: (i % 2) + 1,
        family: 1,
        checkin_time: date.toISOString(),
        status: statuses[i % statuses.length],
        face_photo: '/media/checkins/mock_photo_' + i + '.jpg',
        face_verified: true,
        emotion: emotions[i % emotions.length],
        emotion_confidence: 0.75 + Math.random() * 0.25,
        emotion_detail: emotionDetail,
        note: i % 3 === 0 ? '今天心情不错' : undefined,
        created_at: date.toISOString()
      }
      
      records.push(record)
    }
    
    const response: CheckinRecordListResponse = {
      count: 20,
      results: records
    }
    
    return {
      success: true,
      data: response as ESObject,
      status: 200
    }
  }

  /**
   * Mock情绪记录列表
   */
  private mockEmotionRecords(): MockResponse {
    const recordsData: ESObject[] = []
    const emotions: EmotionType[] = [
      EmotionType.HAPPY,
      EmotionType.SAD,
      EmotionType.ANGRY,
      EmotionType.NEUTRAL,
      EmotionType.SURPRISE,
      EmotionType.FEAR,
      EmotionType.DISGUST
    ]
    
    for (let i = 0; i < 15; i++) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      const record: ESObject = {
        'id': 200 + i,
        'user_id': 1,
        'username': '张三',
        'emotion_type': emotions[i % emotions.length],
        'confidence': 0.75 + Math.random() * 0.25,
        'note': i % 4 === 0 ? '今天发生了有趣的事' : null,
        'created_at': date.toISOString()
      }
      
      recordsData.push(record)
    }
    
    const response: ESObject = {
      'count': 15,
      'results': recordsData
    }
    
    return {
      success: true,
      data: response,
      status: 200
    }
  }
}

export default MockData.getInstance()