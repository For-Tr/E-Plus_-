"""
打卡管理REST API视图（给鸿蒙App使用）
"""
import os
import base64
import cv2
import numpy as np
from datetime import datetime, timedelta
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from checkins.models import CheckinTask, CheckinRecord
from emotions.models import EmotionRecord
from emotions.services import face_recognition_service, emotion_recognition_service


class MyTasksAPIView(APIView):
    """获取我的打卡任务列表"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.family:
            return Response({
                'tasks': [],
                'message': '您还没有加入任何家庭'
            })
        
        # 获取活跃的任务
        tasks = CheckinTask.objects.filter(
            family=user.family,
            is_active=True
        ).order_by('-created_at')
        
        # 检查今天是否已打卡
        today = timezone.now().date()
        today_records = CheckinRecord.objects.filter(
            user=user,
            checkin_time__date=today
        ).values_list('task_id', flat=True)
        
        result = []
        for task in tasks:
            # 检查用户是否在目标成员列表中
            target_members = task.target_members
            if target_members and user.id not in target_members:
                continue
            
            # 获取最近一次打卡记录
            last_record = CheckinRecord.objects.filter(
                task=task,
                user=user
            ).order_by('-checkin_time').first()
            
            result.append({
                'id': task.id,
                'task_name': task.task_name,
                'task_type': task.task_type,
                'task_type_display': task.get_task_type_display(),
                'schedule_config': task.schedule_config,
                'checked_today': task.id in today_records,
                'last_checkin': {
                    'time': last_record.checkin_time,
                    'status': last_record.status,
                    'emotion': last_record.emotion_detected
                } if last_record else None
            })
        
        return Response({
            'tasks': result,
            'total': len(result)
        })


class SubmitCheckinAPIView(APIView):
    """提交打卡"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        task_id = request.data.get('task_id')
        
        if not task_id:
            return Response({
                'error': '任务ID不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查任务是否存在
        try:
            task = CheckinTask.objects.get(id=task_id, family=user.family, is_active=True)
        except CheckinTask.DoesNotExist:
            return Response({
                'error': '任务不存在或已停用'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查今天是否已打卡
        today = timezone.now().date()
        if CheckinRecord.objects.filter(task=task, user=user, checkin_time__date=today).exists():
            return Response({
                'error': '今天已经打过卡了'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取上传的照片
        if 'photo' not in request.FILES and 'photo' not in request.data:
            return Response({
                'error': '请上传打卡照片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 读取图片
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                img_bytes = photo.read()
            else:
                # base64格式
                photo_data = request.data['photo']
                if photo_data.startswith('data:image'):
                    photo_data = photo_data.split(',')[1]
                img_bytes = base64.b64decode(photo_data)
            
            # 转换为OpenCV格式
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return Response({
                    'error': '无效的图片格式'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 保存照片
            photo_dir = os.path.join('media', 'emotion_photos', user.username)
            os.makedirs(photo_dir, exist_ok=True)
            photo_filename = f'checkin_{timezone.now().strftime("%Y%m%d_%H%M%S")}.jpg'
            photo_path = os.path.join(photo_dir, photo_filename)
            cv2.imwrite(photo_path, img)
            
            # 1. 人脸识别验证
            face_verified = False
            recognized_user = None
            if user.face_registered:
                recognized_user, distance = face_recognition_service.recognize(img)
                face_verified = (recognized_user and recognized_user.id == user.id)
            
            # 2. 表情识别
            emotion_result = None
            try:
                # 转换为灰度图
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                emotion_result = emotion_recognition_service.detect_emotion(gray)
            except Exception as e:
                print(f"[ERROR] 表情识别失败: {e}")
            
            # 3. 判断打卡状态
            now = timezone.now()
            scheduled_time = None
            checkin_status = CheckinRecord.STATUS_ON_TIME
            
            # 简单判断：如果是每日任务，计划时间为配置的时间
            if task.task_type == 'daily' and task.schedule_config.get('time'):
                schedule_time_str = task.schedule_config.get('time')
                hour, minute = map(int, schedule_time_str.split(':'))
                scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 超过30分钟算迟到
                if now > scheduled_time + timedelta(minutes=30):
                    checkin_status = CheckinRecord.STATUS_LATE
            
            # 4. 保存打卡记录
            checkin_record = CheckinRecord.objects.create(
                task=task,
                user=user,
                family=user.family,
                checkin_time=now,
                scheduled_time=scheduled_time,
                status=checkin_status,
                face_verified=face_verified,
                emotion_detected=emotion_result['emotion'] if emotion_result else None,
                emotion_confidence=emotion_result['confidence'] if emotion_result else None,
                emotion_probs=emotion_result['probabilities'] if emotion_result else {},
                photo_path=photo_path,
                ai_analysis=emotion_result['ai_analysis'] if emotion_result else '',
                location=request.data.get('location', {})
            )
            
            # 5. 保存表情记录
            if emotion_result:
                EmotionRecord.objects.create(
                    user=user,
                    family=user.family,
                    checkin_record=checkin_record,
                    emotion=emotion_result['emotion'],
                    confidence=emotion_result['confidence'],
                    all_probabilities=emotion_result['probabilities'],
                    photo_path=photo_path,
                    face_encoding_match=face_verified,
                    ai_analysis=emotion_result
                )
            
            # 6. 检查是否需要发送异常通知
            if emotion_result and emotion_result['emotion'] in ['angry', 'disgust', 'sad', 'fear']:
                if emotion_result['confidence'] > 0.70:
                    # TODO: 发送邮件通知给家庭管理员
                    pass
            
            return Response({
                'message': '打卡成功',
                'record_id': checkin_record.id,
                'checkin_time': checkin_record.checkin_time,
                'status': checkin_record.status,
                'face_verified': face_verified,
                'emotion': emotion_result if emotion_result else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'打卡失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckinRecordsAPIView(APIView):
    """获取打卡记录"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 获取查询参数
        task_id = request.query_params.get('task_id')
        days = int(request.query_params.get('days', 7))  # 默认最近7天
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 构建查询
        queryset = CheckinRecord.objects.filter(user=user)
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        # 时间范围
        since_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(checkin_time__gte=since_date)
        
        # 排序
        queryset = queryset.order_by('-checkin_time')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        records = queryset[start:end]
        
        # 序列化
        result = []
        for record in records:
            result.append({
                'id': record.id,
                'task': {
                    'id': record.task.id,
                    'name': record.task.task_name
                },
                'checkin_time': record.checkin_time,
                'scheduled_time': record.scheduled_time,
                'status': record.status,
                'status_display': record.get_status_display(),
                'face_verified': record.face_verified,
                'emotion': {
                    'emotion': record.emotion_detected,
                    'confidence': record.emotion_confidence,
                    'probabilities': record.emotion_probs
                } if record.emotion_detected else None,
                'ai_analysis': record.ai_analysis,
                'photo_path': record.photo_path
            })
        
        return Response({
            'records': result,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        })


class CheckinStatisticsAPIView(APIView):
    """打卡统计"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        since_date = timezone.now() - timedelta(days=days)
        
        # 总打卡次数
        total_checkins = CheckinRecord.objects.filter(
            user=user,
            checkin_time__gte=since_date
        ).count()
        
        # 准时打卡次数
        on_time_count = CheckinRecord.objects.filter(
            user=user,
            checkin_time__gte=since_date,
            status=CheckinRecord.STATUS_ON_TIME
        ).count()
        
        # 迟到次数
        late_count = CheckinRecord.objects.filter(
            user=user,
            checkin_time__gte=since_date,
            status=CheckinRecord.STATUS_LATE
        ).count()
        
        # 缺勤次数
        missed_count = CheckinRecord.objects.filter(
            user=user,
            checkin_time__gte=since_date,
            status=CheckinRecord.STATUS_MISSED
        ).count()
        
        # 表情统计
        emotion_stats = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        ).values('emotion').annotate(count=Count('id'))
        
        emotion_distribution = {stat['emotion']: stat['count'] for stat in emotion_stats}
        
        # 打卡率
        expected_checkins = days  # 简化计算，假设每天一次
        checkin_rate = (total_checkins / expected_checkins * 100) if expected_checkins > 0 else 0
        
        return Response({
            'period_days': days,
            'total_checkins': total_checkins,
            'on_time_count': on_time_count,
            'late_count': late_count,
            'missed_count': missed_count,
            'checkin_rate': round(checkin_rate, 2),
            'emotion_distribution': emotion_distribution
        })