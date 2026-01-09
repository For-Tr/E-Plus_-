"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # Web应用(Django模板)
    path('', include('users.urls')),  # 用户相关页面
    path('families/', include('families.urls')),  # 家庭管理页面
    path('checkins/', include('checkins.urls')),  # 打卡管理页面
    path('emotions/', include('emotions.urls')),  # 表情记录页面
    path('notifications/', include('notifications.urls')),  # 通知页面
    
    # REST API(给鸿蒙App使用)
    path('api/v1/auth/', include('users.api_urls')),  # 认证API
    path('api/v1/families/', include('families.api_urls')),  # 家庭API
    path('api/v1/checkins/', include('checkins.api_urls')),  # 打卡API
    path('api/v1/emotions/', include('emotions.api_urls')),  # 表情API
    path('api/v1/notifications/', include('notifications.api_urls')),  # 通知API
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 自定义管理后台标题
admin.site.site_header = "家庭情绪管理系统"
admin.site.site_title = "管理后台"
admin.site.index_title = "欢迎使用家庭情绪管理系统"