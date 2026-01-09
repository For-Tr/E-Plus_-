"""
通知相关Celery任务
"""
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg

from notifications.models import Notification
from notifications.services import email_service
from emotions.models import EmotionRecord
from users.models import User
from families.models import Family


@shared_task
def send_pending_notifications():
    """
    发送待发送的通知
    处理所有状态为pending的邮件通知
    """
    print(f"[{datetime.now()}] 开始发送待发送通知...")
    
    # 获取所有待发送的邮件通知
    pending_emails = Notification.objects.filter(
        notification_type=Notification.TYPE_EMAIL,
        status=Notification.STATUS_PENDING
    )
    
    result = email_service.send_batch_emails(pending_emails)
    
    print(f"[{datetime.now()}] 通知发送完成: 成功 {result['success']}, 失败 {result['failed']}")
    return result


@shared_task
def detect_emotion_anomalies():
    """
    检测情绪异常
    分析最近的情绪记录,发现异常情况时通知家庭管理员
    """
    print(f"[{datetime.now()}] 开始检测情绪异常...")
    
    today = timezone.now().date()
    alert_count = 0
    
    # 获取所有家庭
    families = Family.objects.filter(status=Family.STATUS_ACTIVE)
    
    for family in families:
        admin = family.admin
        members = User.objects.filter(family=family, status='active', role='family_member')
        
        for member in members:
            # 检查今天的负面情绪
            today_negative = EmotionRecord.objects.filter(
                user=member,
                recorded_at__date=today,
                emotion__in=[EmotionRecord.EMOTION_ANGRY, EmotionRecord.EMOTION_DISGUST, 
                            EmotionRecord.EMOTION_SAD, EmotionRecord.EMOTION_FEAR],
                confidence__gte=0.70
            ).first()
            
            if today_negative:
                # 发送通知
                Notification.objects.create(
                    notification_type=Notification.TYPE_EMAIL,
                    recipient=admin,
                    recipient_email=admin.email or '',
                    subject=f'情绪异常提醒: {member.display_name}',
                    content=f'家庭成员 {member.display_name} 检测到异常情绪:\n\n表情: {today_negative.get_emotion_display()}\n置信度: {today_negative.confidence:.2%}\n时间: {today_negative.recorded_at}\n\n建议及时关注该成员的情绪状态。',
                    related_type='emotion_record',
                    related_id=today_negative.id,
                    status=Notification.STATUS_PENDING
                )
                alert_count += 1
                continue
            
            # 检查连续3天负面情绪
            last_3days = timezone.now() - timedelta(days=3)
            negative_count = EmotionRecord.objects.filter(
                user=member,
                recorded_at__gte=last_3days,
                emotion__in=[EmotionRecord.EMOTION_ANGRY, EmotionRecord.EMOTION_DISGUST, 
                            EmotionRecord.EMOTION_SAD, EmotionRecord.EMOTION_FEAR]
            ).count()
            
            total_count = EmotionRecord.objects.filter(
                user=member,
                recorded_at__gte=last_3days
            ).count()
            
            if total_count >= 3 and negative_count / total_count >= 0.6:
                # 发送通知
                Notification.objects.create(
                    notification_type=Notification.TYPE_EMAIL,
                    recipient=admin,
                    recipient_email=admin.email or '',
                    subject=f'情绪趋势提醒: {member.display_name}',
                    content=f'家庭成员 {member.display_name} 最近3天情绪不佳:\n\n负面情绪占比: {negative_count/total_count:.1%}\n记录次数: {total_count}\n\n建议及时关注该成员的情绪状态。',
                    related_type='emotion_trend',
                    related_id=member.id,
                    status=Notification.STATUS_PENDING
                )
                alert_count += 1
    
    print(f"[{datetime.now()}] 情绪异常检测完成,共发现 {alert_count} 条异常")
    return alert_count


@shared_task
def send_weekly_report():
    """
    发送周报
    每周一发送上周的打卡和情绪汇总报告
    """
    print(f"[{datetime.now()}] 开始生成周报...")
    
    # 获取上周的日期范围
    today = timezone.now().date()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    
    report_count = 0
    
    # 获取所有家庭
    families = Family.objects.filter(status=Family.STATUS_ACTIVE)
    
    for family in families:
        admin = family.admin
        members = User.objects.filter(family=family, status='active')
        
        # 统计打卡情况
        from checkins.models import CheckinRecord
        checkin_stats = CheckinRecord.objects.filter(
            family=family,
            checkin_time__date__gte=last_monday,
            checkin_time__date__lte=last_sunday
        ).aggregate(
            total=Count('id'),
            on_time=Count('id', filter={'status': CheckinRecord.STATUS_ON_TIME}),
            late=Count('id', filter={'status': CheckinRecord.STATUS_LATE})
        )
        
        # 统计情绪情况
        emotion_stats = EmotionRecord.objects.filter(
            family=family,
            recorded_at__date__gte=last_monday,
            recorded_at__date__lte=last_sunday
        ).values('emotion').annotate(count=Count('id'))
        
        # 生成报告内容
        content = f"""家庭"{family.family_name}"上周汇总报告

时间范围: {last_monday} 至 {last_sunday}
成员人数: {members.count()}

打卡统计:
- 总打卡次数: {checkin_stats['total']}
- 准时打卡: {checkin_stats['on_time']}
- 迟到打卡: {checkin_stats['late']}

情绪统计:
"""
        for stat in emotion_stats:
            emotion_display = dict(EmotionRecord.EMOTION_CHOICES).get(stat['emotion'], stat['emotion'])
            content += f"- {emotion_display}: {stat['count']}次\n"
        
        # 创建通知
        Notification.objects.create(
            notification_type=Notification.TYPE_EMAIL,
            recipient=admin,
            recipient_email=admin.email or '',
            subject=f'家庭周报: {family.family_name} ({last_monday} - {last_sunday})',
            content=content,
            related_type='weekly_report',
            related_id=family.id,
            status=Notification.STATUS_PENDING
        )
        report_count += 1
    
    print(f"[{datetime.now()}] 周报生成完成,共生成 {report_count} 份周报")
    return report_count


@shared_task
def cleanup_old_notifications():
    """
    清理旧通知
    删除超过30天的已读通知
    """
    print(f"[{datetime.now()}] 开始清理旧通知...")
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # 删除已读且超过30天的通知
    deleted_count, _ = Notification.objects.filter(
        status=Notification.STATUS_READ,
        read_at__lt=cutoff_date
    ).delete()
    
    print(f"[{datetime.now()}] 旧通知清理完成,共删除 {deleted_count} 条通知")
    return deleted_count