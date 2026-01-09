/**
 * 打卡记录数据模型
 */
import { CheckinStatus, EmotionType } from '../common/constants/AppConstants'

export interface CheckinRecord {
  id: number
  user: number
  task: number
  family: number
  checkin_time: string
  status: CheckinStatus
  face_photo?: string
  face_verified: boolean
  emotion?: EmotionType
  emotion_confidence?: number
  emotion_detail?: object
  location?: string
  note?: string
  created_at: string
}

export interface CheckinCreateRequest {
  task_id: number
  photo: string  // Base64编码的图片
  location?: string
  note?: string
}

export interface CheckinRecordListResponse {
  count: number
  next?: string
  previous?: string
  results: CheckinRecord[]
}