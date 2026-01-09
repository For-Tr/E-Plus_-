"""
打卡管理Web视图路由(Django模板)
"""
from django.urls import path
from . import views

app_name = 'checkins'

urlpatterns = [
    # 打卡任务管理
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    
    # 打卡记录
    path('records/', views.record_list, name='record_list'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
]