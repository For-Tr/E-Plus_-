/**
 * 打卡任务数据模型
 */

export interface CheckinTask {
  id: number
  task_name: string
  task_type: 'daily' | 'weekly' | 'custom'
  family: number
  is_active: boolean
  schedule_config: object
  reminder_config: object
  created_at: string
  updated_at: string
}

export interface CheckinTaskListResponse {
  count: number
  results: CheckinTask[]
}