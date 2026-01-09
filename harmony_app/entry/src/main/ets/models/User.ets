/**
 * 用户数据模型
 */
import { UserRole } from '../common/constants/AppConstants'

export interface Family {
  id: number
  name: string
}

export interface User {
  id: number
  username: string
  display_name: string
  email?: string
  role: UserRole
  face_registered: boolean
  family?: Family
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
  invite_code: string
}