"""
表情分析REST API路由
"""
from django.urls import path
from . import api_views

app_name = 'emotions_api'

urlpatterns = [
    # 表情分析
    path('analyze/', api_views.AnalyzeEmotionAPIView.as_view(), name='analyze'),
    
    # 表情记录
    path('records/', api_views.EmotionRecordsAPIView.as_view(), name='records'),
    
    # 表情统计
    path('statistics/', api_views.EmotionStatisticsAPIView.as_view(), name='statistics'),
    
    # 情绪趋势
    path('trends/', api_views.EmotionTrendsAPIView.as_view(), name='trends'),
]