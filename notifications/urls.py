"""
通知Web视图路由(Django模板)
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # 通知列表
    path('', views.notification_list, name='list'),
    path('<int:notification_id>/', views.notification_detail, name='detail'),
    path('<int:notification_id>/mark-read/', views.mark_read, name='mark_read'),
]