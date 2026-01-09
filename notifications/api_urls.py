"""
通知REST API路由
"""
from django.urls import path
from . import api_views

app_name = 'notifications_api'

urlpatterns = [
    # 通知列表
    path('', api_views.NotificationListAPIView.as_view(), name='list'),
    path('<int:notification_id>/', api_views.NotificationDetailAPIView.as_view(), name='detail'),
    path('<int:notification_id>/mark-read/', api_views.MarkReadAPIView.as_view(), name='mark_read'),
]