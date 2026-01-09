"""
家庭管理Web视图路由(Django模板)
"""
from django.urls import path
from . import views

app_name = 'families'

urlpatterns = [
    # 家庭仪表板
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 邀请码管理
    path('invites/', views.invite_list, name='invite_list'),
    path('invites/generate/', views.generate_invite, name='generate_invite'),
    
    # 成员管理
    path('members/', views.member_list, name='member_list'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
]