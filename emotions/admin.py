"""
表情模型Admin配置
"""
from django.contrib import admin
from .models import EmotionRecord, FaceEncoding


@admin.register(EmotionRecord)
class EmotionRecordAdmin(admin.ModelAdmin):
    """表情记录管理"""
    
    list_display = ['user', 'emotion', 'confidence', 'emotion_score', 'is_negative', 'face_encoding_match', 'recorded_at']
    list_filter = ['emotion', 'face_encoding_match', 'recorded_at']
    search_fields = ['user__username', 'user__display_name']
    ordering = ['-recorded_at']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'family', 'checkin_record')
        }),
        ('表情识别', {
            'fields': ('emotion', 'confidence', 'all_probabilities')
        }),
        ('AI分析', {
            'fields': ('ai_analysis', 'context_info')
        }),
        ('人脸匹配', {
            'fields': ('face_encoding_match',)
        }),
        ('照片', {
            'fields': ('photo_path',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('recorded_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['recorded_at']
    
    def emotion_score(self, obj):
        return obj.emotion_score
    emotion_score.short_description = '情绪评分'
    
    def is_negative(self, obj):
        return obj.is_negative
    is_negative.boolean = True
    is_negative.short_description = '负面情绪'


@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    """人脸特征管理"""
    
    list_display = ['user', 'is_primary', 'quality_score', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['user__username', 'user__display_name']
    ordering = ['-is_primary', '-created_at']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('特征信息', {
            'fields': ('encoding_json', 'quality_score', 'is_primary')
        }),
        ('照片', {
            'fields': ('photo_path',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']