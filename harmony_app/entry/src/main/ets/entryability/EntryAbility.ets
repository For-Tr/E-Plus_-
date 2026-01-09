/**
 * 应用入口Ability
 */
import UIAbility from '@ohos.app.ability.UIAbility'
import hilog from '@ohos.hilog'
import window from '@ohos.window'
import StorageUtil from '../common/utils/StorageUtil'

export default class EntryAbility extends UIAbility {
  onCreate(want, launchParam) {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onCreate')
    
    // 初始化本地存储
    StorageUtil.init(this.context)
  }

  onDestroy() {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onDestroy')
  }

  onWindowStageCreate(windowStage: window.WindowStage) {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onWindowStageCreate')

    windowStage.loadContent('pages/Index', (err, data) => {
      if (err.code) {
        hilog.error(0x0000, 'FamilyEmotion', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? '')
        return
      }
      hilog.info(0x0000, 'FamilyEmotion', 'Succeeded in loading the content. Data: %{public}s', JSON.stringify(data) ?? '')
    })
  }

  onWindowStageDestroy() {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onWindowStageDestroy')
  }

  onForeground() {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onForeground')
  }

  onBackground() {
    hilog.info(0x0000, 'FamilyEmotion', '%{public}s', 'Ability onBackground')
  }
}