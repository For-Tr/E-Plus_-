/**
 * 人脸注册页面
 */
import router from '@ohos.router'
import promptAction from '@ohos.promptAction'
import HttpUtil from '../common/utils/HttpUtil'
import StorageUtil from '../common/utils/StorageUtil'
import CameraUtil from '../common/utils/CameraUtil'
import { ApiEndpoints, StorageKeys, AppConfig, ErrorMessages } from '../common/constants/AppConstants'

@Entry
@Component
struct FaceRegister {
  @State isLoading: boolean = false
  @State message: string = ''
  @State capturedImage: string = ''
  @State step: number = 1  // 1:说明 2:拍照 3:上传

  async aboutToAppear() {
    // 初始化相机
    await CameraUtil.init(getContext(this))
  }

  /**
   * 拍照
   */
  async handleTakePicture() {
    this.isLoading = true
    this.message = '正在启动相机...'

    try {
      const photoBase64 = await CameraUtil.takePictureAsBase64()
      
      if (photoBase64) {
        this.capturedImage = photoBase64
        this.step = 3
        this.message = ''
        
        promptAction.showToast({
          message: '照片拍摄成功',
          duration: 1500
        })
      } else {
        this.message = ErrorMessages.CAMERA_ERROR
        promptAction.showToast({
          message: ErrorMessages.CAMERA_ERROR,
          duration: 2000
        })
      }
    } catch (error) {
      console.error('[FaceRegister] Take picture error:', JSON.stringify(error))
      this.message = ErrorMessages.CAMERA_ERROR
      promptAction.showToast({
        message: ErrorMessages.CAMERA_ERROR,
        duration: 2000
      })
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 上传人脸照片
   */
  async handleUpload() {
    if (!this.capturedImage) {
      promptAction.showToast({
        message: '请先拍照',
        duration: 2000
      })
      return
    }

    this.isLoading = true
    this.message = '正在注册人脸...'

    try {
      const response: { success: boolean; error?: string } = await HttpUtil.uploadImage(
        ApiEndpoints.FACE_REGISTER,
        this.capturedImage,
        'photo'
      )

      if (response.success) {
        // 更新本地人脸注册状态
        await StorageUtil.setBoolean(StorageKeys.IS_FACE_REGISTERED, true)
        
        promptAction.showToast({
          message: '人脸注册成功!',
          duration: 2000
        })

        // 跳转到主页
        setTimeout(() => {
          router.replaceUrl({
            url: AppConfig.PAGE_HOME
          })
        }, 1500)
      } else {
        this.message = response.error || ErrorMessages.FACE_REGISTER_FAILED
        promptAction.showToast({
          message: response.error || ErrorMessages.FACE_REGISTER_FAILED,
          duration: 3000
        })
      }
    } catch (error) {
      console.error('[FaceRegister] Upload error:', JSON.stringify(error))
      this.message = ErrorMessages.NETWORK_ERROR
      promptAction.showToast({
        message: ErrorMessages.NETWORK_ERROR,
        duration: 3000
      })
    } finally {
      this.isLoading = false
    }
  }

  /**
   * 重新拍照
   */
  handleRetake() {
    this.capturedImage = ''
    this.step = 2
    this.message = ''
  }

  /**
   * 跳过注册
   */
  handleSkip() {
    router.replaceUrl({
      url: AppConfig.PAGE_HOME
    })
  }

  build() {
    Column() {
      // 顶部标题
      Row() {
        Text('人脸注册')
          .fontSize(20)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
      }
      .width('100%')
      .height(56)
      .padding({ left: 20, right: 20 })
      .backgroundColor('#FFFFFF')
      .justifyContent(FlexAlign.Center)

      // 主内容区域
      Column() {
        if (this.step === 1) {
          // 说明页面
          Column() {
            Image($r('app.media.face_guide'))
              .width(200)
              .height(200)
              .margin({ bottom: 30 })

            Text('首次使用需要注册人脸')
              .fontSize(20)
              .fontWeight(FontWeight.Medium)
              .fontColor('#333')
              .margin({ bottom: 15 })

            Column() {
              Text('• 请确保光线充足')
                .fontSize(16)
                .fontColor('#666')
                .margin({ bottom: 8 })

              Text('• 正对摄像头,保持面部清晰')
                .fontSize(16)
                .fontColor('#666')
                .margin({ bottom: 8 })

              Text('• 摘下眼镜和口罩')
                .fontSize(16)
                .fontColor('#666')
                .margin({ bottom: 8 })

              Text('• 保持自然表情')
                .fontSize(16)
                .fontColor('#666')
            }
            .alignItems(HorizontalAlign.Start)
            .margin({ bottom: 40 })

            Button('开始拍照')
              .width('80%')
              .height(50)
              .fontSize(18)
              .fontColor('#FFFFFF')
              .backgroundColor('#007DFF')
              .borderRadius(10)
              .onClick(() => {
                this.step = 2
                this.handleTakePicture()
              })

            Button('稍后注册')
              .width('80%')
              .height(50)
              .fontSize(16)
              .fontColor('#666')
              .backgroundColor('#FFFFFF')
              .border({ width: 1, color: '#DDDDDD' })
              .borderRadius(10)
              .margin({ top: 15 })
              .onClick(() => {
                this.handleSkip()
              })
          }
          .width('100%')
          .padding(30)

        } else if (this.step === 2) {
          // 拍照中
          Column() {
            Text('请正对摄像头')
              .fontSize(18)
              .fontColor('#333')
              .margin({ top: 50, bottom: 30 })

            // 相机预览区域占位
            Column() {
              Text('📷')
                .fontSize(80)
            }
            .width(300)
            .height(400)
            .backgroundColor('#000000')
            .borderRadius(15)
            .justifyContent(FlexAlign.Center)

            if (this.isLoading) {
              Text(this.message || '准备中...')
                .fontSize(16)
                .fontColor('#666')
                .margin({ top: 20 })
            }
          }
          .width('100%')

        } else if (this.step === 3) {
          // 照片预览和上传
          Column() {
            Text('照片预览')
              .fontSize(18)
              .fontWeight(FontWeight.Medium)
              .fontColor('#333')
              .margin({ top: 20, bottom: 20 })

            // 显示拍摄的照片
            Image(`data:image/jpeg;base64,${this.capturedImage}`)
              .width(300)
              .height(400)
              .objectFit(ImageFit.Cover)
              .borderRadius(15)
              .margin({ bottom: 30 })

            Row() {
              Button('重新拍照')
                .width('45%')
                .height(50)
                .fontSize(16)
                .fontColor('#666')
                .backgroundColor('#FFFFFF')
                .border({ width: 1, color: '#DDDDDD' })
                .borderRadius(10)
                .enabled(!this.isLoading)
                .onClick(() => {
                  this.handleRetake()
                })

              Button(this.isLoading ? '上传中...' : '确认上传')
                .width('45%')
                .height(50)
                .fontSize(16)
                .fontColor('#FFFFFF')
                .backgroundColor(this.isLoading ? '#CCCCCC' : '#007DFF')
                .borderRadius(10)
                .enabled(!this.isLoading)
                .onClick(() => {
                  this.handleUpload()
                })
            }
            .width('85%')
            .justifyContent(FlexAlign.SpaceBetween)

            if (this.message) {
              Text(this.message)
                .fontSize(14)
                .fontColor('#FF0000')
                .margin({ top: 15 })
            }
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