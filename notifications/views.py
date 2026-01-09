"""
通知Web视图(Django模板) - 占位视图
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def notification_list(request):
    """通知列表"""
    return HttpResponse("Notifications - Coming Soon")


@login_required
def notification_detail(request, notification_id):
    """通知详情"""
    return HttpResponse(f"Notification {notification_id} - Coming Soon")


@login_required
def mark_read(request, notification_id):
    """标记为已读"""
    return HttpResponse(f"Mark {notification_id} as Read - Coming Soon")