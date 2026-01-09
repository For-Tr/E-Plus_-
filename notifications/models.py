"""
通知相关模型
"""
from django.db import models
from django.utils import timezone
from django.conf import settings


class Notification(models.Model):
    """通知记录模型"""
    
    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'
    TYPE_PUSH = 'push'
    TYPE_IN_APP = 'in_app'
    
    TYPE_CHOICES = [
        (TYPE_EMAIL, '邮件'),
        (TYPE_SMS, '短信'),
        (TYPE_PUSH, '推送'),
        (TYPE_IN_APP, '站内信'),
    ]
    
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_READ = 'read'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, '待发送'),
        (STATUS_SENT, '已发送'),
        (STATUS_FAILED, '发送失败'),
        (STATUS_READ, '已读'),
    ]
    
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收者'
    )
    recipient_email = models.EmailField('接收邮箱', blank=True)
    subject = models.CharField('主题', max_length=200)
    content = models.TextField('内容')
    
    related_type = models.CharField('关联类型', max_length=50, blank=True)
    related_id = models.BigIntegerField('关联ID', null=True, blank=True)
    
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sent_at = models.DateTimeField('发送时间', null=True, blank=True)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.subject}"
    
    def mark_as_read(self):
        """标记为已读"""
        if self.status == self.STATUS_SENT:
            self.status = self.STATUS_READ
            self.read_at = timezone.now()
            self.save()