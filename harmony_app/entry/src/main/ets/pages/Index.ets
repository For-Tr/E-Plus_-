/**
 * 首页 - 邀请码登录页面
 */
import router from '@ohos.router'
import promptAction from '@ohos.promptAction'
import HttpUtil from '../common/utils/HttpUtil'
import StorageUtil from '../common/utils/StorageUtil'
import { ApiEndpoints, StorageKeys, AppConfig, ErrorMessages } from '../common/constants/AppConstants'
import { LoginResponse } from '../models/User'

@Entry
@Component
struct Index {
  @State inviteCode: string = ''
  @State isLoading: boolean = false
  @State message: string = ''

  async aboutToAppear() {
    // 检查是否已保存邀请码,自动登录
    const savedInviteCode = await StorageUtil.getString(StorageKeys.INVITE_CODE)
    if (savedInviteCode) {
      this.inviteCode = savedInviteCode
      console.info('[Index] Found saved invite code, auto login...')
      await this.handleLogin()
    }
  }

  /**
   * 处理登录
   */
  async handleLogin() {
    // 验证邀请码
    if (!this.inviteCode || this.inviteCode.trim().length === 0) {
      promptAction.showToast({
        message: '请输入邀请码',
        duration: 2000
      })
      return
    }

    this.isLoading = true
    this.message = '登录中...'

    try {
      // 调用邀请码登录API
      const requestBody: ESObject = {
        'invite_code': this.inviteCode.trim().toUpperCase()
      }
      const response = await HttpUtil.post<LoginResponse>(
        ApiEndpoints.INVITE_LOGIN,
        requestBody,
        false  // 登录时不需要Token
      )

      if (response.success && response.data) {
        // 保存登录信息
        await StorageUtil.setString(StorageKeys.INVITE_CODE, this.inviteCode.trim().toUpperCase())
        await StorageUtil.setString(StorageKeys.ACCESS_TOKEN, response.data.access)
        await StorageUtil.setString(StorageKeys.REFRESH_TOKEN, response.data.refresh)
        await StorageUtil.setObject(StorageKeys.USER_INFO, response.data.user)
        await StorageUtil.setBoolean(StorageKeys.IS_FACE_REGISTERED, response.data.user.face_registered)

        console.info('[Index] Login success, user:', JSON.stringify(response.data.user))

        // 显示欢迎消息
        promptAction.showToast({
          message: `欢迎,${response.data.user.display_name}!`,
          duration: 2000
        })

        // 登录流程到此结束,标记为成功
        this.isLoading = false
        
        // 检查是否已注册人脸 - 在预览器中这个路由跳转会失败,但不影响登录本身
        const targetPage = !response.data.user.face_registered ? 
          AppConfig.PAGE_FACE_REGISTER : AppConfig.PAGE_HOME
        
        console.info('[Index] Preparing to navigate to:', targetPage)
        
        // 延迟跳转,完全独立于登录流程
        setTimeout(() => {
          router.replaceUrl({ url: targetPage })
            .then(() => {
              console.info('[Index] Navigation successful')
            })
            .catch((err: Error) => {
              // 预览器不支持路由跳转,这是正常的
              console.warn('[Index] Navigation failed (预览器限制):', JSON.stringify(err))
            })
        }, 1000)
        
        return // 提前返回,避免执行失败分支
      } else {
        // 登录失败
        this.message = response.error || ErrorMessages.LOGIN_FAILED
        promptAction.showToast({
          message: response.error || ErrorMessages.LOGIN_FAILED,
          duration: 3000
        })
      }
    } catch (error) {
      console.error('[Index] Login error:', JSON.stringify(error))
      this.message = ErrorMessages.NETWORK_ERROR
      promptAction.showToast({
        message: ErrorMessages.NETWORK_ERROR,
        duration: 3000
      })
    } finally {
      // 只有登录失败时才设置为false,成功时已经提前设置了
      if (this.isLoading) {
        this.isLoading = false
      }
    }
  }

  build() {
    Column() {
      // 顶部Logo和标题
      Column() {
        Image($r('app.media.app_icon'))
          .width(100)
          .height(100)
          .margin({ bottom: 20 })

        Text(AppConfig.APP_NAME)
          .fontSize(28)
          .fontWeight(FontWeight.Bold)
          .fontColor('#333')
          .margin({ bottom: 10 })

        Text('用AI守护家人的心理健康')
          .fontSize(16)
          .fontColor('#666')
          .margin({ bottom: 40 })
      }
      .margin({ top: 80 })

      // 邀请码输入区域
      Column() {
        Text('请输入邀请码')
          .fontSize(18)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .alignSelf(ItemAlign.Start)
          .margin({ bottom: 15 })

        TextInput({ placeholder: '请输入8位邀请码', text: this.inviteCode })
          .height(50)
          .fontSize(16)
          .maxLength(8)
          .type(InputType.Normal)
          .placeholderColor('#999')
          .backgroundColor('#F5F5F5')
          .borderRadius(10)
          .padding({ left: 15, right: 15 })
          .onChange((value: string) => {
            this.inviteCode = value.toUpperCase()
          })
          .margin({ bottom: 20 })

        // 登录按钮
        Button(this.isLoading ? '登录中...' : '登录')
          .width('100%')
          .height(50)
          .fontSize(18)
          .fontColor('#FFFFFF')
          .backgroundColor(this.isLoading ? '#CCCCCC' : '#007DFF')
          .borderRadius(10)
          .enabled(!this.isLoading)
          .onClick(() => {
            this.handleLogin()
          })

        // 提示信息
        if (this.message) {
          Text(this.message)
            .fontSize(14)
            .fontColor('#FF0000')
            .margin({ top: 15 })
        }
      }
      .width('85%')
      .padding({ left: 20, right: 20, top: 30, bottom: 30 })
      .backgroundColor('#FFFFFF')
      .borderRadius(15)
      .shadow({
        radius: 20,
        color: '#00000010',
        offsetX: 0,
        offsetY: 5
      })

      // 说明文字
      Column() {
        Text('如何获取邀请码?')
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .margin({ bottom: 10 })

        Text('1. 请联系家庭管理员')
          .fontSize(14)
          .fontColor('#666')
          .margin({ bottom: 5 })

        Text('2. 管理员在Web管理界面生成邀请码')
          .fontSize(14)
          .fontColor('#666')
          .margin({ bottom: 5 })

        Text('3. 使用邀请码即可登录')
          .fontSize(14)
          .fontColor('#666')
      }
      .margin({ top: 40 })
      .padding(20)

      Blank()

      // 底部版本信息
      Text(`版本 ${AppConfig.APP_VERSION}`)
        .fontSize(12)
        .fontColor('#999')
        .margin({ bottom: 20 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}