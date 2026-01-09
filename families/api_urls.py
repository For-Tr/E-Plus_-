"""
家庭管理REST API路由
"""
from django.urls import path
from . import api_views

app_name = 'families_api'

urlpatterns = [
    # 邀请码管理
    path('invite/generate/', api_views.GenerateInviteCodeAPIView.as_view(), name='generate_invite'),
    path('invite/list/', api_views.InviteCodeListAPIView.as_view(), name='invite_list'),
    path('invite/revoke/<str:code>/', api_views.RevokeInviteCodeAPIView.as_view(), name='revoke_invite'),
    
    # 家庭信息
    path('detail/', api_views.FamilyDetailAPIView.as_view(), name='detail'),
    path('members/', api_views.FamilyMembersAPIView.as_view(), name='members'),
    path('members/<int:member_id>/remove/', api_views.RemoveMemberAPIView.as_view(), name='remove_member'),
]