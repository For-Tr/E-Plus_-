"""
用户模型Admin配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    
    list_display = ['username', 'display_name', 'role', 'family', 'face_registered', 'status', 'date_joined']
    list_filter = ['role', 'status', 'face_registered', 'date_joined']
    search_fields = ['username', 'display_name', 'email', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'display_name', 'email', 'phone')
        }),
        ('角色与家庭', {
            'fields': ('role', 'family', 'created_by')
        }),
        ('人脸识别', {
            'fields': ('face_registered', 'face_encodings_count')
        }),
        ('状态', {
            'fields': ('status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('权限', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('date_joined', 'last_login', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'display_name', 'role', 'family'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'updated_at']