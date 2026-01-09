/**
 * 打卡页面
 */
import router from '@ohos.router'
import promptAction from '@ohos.promptAction'
import HttpUtil from '../common/utils/HttpUtil'
import CameraUtil from '../common/utils/CameraUtil'
import { ApiEndpoints, EMOTION_NAMES, ErrorMessages } from '../common/constants/AppConstants'
import { CheckinTaskListResponse } from '../models/CheckinTask'
import { CheckinCreateRequest, CheckinRecord } from '../models/CheckinRecord'

@Entry
@Component
struct Checkin {
  @State isLoading: boolean = false
  @State message: string = ''
  @State currentTask: any = null
  @State capturedImage: string = ''
  @State checkinResult: CheckinRecord | null = null
  @State step: number = 1  // 1:任务说明 2:拍照 3:结果展示

  async aboutToAppear() {
    await CameraUtil.init(getContext(this))
    await this.loadTask()
  }

  /**
   * 加载打卡任务
   */
  async loadTask() {
    this.isLoading = true

    try {
      const response = await HttpUtil.get<CheckinTaskListResponse>(ApiEndpoints.CHECKIN_TASKS)
      
      if (response.success && response.data && response.data.results.length > 0) {
        // 获取第一个活跃任务
        this.currentTask = response.data.results[0]
        console.info('[Checkin] Task loaded:', JSON.stringify(this.currentTask))
      } else {
        promptAction.showToast({
          message: '暂无打卡任务',
          duration: 2000
        })
        setTimeout(() => {
          router.back()
        }, 1500)
      }
    } catch (error) {
      console.error('[Checkin] Load task error:', JSON.stringify(error))
      promptAction.showToast({
        message: ErrorMessages.NETWORK_ERROR,
        duration: 2000
      })
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 开始拍照
   */
  async handleStartCapture() {
    this.step = 2
    this.isLoading = true
    this.message = '正在启动相机...'

    try {
      const photoBase64 = await CameraUtil.takePictureAsBase64()
      
      if (photoBase64) {
        this.capturedImage = photoBase64
        this.message = ''
        
        // 直接提交打卡
        await this.submitCheckin()
      } else {
        this.message = ErrorMessages.CAMERA_ERROR
        promptAction.showToast({
          message: ErrorMessages.CAMERA_ERROR,
          duration: 2000
        })
        this.step = 1
      }
    } catch (error) {
      console.error('[Checkin] Capture error:', JSON.stringify(error))
      this.message = ErrorMessages.CAMERA_ERROR
      this.step = 1
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 提交打卡
   */
  async submitCheckin() {
    this.isLoading = true
    this.message = '正在识别人脸和情绪...'

    try {
      const requestData: CheckinCreateRequest = {
        task_id: this.currentTask.id,
        photo: this.capturedImage
      }

      const response = await HttpUtil.post<CheckinRecord>(
        ApiEndpoints.CHECKIN_CREATE,
        requestData
      )

      if (response.success && response.data) {
        this.checkinResult = response.data
        this.step = 3
        this.message = ''
        
        promptAction.showToast({
          message: '打卡成功!',
          duration: 2000
        })
      } else {
        this.message = response.error || ErrorMessages.CHECKIN_FAILED
        this.step = 1
        promptAction.showToast({
          message: response.error || ErrorMessages.CHECKIN_FAILED,
          duration: 3000
        })
      }
    } catch (error) {
      console.error('[Checkin] Submit error:', JSON.stringify(error))
      this.message = ErrorMessages.NETWORK_ERROR
      this.step = 1
      promptAction.showToast({
        message: ErrorMessages.NETWORK_ERROR,
        duration: 3000
      })
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 完成打卡,返回主页
   */
  handleFinish() {
    router.back()
  }

  build() {
    Column() {
      // 顶部标题栏
      Row() {
        Image($r('app.media.back'))
          .width(24)
          .height(24)
          .onClick(() => {
            router.back()
          })

        Text('打卡')
          .fontSize(20)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .layoutWeight(1)
          .textAlign(TextAlign.Center)

        // 占位,保持标题居中
        Column()
          .width(24)
          .height(24)
      }
      .width('100%')
      .height(56)
      .padding({ left: 20, right: 20 })
      .backgroundColor('#FFFFFF')

      // 主内容
      Column() {
        if (this.step === 1 && this.currentTask) {
          // 任务说明页面
          Column() {
            Image($r('app.media.checkin_icon'))
              .width(100)
              .height(100)
              .margin({ top: 50, bottom: 30 })

            Text(this.currentTask.task_name)
              .fontSize(24)
              .fontWeight(FontWeight.Bold)
              .fontColor('#333')
              .margin({ bottom: 15 })

            Column() {
              Text('准备开始打卡')
                .fontSize(18)
                .fontColor('#666')
                .margin({ bottom: 20 })

              Column() {
                Text('• 请正对摄像头')
                  .fontSize(16)
                  .fontColor('#666')
                  .margin({ bottom: 8 })

                Text('• 保持面部清晰可见')
                  .fontSize(16)
                  .fontColor('#666')
                  .margin({ bottom: 8 })

                Text('• 系统将自动识别您的情绪')
                  .fontSize(16)
                  .fontColor('#666')
                  .margin({ bottom: 8 })
              }
              .alignItems(HorizontalAlign.Start)
              .padding(20)
              .backgroundColor('#FFF9E6')
              .borderRadius(10)
            }
            .width('85%')
            .margin({ bottom: 50 })

            Button('开始打卡')
              .width('70%')
              .height(55)
              .fontSize(20)
              .fontColor('#FFFFFF')
              .backgroundColor('#007DFF')
              .borderRadius(15)
              .enabled(!this.isLoading)
              .onClick(() => {
                this.handleStartCapture()
              })
          }
          .width('100%')

        } else if (this.step === 2) {
          // 拍照中
          Column() {
            Text('请保持面部在框内')
              .fontSize(18)
              .fontColor('#333')
              .margin({ top: 50, bottom: 30 })

            // 相机预览占位
            Column() {
              Text('📷')
                .fontSize(80)
            }
            .width(300)
            .height(400)
            .backgroundColor('#000000')
            .borderRadius(15)
            .justifyContent(FlexAlign.Center)

            Text(this.message)
              .fontSize(16)
              .fontColor('#666')
              .margin({ top: 20 })
          }

        } else if (this.step === 3 && this.checkinResult) {
          // 结果展示
          Column() {
            // 成功图标
            Text('✓')
              .fontSize(80)
              .fontColor('#52C41A')
              .margin({ top: 50, bottom: 20 })

            Text('打卡成功!')
              .fontSize(28)
              .fontWeight(FontWeight.Bold)
              .fontColor('#333')
              .margin({ bottom: 40 })

            // 结果卡片
            Column() {
              // 打卡时间
              Row() {
                Text('打卡时间:')
                  .fontSize(16)
                  .fontColor('#666')
                Blank()
                Text(new Date(this.checkinResult.checkin_time).toLocaleString('zh-CN'))
                  .fontSize(16)
                  .fontColor('#333')
              }
              .width('100%')
              .margin({ bottom: 15 })

              // 打卡状态
              Row() {
                Text('打卡状态:')
                  .fontSize(16)
                  .fontColor('#666')
                Blank()
                Text(
                  this.checkinResult.status === 'on_time' ? '准时' :
                  this.checkinResult.status === 'late' ? '迟到' : '补签'
                )
                  .fontSize(16)
                  .fontColor(
                    this.checkinResult.status === 'on_time' ? '#52C41A' :
                    this.checkinResult.status === 'late' ? '#FAAD14' : '#F5222D'
                  )
                  .fontWeight(FontWeight.Medium)
              }
              .width('100%')
              .margin({ bottom: 15 })

              // 识别情绪
              if (this.checkinResult.emotion) {
                Row() {
                  Text('当前情绪:')
                    .fontSize(16)
                    .fontColor('#666')
                  Blank()
                  Text(EMOTION_NAMES[this.checkinResult.emotion] || this.checkinResult.emotion)
                    .fontSize(20)
                    .fontWeight(FontWeight.Medium)
                }
                .width('100%')
                .margin({ bottom: 15 })
              }

              // 置信度
              if (this.checkinResult.emotion_confidence) {
                Row() {
                  Text('置信度:')
                    .fontSize(16)
                    .fontColor('#666')
                  Blank()
                  Text(`${this.checkinResult.emotion_confidence.toFixed(1)}%`)
                    .fontSize(16)
                    .fontColor('#333')
                }
                .width('100%')
              }
            }
            .width('85%')
            .padding(25)
            .backgroundColor('#FFFFFF')
            .borderRadius(15)
            .shadow({
              radius: 15,
              color: '#00000010',
              offsetX: 0,
              offsetY: 3
            })
            .margin({ bottom: 50 })

            Button('完成')
              .width('70%')
              .height(50)
              .fontSize(18)
              .fontColor('#FFFFFF')
              .backgroundColor('#007DFF')
              .borderRadius(10)
              .onClick(() => {
                this.handleFinish()
              })
          }
          .width('100%')
        }
      }
      .layoutWeight(1)
      .backgroundColor('#F5F5F5')
    }
    .width('100%')
    .height('100%')
  }
}