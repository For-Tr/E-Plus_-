/**
 * 本地存储工具类
 */
import preferences from '@ohos.data.preferences'
import { USE_MOCK_DATA } from '../constants/AppConstants'

class StorageUtil {
  private static instance: StorageUtil
  private preferences: preferences.Preferences | null = null
  private readonly STORE_NAME = 'family_emotion_prefs'
  // Mock模式下使用内存存储
  private mockStorage: Map<string, string | boolean> = new Map()

  private constructor() {}

  public static getInstance(): StorageUtil {
    if (!StorageUtil.instance) {
      StorageUtil.instance = new StorageUtil()
    }
    return StorageUtil.instance
  }

  /**
   * 初始化存储
   */
  async init(context: Context): Promise<void> {
    try {
      this.preferences = await preferences.getPreferences(context, this.STORE_NAME)
      console.info('[StorageUtil] Storage initialized')
    } catch (error) {
      console.error('[StorageUtil] Init failed:', JSON.stringify(error))
    }
  }

  /**
   * 保存字符串
   */
  async setString(key: string, value: string): Promise<boolean> {
    try {
      // Mock模式:使用内存存储
      if (USE_MOCK_DATA || !this.preferences) {
        this.mockStorage.set(key, value)
        console.info(`[StorageUtil] Mock saved: ${key}`)
        return true
      }
      
      await this.preferences.put(key, value)
      await this.preferences.flush()
      console.info(`[StorageUtil] Saved: ${key}`)
      return true
    } catch (error) {
      console.error(`[StorageUtil] Save failed: ${key}`, JSON.stringify(error))
      // 失败时降级到Mock存储
      this.mockStorage.set(key, value)
      return true
    }
  }

  /**
   * 获取字符串
   */
  async getString(key: string, defaultValue: string = ''): Promise<string> {
    try {
      // Mock模式:使用内存存储
      if (USE_MOCK_DATA || !this.preferences) {
        const value = this.mockStorage.get(key)
        return (value as string) || defaultValue
      }
      
      const value = await this.preferences.get(key, defaultValue)
      return value as string
    } catch (error) {
      console.error(`[StorageUtil] Get failed: ${key}`, JSON.stringify(error))
      // 失败时从Mock存储读取
      const value = this.mockStorage.get(key)
      return (value as string) || defaultValue
    }
  }

  /**
   * 保存对象(JSON)
   */
  async setObject(key: string, value: object): Promise<boolean> {
    try {
      const jsonString = JSON.stringify(value)
      return await this.setString(key, jsonString)
    } catch (error) {
      console.error(`[StorageUtil] Save object failed: ${key}`, JSON.stringify(error))
      return false
    }
  }

  /**
   * 获取对象(JSON)
   */
  async getObject(key: string): Promise<object | null> {
    try {
      const jsonString = await this.getString(key)
      if (jsonString) {
        return JSON.parse(jsonString)
      }
      return null
    } catch (error) {
      console.error(`[StorageUtil] Get object failed: ${key}`, JSON.stringify(error))
      return null
    }
  }

  /**
   * 保存布尔值
   */
  async setBoolean(key: string, value: boolean): Promise<boolean> {
    try {
      // Mock模式:使用内存存储
      if (USE_MOCK_DATA || !this.preferences) {
        this.mockStorage.set(key, value)
        console.info(`[StorageUtil] Mock saved boolean: ${key}`)
        return true
      }
      
      await this.preferences.put(key, value)
      await this.preferences.flush()
      return true
    } catch (error) {
      console.error(`[StorageUtil] Save boolean failed: ${key}`, JSON.stringify(error))
      // 失败时降级到Mock存储
      this.mockStorage.set(key, value)
      return true
    }
  }

  /**
   * 获取布尔值
   */
  async getBoolean(key: string, defaultValue: boolean = false): Promise<boolean> {
    try {
      // Mock模式:使用内存存储
      if (USE_MOCK_DATA || !this.preferences) {
        const value = this.mockStorage.get(key)
        return (value as boolean) ?? defaultValue
      }
      
      const value = await this.preferences.get(key, defaultValue)
      return value as boolean
    } catch (error) {
      console.error(`[StorageUtil] Get boolean failed: ${key}`, JSON.stringify(error))
      const value = this.mockStorage.get(key)
      return (value as boolean) ?? defaultValue
    }
  }

  /**
   * 删除数据
   */
  async remove(key: string): Promise<boolean> {
    try {
      if (!this.preferences) {
        return false
      }
      await this.preferences.delete(key)
      await this.preferences.flush()
      console.info(`[StorageUtil] Removed: ${key}`)
      return true
    } catch (error) {
      console.error(`[StorageUtil] Remove failed: ${key}`, JSON.stringify(error))
      return false
    }
  }

  /**
   * 清空所有数据
   */
  async clear(): Promise<boolean> {
    try {
      if (!this.preferences) {
        return false
      }
      await this.preferences.clear()
      await this.preferences.flush()
      console.info('[StorageUtil] Cleared all data')
      return true
    } catch (error) {
      console.error('[StorageUtil] Clear failed:', JSON.stringify(error))
      return false
    }
  }

  /**
   * 检查键是否存在
   */
  async has(key: string): Promise<boolean> {
    try {
      if (!this.preferences) {
        return false
      }
      return await this.preferences.has(key)
    } catch (error) {
      console.error(`[StorageUtil] Has check failed: ${key}`, JSON.stringify(error))
      return false
    }
  }
}

export default StorageUtil.getInstance()