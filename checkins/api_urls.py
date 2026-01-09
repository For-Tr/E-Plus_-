"""
打卡REST API路由
"""
from django.urls import path
from . import api_views

app_name = 'checkins_api'

urlpatterns = [
    # 打卡任务
    path('my-tasks/', api_views.MyTasksAPIView.as_view(), name='my_tasks'),
    
    # 提交打卡
    path('submit/', api_views.SubmitCheckinAPIView.as_view(), name='submit'),
    
    # 打卡记录
    path('records/', api_views.CheckinRecordsAPIView.as_view(), name='records'),
    
    # 打卡统计
    path('statistics/', api_views.CheckinStatisticsAPIView.as_view(), name='statistics'),
]