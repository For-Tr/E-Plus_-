"""
通知模型Admin配置
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理"""
    
    list_display = ['recipient', 'notification_type', 'subject', 'status', 'created_at', 'sent_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['recipient__username', 'subject', 'content']
    ordering = ['-created_at']
    
    fieldsets = (
        ('通知信息', {
            'fields': ('notification_type', 'recipient', 'recipient_email', 'subject', 'content')
        }),
        ('关联信息', {
            'fields': ('related_type', 'related_id'),
            'classes': ('collapse',)
        }),
        ('状态', {
            'fields': ('status', 'error_message')
        }),
        ('时间信息', {
            'fields': ('created_at', 'sent_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    actions = ['mark_as_sent', 'mark_as_failed']
    
    def mark_as_sent(self, request, queryset):
        queryset.update(status=Notification.STATUS_SENT)
        self.message_user(request, f'{queryset.count()} 条通知已标记为已发送')
    mark_as_sent.short_description = '标记为已发送'
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status=Notification.STATUS_FAILED)
        self.message_user(request, f'{queryset.count()} 条通知已标记为发送失败')
    mark_as_failed.short_description = '标记为发送失败'