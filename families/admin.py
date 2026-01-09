"""
家庭模型Admin配置
"""
from django.contrib import admin
from .models import Family, InviteCode


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    """家庭管理"""
    
    list_display = ['family_name', 'family_code', 'admin', 'member_count', 'max_members', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['family_name', 'family_code', 'admin__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('family_name', 'family_code', 'admin', 'description')
        }),
        ('设置', {
            'fields': ('max_members', 'settings_json', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['family_code', 'created_at', 'updated_at']


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    """邀请码管理"""
    
    list_display = ['code', 'username_for', 'display_name_for', 'family', 'status', 'used_count', 'max_uses', 'expires_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'username_for', 'family__family_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('邀请码信息', {
            'fields': ('code', 'family', 'created_by')
        }),
        ('目标用户', {
            'fields': ('username_for', 'display_name_for')
        }),
        ('使用限制', {
            'fields': ('max_uses', 'used_count', 'expires_at', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['code', 'created_at']