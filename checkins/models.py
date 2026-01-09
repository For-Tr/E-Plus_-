"""
打卡相关模型
"""
from django.db import models
from django.utils import timezone
from django.conf import settings


class CheckinTask(models.Model):
    """打卡任务模型"""
    
    TYPE_DAILY = 'daily'
    TYPE_WEEKLY = 'weekly'
    TYPE_CUSTOM = 'custom'
    
    TYPE_CHOICES = [
        (TYPE_DAILY, '每日打卡'),
        (TYPE_WEEKLY, '每周打卡'),
        (TYPE_CUSTOM, '自定义'),
    ]
    
    task_name = models.CharField('任务名称', max_length=100)
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='checkin_tasks',
        verbose_name='所属家庭'
    )
    task_type = models.CharField('任务类型', max_length=20, choices=TYPE_CHOICES)
    target_members = models.JSONField('目标成员', default=list, help_text='成员ID列表')
    schedule_config = models.JSONField('调度配置', default=dict)
    reminder_config = models.JSONField('提醒配置', default=dict)
    emotion_threshold = models.JSONField('情绪阈值设置', default=dict)
    is_active = models.BooleanField('是否激活', default=True, db_index=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'checkin_tasks'
        verbose_name = '打卡任务'
        verbose_name_plural = '打卡任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.task_name} ({self.get_task_type_display()})"


class CheckinRecord(models.Model):
    """打卡记录模型"""
    
    STATUS_ON_TIME = 'on_time'
    STATUS_LATE = 'late'
    STATUS_MISSED = 'missed'
    
    STATUS_CHOICES = [
        (STATUS_ON_TIME, '准时'),
        (STATUS_LATE, '迟到'),
        (STATUS_MISSED, '缺勤'),
    ]
    
    task = models.ForeignKey(
        CheckinTask,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='任务'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkin_records',
        verbose_name='用户'
    )
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        related_name='checkin_records',
        verbose_name='家庭'
    )
    
    checkin_time = models.DateTimeField('打卡时间')
    scheduled_time = models.DateTimeField('计划时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    
    face_verified = models.BooleanField('人脸验证', default=False)
    emotion_detected = models.CharField('检测表情', max_length=50, blank=True)
    emotion_confidence = models.FloatField('表情置信度', null=True, blank=True)
    emotion_probs = models.JSONField('所有表情概率', default=dict)
    photo_path = models.CharField('照片路径', max_length=255, blank=True)
    ai_analysis = models.TextField('AI分析', blank=True)
    location = models.JSONField('位置信息', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'checkin_records'
        verbose_name = '打卡记录'
        verbose_name_plural = '打卡记录'
        ordering = ['-checkin_time']
        indexes = [
            models.Index(fields=['task', 'user']),
            models.Index(fields=['family', 'checkin_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.checkin_time.strftime('%Y-%m-%d %H:%M')}"