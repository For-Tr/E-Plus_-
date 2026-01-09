"""
用户Web页面路由(Django模板)
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 认证相关
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('accept-invite/<str:code>/', views.accept_invite, name='accept_invite'),
    
    # 用户中心
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/register-face/', views.register_face, name='register_face'),
]