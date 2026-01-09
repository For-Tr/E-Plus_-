"""
表情记录Web视图路由(Django模板)
"""
from django.urls import path
from . import views

app_name = 'emotions'

urlpatterns = [
    # 表情记录
    path('records/', views.record_list, name='record_list'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
    
    # 表情统计
    path('statistics/', views.statistics, name='statistics'),
    path('trends/', views.trends, name='trends'),
]