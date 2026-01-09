"""
打卡相关Celery任务
"""
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.conf import settings

from checkins.models import CheckinTask, CheckinRecord
from users.models import User
from notifications.models import Notification


@shared_task
def send_checkin_reminders():
    """
    发送打卡提醒
    每天定时执行,向需要打卡的用户发送提醒
    """
    print(f"[{datetime.now()}] 开始发送打卡提醒...")
    
    # 获取所有激活的打卡任务
    active_tasks = CheckinTask.objects.filter(is_active=True).select_related('family')
    
    reminder_count = 0
    
    for task in active_tasks:
        # 获取任务的目标成员
        if task.target_members:
            # 指定成员
            target_users = User.objects.filter(
                id__in=task.target_members,
                status='active'
            )
        else:
            # 所有家庭成员
            target_users = User.objects.filter(
                family=task.family,
                status='active',
                role='family_member'
            )
        
        # 检查今天是否已打卡
        today = timezone.now().date()
        today_checkins = CheckinRecord.objects.filter(
            task=task,
            checkin_time__date=today
        ).values_list('user_id', flat=True)
        
        # 发送提醒给未打卡的用户
        for user in target_users:
            if user.id in today_checkins:
                continue
            
            # 创建通知
            Notification.objects.create(
                notification_type=Notification.TYPE_IN_APP,
                recipient=user,
                recipient_email=user.email or '',
                subject=f'打卡提醒: {task.task_name}',
                content=f'您好 {user.display_name},今天还未完成"{task.task_name}"打卡,请及时完成。',
                related_type='checkin_task',
                related_id=task.id,
                status=Notification.STATUS_PENDING
            )
            reminder_count += 1
    
    print(f"[{datetime.now()}] 打卡提醒发送完成,共发送 {reminder_count} 条提醒")
    return reminder_count


@shared_task
def detect_missed_checkins():
    """
    检测未打卡情况
    每天定时执行,检测应打卡但未打卡的情况,通知家庭管理员
    """
    print(f"[{datetime.now()}] 开始检测未打卡情况...")
    
    today = timezone.now().date()
    missed_count = 0
    
    # 获取所有激活的每日任务
    daily_tasks = CheckinTask.objects.filter(
        is_active=True,
        task_type=CheckinTask.TYPE_DAILY
    ).select_related('family', 'family__admin')
    
    for task in daily_tasks:
        # 获取应打卡的用户
        if task.target_members:
            target_users = User.objects.filter(
                id__in=task.target_members,
                status='active'
            )
        else:
            target_users = User.objects.filter(
                family=task.family,
                status='active',
                role='family_member'
            )
        
        # 检查未打卡的用户
        checkin_user_ids = CheckinRecord.objects.filter(
            task=task,
            checkin_time__date=today
        ).values_list('user_id', flat=True)
        
        missed_users = target_users.exclude(id__in=checkin_user_ids)
        
        if missed_users.exists():
            # 通知家庭管理员
            admin = task.family.admin
            missed_names = ', '.join([u.display_name for u in missed_users])
            
            Notification.objects.create(
                notification_type=Notification.TYPE_EMAIL,
                recipient=admin,
                recipient_email=admin.email or '',
                subject=f'未打卡提醒: {task.task_name}',
                content=f'家庭"{task.family.family_name}"中以下成员今日未完成打卡:\n{missed_names}\n\n任务: {task.task_name}',
                related_type='checkin_task',
                related_id=task.id,
                status=Notification.STATUS_PENDING
            )
            missed_count += len(missed_users)
    
    print(f"[{datetime.now()}] 未打卡检测完成,共发现 {missed_count} 人未打卡")
    return missed_count


@shared_task
def process_late_checkins():
    """
    处理迟到打卡
    检查打卡记录,将超时的打卡标记为迟到
    """
    print(f"[{datetime.now()}] 开始处理迟到打卡...")
    
    # 获取今天的所有准时打卡记录
    today = timezone.now().date()
    on_time_records = CheckinRecord.objects.filter(
        checkin_time__date=today,
        status=CheckinRecord.STATUS_ON_TIME
    )
    
    late_count = 0
    
    for record in on_time_records:
        # 检查是否超时
        if record.scheduled_time:
            late_threshold = record.scheduled_time + timedelta(minutes=30)
            if record.checkin_time > late_threshold:
                record.status = CheckinRecord.STATUS_LATE
                record.save()
                late_count += 1
    
    print(f"[{datetime.now()}] 迟到打卡处理完成,共标记 {late_count} 条记录为迟到")
    return late_count