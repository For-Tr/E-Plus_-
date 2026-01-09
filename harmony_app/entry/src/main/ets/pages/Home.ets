/**
 * 主页 - 打卡入口
 */
import router from '@ohos.router'
import promptAction from '@ohos.promptAction'
import HttpUtil from '../common/utils/HttpUtil'
import StorageUtil from '../common/utils/StorageUtil'
import { ApiEndpoints, StorageKeys, AppConfig, EmotionNames } from '../common/constants/AppConstants'
import { User } from '../models/User'
import { CheckinTaskListResponse } from '../models/CheckinTask'

@Entry
@Component
struct Home {
  @State user: User | null = null
  @State isLoading: boolean = false
  @State hasActiveTasks: boolean = false

  async aboutToAppear() {
    await this.loadUserInfo()
    await this.checkTasks()
  }

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    const userInfo = await StorageUtil.getObject(StorageKeys.USER_INFO)
    if (userInfo) {
      this.user = userInfo as User
      console.info('[Home] User loaded:', JSON.stringify(this.user))
    }
  }

  /**
   * 检查是否有活跃的打卡任务
   */
  async checkTasks() {
    try {
      const response = await HttpUtil.get<CheckinTaskListResponse>(ApiEndpoints.CHECKIN_TASKS)
      if (response.success && response.data) {
        this.hasActiveTasks = response.data.results.length > 0
        console.info(`[Home] Active tasks count: ${response.data.results.length}`)
      }
    } catch (error) {
      console.error('[Home] Check tasks error:', JSON.stringify(error))
    }
  }

  /**
   * 开始打卡
   */
  handleStartCheckin() {
    if (!this.hasActiveTasks) {
      promptAction.showToast({
        message: '暂无打卡任务',
        duration: 2000
      })
      return
    }

    router.pushUrl({
      url: AppConfig.PAGE_CHECKIN
    })
  }

  /**
   * 查看历史记录
   */
  handleViewHistory() {
    router.pushUrl({
      url: AppConfig.PAGE_HISTORY
    })
  }

  /**
   * 退出登录
   */
  async handleLogout() {
    try {
      // 清除本地存储
      await StorageUtil.clear()
      
      promptAction.showToast({
        message: '已退出登录',
        duration: 2000
      })

      // 返回登录页
      router.replaceUrl({
        url: AppConfig.PAGE_INDEX
      })
    } catch (error) {
      console.error('[Home] Logout error:', JSON.stringify(error))
    }
  }

  build() {
    Column() {
      // 顶部用户信息栏
      Row() {
        // 用户头像
        Image($r('app.media.default_avatar'))
          .width(50)
          .height(50)
          .borderRadius(25)
          .margin({ right: 15 })

        // 用户信息
        Column() {
          Text(this.user?.display_name || '用户')
            .fontSize(18)
            .fontWeight(FontWeight.Medium)
            .fontColor('#333')

          Text(this.user?.family?.name || '未加入家庭')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 5 })
        }
        .alignItems(HorizontalAlign.Start)

        Blank()

        // 退出按钮
        Button('退出')
          .fontSize(14)
          .fontColor('#FF0000')
          .backgroundColor('#FFFFFF')
          .border({ width: 1, color: '#FF0000' })
          .borderRadius(5)
          .padding({ left: 15, right: 15, top: 8, bottom: 8 })
          .onClick(() => {
            this.handleLogout()
          })
      }
      .width('100%')
      .padding(20)
      .backgroundColor('#FFFFFF')

      // 主内容区域
      Column() {
        // 打卡按钮
        Column() {
          Image($r('app.media.checkin_icon'))
            .width(80)
            .height(80)
            .margin({ bottom: 20 })

          Text('开始打卡')
            .fontSize(24)
            .fontWeight(FontWeight.Bold)
            .fontColor('#FFFFFF')
            .margin({ bottom: 10 })

          Text(this.hasActiveTasks ? '点击进行打卡' : '暂无打卡任务')
            .fontSize(14)
            .fontColor('#FFFFFF')
            .opacity(0.8)
        }
        .width('85%')
        .padding(40)
        .backgroundColor(this.hasActiveTasks ? '#007DFF' : '#CCCCCC')
        .borderRadius(20)
        .shadow({
          radius: 20,
          color: '#00000020',
          offsetX: 0,
          offsetY: 5
        })
        .onClick(() => {
          this.handleStartCheckin()
        })
        .margin({ top: 40 })

        // 功能按钮组
        Row() {
          // 历史记录
          Column() {
            Image($r('app.media.history_icon'))
              .width(40)
              .height(40)
              .margin({ bottom: 10 })

            Text('历史记录')
              .fontSize(14)
              .fontColor('#666')
          }
          .width('45%')
          .padding(20)
          .backgroundColor('#FFFFFF')
          .borderRadius(15)
          .shadow({
            radius: 10,
            color: '#00000010',
            offsetX: 0,
            offsetY: 2
          })
          .onClick(() => {
            this.handleViewHistory()
          })

          Blank()

          // 人脸管理
          Column() {
            Image($r('app.media.face_icon'))
              .width(40)
              .height(40)
              .margin({ bottom: 10 })

            Text('人脸管理')
              .fontSize(14)
              .fontColor('#666')
          }
          .width('45%')
          .padding(20)
          .backgroundColor('#FFFFFF')
          .borderRadius(15)
          .shadow({
            radius: 10,
            color: '#00000010',
            offsetX: 0,
            offsetY: 2
          })
          .onClick(() => {
            router.pushUrl({
              url: AppConfig.PAGE_FACE_REGISTER
            })
          })
        }
        .width('85%')
        .margin({ top: 30 })

        // 提示信息
        Column() {
          Text('使用说明')
            .fontSize(16)
            .fontWeight(FontWeight.Medium)
            .fontColor('#333')
            .margin({ bottom: 10 })

          Text('• 每日按时打卡,记录您的情绪状态')
            .fontSize(14)
            .fontColor('#666')
            .margin({ bottom: 5 })

          Text('• 打卡时会自动识别您的表情')
            .fontSize(14)
            .fontColor('#666')
            .margin({ bottom: 5 })

          Text('• 家庭管理员可查看所有成员的情绪记录')
            .fontSize(14)
            .fontColor('#666')
        }
        .width('85%')
        .padding(20)
        .backgroundColor('#FFF9E6')
        .borderRadius(10)
        .margin({ top: 30 })
        .alignItems(HorizontalAlign.Start)
      }
      .width('100%')
      .layoutWeight(1)

    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}