"""
打卡模型Admin配置
"""
from django.contrib import admin
from .models import CheckinTask, CheckinRecord


@admin.register(CheckinTask)
class CheckinTaskAdmin(admin.ModelAdmin):
    """打卡任务管理"""
    
    list_display = ['task_name', 'family', 'task_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['task_type', 'is_active', 'created_at']
    search_fields = ['task_name', 'family__family_name', 'created_by__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('task_name', 'family', 'task_type', 'created_by')
        }),
        ('目标成员', {
            'fields': ('target_members',)
        }),
        ('配置信息', {
            'fields': ('schedule_config', 'reminder_config', 'emotion_threshold')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CheckinRecord)
class CheckinRecordAdmin(admin.ModelAdmin):
    """打卡记录管理"""
    
    list_display = ['user', 'task', 'checkin_time', 'status', 'face_verified', 'emotion_detected', 'emotion_confidence']
    list_filter = ['status', 'face_verified', 'emotion_detected', 'checkin_time']
    search_fields = ['user__username', 'task__task_name']
    ordering = ['-checkin_time']
    
    fieldsets = (
        ('打卡信息', {
            'fields': ('task', 'user', 'family', 'checkin_time', 'scheduled_time', 'status')
        }),
        ('人脸验证', {
            'fields': ('face_verified',)
        }),
        ('表情识别', {
            'fields': ('emotion_detected', 'emotion_confidence', 'emotion_probs', 'ai_analysis')
        }),
        ('附加信息', {
            'fields': ('photo_path', 'location'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']