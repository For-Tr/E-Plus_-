"""
通知服务 - 邮件发送等
"""
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from notifications.models import Notification


class EmailService:
    """邮件发送服务"""
    
    @staticmethod
    def send_notification_email(notification):
        """
        发送通知邮件
        
        Args:
            notification: Notification对象
        
        Returns:
            bool: 是否发送成功
        """
        try:
            # 检查邮箱地址
            if not notification.recipient_email:
                notification.status = Notification.STATUS_FAILED
                notification.error_message = '收件人邮箱为空'
                notification.save()
                return False
            
            # 发送邮件
            send_mail(
                subject=notification.subject,
                message=notification.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                fail_silently=False,
            )
            
            # 标记为已发送
            notification.status = Notification.STATUS_SENT
            notification.sent_at = timezone.now()
            notification.save()
            
            return True
            
        except Exception as e:
            # 发送失败
            notification.status = Notification.STATUS_FAILED
            notification.error_message = str(e)
            notification.save()
            return False
    
    @staticmethod
    def send_batch_emails(notifications):
        """
        批量发送邮件
        
        Args:
            notifications: Notification查询集
        
        Returns:
            dict: 发送结果统计
        """
        success_count = 0
        failed_count = 0
        
        for notification in notifications:
            if EmailService.send_notification_email(notification):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': success_count + failed_count
        }


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def create_checkin_reminder(user, task):
        """创建打卡提醒"""
        return Notification.objects.create(
            notification_type=Notification.TYPE_IN_APP,
            recipient=user,
            recipient_email=user.email or '',
            subject=f'打卡提醒: {task.task_name}',
            content=f'您好 {user.display_name},今天还未完成"{task.task_name}"打卡,请及时完成。',
            related_type='checkin_task',
            related_id=task.id,
            status=Notification.STATUS_PENDING
        )
    
    @staticmethod
    def create_emotion_alert(admin, user, emotion_record):
        """创建情绪异常通知"""
        return Notification.objects.create(
            notification_type=Notification.TYPE_EMAIL,
            recipient=admin,
            recipient_email=admin.email or '',
            subject=f'情绪异常提醒: {user.display_name}',
            content=f'家庭成员 {user.display_name} 检测到异常情绪:\n\n表情: {emotion_record.get_emotion_display()}\n置信度: {emotion_record.confidence:.2%}\n时间: {emotion_record.recorded_at}\n\n建议及时关注该成员的情绪状态。',
            related_type='emotion_record',
            related_id=emotion_record.id,
            status=Notification.STATUS_PENDING
        )
    
    @staticmethod
    def create_missed_checkin_alert(admin, task, missed_users):
        """创建未打卡通知"""
        missed_names = ', '.join([u.display_name for u in missed_users])
        return Notification.objects.create(
            notification_type=Notification.TYPE_EMAIL,
            recipient=admin,
            recipient_email=admin.email or '',
            subject=f'未打卡提醒: {task.task_name}',
            content=f'家庭"{task.family.family_name}"中以下成员今日未完成打卡:\n{missed_names}\n\n任务: {task.task_name}',
            related_type='checkin_task',
            related_id=task.id,
            status=Notification.STATUS_PENDING
        )


# 全局实例
email_service = EmailService()
notification_service = NotificationService()