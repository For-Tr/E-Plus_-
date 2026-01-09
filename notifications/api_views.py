"""
通知REST API视图
"""
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notifications.models import Notification


class NotificationListAPIView(APIView):
    """获取通知列表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 获取查询参数
        notification_type = request.query_params.get('type')
        status_filter = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 构建查询
        queryset = Notification.objects.filter(recipient=user)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 排序
        queryset = queryset.order_by('-created_at')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        notifications = queryset[start:end]
        
        # 序列化
        result = []
        for notification in notifications:
            result.append({
                'id': notification.id,
                'type': notification.notification_type,
                'type_display': notification.get_notification_type_display(),
                'subject': notification.subject,
                'content': notification.content,
                'status': notification.status,
                'status_display': notification.get_status_display(),
                'created_at': notification.created_at,
                'sent_at': notification.sent_at,
                'read_at': notification.read_at,
                'related_type': notification.related_type,
                'related_id': notification.related_id
            })
        
        # 未读数量
        unread_count = Notification.objects.filter(
            recipient=user,
            status__in=[Notification.STATUS_PENDING, Notification.STATUS_SENT]
        ).count()
        
        return Response({
            'notifications': result,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
            'unread_count': unread_count
        })


class NotificationDetailAPIView(APIView):
    """获取通知详情"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            
            # 自动标记为已读
            if notification.status == Notification.STATUS_SENT:
                notification.mark_as_read()
            
            return Response({
                'id': notification.id,
                'type': notification.notification_type,
                'type_display': notification.get_notification_type_display(),
                'subject': notification.subject,
                'content': notification.content,
                'status': notification.status,
                'status_display': notification.get_status_display(),
                'created_at': notification.created_at,
                'sent_at': notification.sent_at,
                'read_at': notification.read_at,
                'related_type': notification.related_type,
                'related_id': notification.related_id
            })
            
        except Notification.DoesNotExist:
            return Response({
                'error': '通知不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class MarkReadAPIView(APIView):
    """标记通知为已读"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            
            notification.mark_as_read()
            
            return Response({
                'message': '已标记为已读',
                'notification_id': notification_id
            })
            
        except Notification.DoesNotExist:
            return Response({
                'error': '通知不存在'
            }, status=status.HTTP_404_NOT_FOUND)