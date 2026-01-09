"""
用户REST API路由(给鸿蒙App使用)
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'users_api'

urlpatterns = [
    # JWT认证
    path('login/', api_views.LoginAPIView.as_view(), name='login'),
    path('invite-login/', api_views.InviteCodeLoginAPIView.as_view(), name='invite_login'),  # 邀请码登录(推荐)
    path('register/', api_views.RegisterAPIView.as_view(), name='register'),  # 已废弃
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    
    # 用户信息
    path('me/', api_views.CurrentUserAPIView.as_view(), name='current_user'),
    path('me/update/', api_views.UpdateUserAPIView.as_view(), name='update_user'),
    path('me/change-password/', api_views.ChangePasswordAPIView.as_view(), name='change_password'),
    
    # 人脸注册
    path('face/register/', api_views.RegisterFaceAPIView.as_view(), name='register_face'),
    path('face/verify/', api_views.VerifyFaceAPIView.as_view(), name='verify_face'),
    
    # 邀请码
    path('invite/validate/', api_views.ValidateInviteAPIView.as_view(), name='validate_invite'),
    path('invite/accept/', api_views.AcceptInviteAPIView.as_view(), name='accept_invite'),
]