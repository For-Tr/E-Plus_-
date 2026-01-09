/**
 * 历史记录页面
 */
import router from '@ohos.router'
import promptAction from '@ohos.promptAction'
import HttpUtil from '../common/utils/HttpUtil'
import { ApiEndpoints, EMOTION_NAMES, ErrorMessages } from '../common/constants/AppConstants'
import { CheckinRecordListResponse, CheckinRecord } from '../models/CheckinRecord'

@Entry
@Component
struct History {
  @State records: CheckinRecord[] = []
  @State isLoading: boolean = false
  @State isRefreshing: boolean = false
  @State hasMore: boolean = true
  @State page: number = 1

  async aboutToAppear() {
    await this.loadRecords()
  }

  /**
   * 加载打卡记录
   */
  async loadRecords(refresh: boolean = false) {
    if (refresh) {
      this.isRefreshing = true
      this.page = 1
      this.records = []
    } else {
      this.isLoading = true
    }

    try {
      const url = `${ApiEndpoints.CHECKIN_RECORDS}?page=${this.page}&page_size=20`
      const response = await HttpUtil.get<CheckinRecordListResponse>(url)

      if (response.success && response.data) {
        if (refresh) {
          this.records = response.data.results
        } else {
          this.records = [...this.records, ...response.data.results]
        }

        this.hasMore = !!response.data.next
        console.info(`[History] Loaded ${response.data.results.length} records`)
      } else {
        promptAction.showToast({
          message: response.error || '加载失败',
          duration: 2000
        })
      }
    } catch (error) {
      console.error('[History] Load records error:', JSON.stringify(error))
      promptAction.showToast({
        message: ErrorMessages.NETWORK_ERROR,
        duration: 2000
      })
    } finally {
      this.isLoading = false
      this.isRefreshing = false
    }
  }

  /**
   * 加载更多
   */
  async loadMore() {
    if (this.isLoading || !this.hasMore) {
      return
    }

    this.page++
    await this.loadRecords()
  }

  /**
   * 下拉刷新
   */
  async handleRefresh() {
    await this.loadRecords(true)
  }

  /**
   * 格式化日期时间
   */
  formatDateTime(dateString: string): string {
    const date = new Date(dateString)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = date.getHours()
    const minute = date.getMinutes()
    return `${month}月${day}日 ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
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

        Text('历史记录')
          .fontSize(20)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .layoutWeight(1)
          .textAlign(TextAlign.Center)

        // 占位
        Column()
          .width(24)
          .height(24)
      }
      .width('100%')
      .height(56)
      .padding({ left: 20, right: 20 })
      .backgroundColor('#FFFFFF')

      // 记录列表
      if (this.records.length > 0) {
        List() {
          ForEach(this.records, (record: CheckinRecord) => {
            ListItem() {
              Column() {
                Row() {
                  // 左侧:日期时间
                  Column() {
                    Text(this.formatDateTime(record.checkin_time))
                      .fontSize(16)
                      .fontColor('#333')
                      .fontWeight(FontWeight.Medium)
                      .margin({ bottom: 5 })

                    Text(record.task ? `任务ID: ${record.task}` : '')
                      .fontSize(14)
                      .fontColor('#999')
                  }
                  .alignItems(HorizontalAlign.Start)

                  Blank()

                  // 右侧:状态和情绪
                  Column() {
                    // 打卡状态
                    Text(
                      record.status === 'on_time' ? '✓ 准时' :
                      record.status === 'late' ? '⚠ 迟到' : '补签'
                    )
                      .fontSize(14)
                      .fontColor(
                        record.status === 'on_time' ? '#52C41A' :
                        record.status === 'late' ? '#FAAD14' : '#F5222D'
                      )
                      .fontWeight(FontWeight.Medium)
                      .margin({ bottom: 8 })

                    // 情绪
                    if (record.emotion) {
                      Text(EMOTION_NAMES[record.emotion] || record.emotion)
                        .fontSize(20)
                    }
                  }
                  .alignItems(HorizontalAlign.End)
                }
                .width('100%')
                .padding(20)
              }
              .width('95%')
              .backgroundColor('#FFFFFF')
              .borderRadius(10)
              .margin({ top: 10, left: 10, right: 10 })
              .shadow({
                radius: 8,
                color: '#00000008',
                offsetX: 0,
                offsetY: 2
              })
            }
          })

          // 加载更多指示器
          if (this.hasMore) {
            ListItem() {
              Row() {
                if (this.isLoading) {
                  LoadingProgress()
                    .width(30)
                    .height(30)
                    .margin({ right: 10 })
                  Text('加载中...')
                    .fontSize(14)
                    .fontColor('#999')
                } else {
                  Text('上拉加载更多')
                    .fontSize(14)
                    .fontColor('#999')
                }
              }
              .width('100%')
              .height(60)
              .justifyContent(FlexAlign.Center)
            }
            .onClick(() => {
              this.loadMore()
            })
          } else {
            ListItem() {
              Text('没有更多了')
                .fontSize(14)
                .fontColor('#999')
                .width('100%')
                .height(60)
                .textAlign(TextAlign.Center)
            }
          }
        }
        .width('100%')
        .layoutWeight(1)
        .backgroundColor('#F5F5F5')
        .edgeEffect(EdgeEffect.Spring)
        .onReachEnd(() => {
          this.loadMore()
        })
        .onScrollFrameBegin((offset: number) => {
          // 下拉刷新逻辑(简化版)
          if (offset < -100 && !this.isRefreshing && !this.isLoading) {
            this.handleRefresh()
          }
          return { offsetRemain: offset }
        })

      } else if (this.isLoading) {
        // 首次加载
        Column() {
          LoadingProgress()
            .width(50)
            .height(50)
            .margin({ bottom: 20 })

          Text('加载中...')
            .fontSize(16)
            .fontColor('#999')
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#F5F5F5')

      } else {
        // 空状态
        Column() {
          Image($r('app.media.empty'))
            .width(150)
            .height(150)
            .margin({ bottom: 20 })

          Text('暂无打卡记录')
            .fontSize(18)
            .fontColor('#999')
            .margin({ bottom: 10 })

          Text('完成首次打卡后,记录将显示在这里')
            .fontSize(14)
            .fontColor('#CCCCCC')
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#F5F5F5')
      }
    }
    .width('100%')
    .height('100%')
  }
}