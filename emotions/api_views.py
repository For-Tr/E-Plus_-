"""
表情分析REST API视图（给鸿蒙App使用）
"""
import os
import base64
import cv2
import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from emotions.models import EmotionRecord
from emotions.services import emotion_recognition_service


class AnalyzeEmotionAPIView(APIView):
    """分析表情API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # 获取上传的照片
        if 'image' not in request.FILES and 'image' not in request.data:
            return Response({
                'error': '请上传照片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 读取图片
            if 'image' in request.FILES:
                image = request.FILES['image']
                img_bytes = image.read()
            else:
                # base64格式
                img_data = request.data['image']
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
            
            # 转换为OpenCV格式
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return Response({
                    'error': '无效的图片格式'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 表情识别
            result = emotion_recognition_service.detect_emotion(gray)
            
            # 可选：保存照片
            save_photo = request.data.get('save_photo', False)
            photo_path = None
            
            if save_photo:
                photo_dir = os.path.join('media', 'emotion_photos', user.username)
                os.makedirs(photo_dir, exist_ok=True)
                photo_filename = f'emotion_{timezone.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                photo_path = os.path.join(photo_dir, photo_filename)
                cv2.imwrite(photo_path, img)
                
                # 保存表情记录
                EmotionRecord.objects.create(
                    user=user,
                    family=user.family,
                    emotion=result['emotion'],
                    confidence=result['confidence'],
                    all_probabilities=result['probabilities'],
                    photo_path=photo_path,
                    ai_analysis=result
                )
            
            return Response({
                'emotion': result['emotion'],
                'emotion_cn': result['emotion_cn'],
                'confidence': result['confidence'],
                'probabilities': result['probabilities'],
                'ai_analysis': result['ai_analysis'],
                'saved': save_photo
            })
            
        except Exception as e:
            return Response({
                'error': f'表情分析失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmotionRecordsAPIView(APIView):
    """获取表情记录"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 获取查询参数
        days = int(request.query_params.get('days', 7))
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 构建查询
        since_date = timezone.now() - timedelta(days=days)
        queryset = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        ).order_by('-recorded_at')
        
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
                'emotion': record.emotion,
                'emotion_display': record.get_emotion_display(),
                'confidence': record.confidence,
                'probabilities': record.all_probabilities,
                'photo_path': record.photo_path,
                'face_match': record.face_encoding_match,
                'ai_analysis': record.ai_analysis,
                'recorded_at': record.recorded_at,
                'emotion_score': record.emotion_score,
                'is_negative': record.is_negative,
                'checkin_record': {
                    'id': record.checkin_record.id,
                    'task_name': record.checkin_record.task.task_name
                } if record.checkin_record else None
            })
        
        return Response({
            'records': result,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        })


class EmotionStatisticsAPIView(APIView):
    """表情统计"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        since_date = timezone.now() - timedelta(days=days)
        
        # 总记录数
        total_records = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        ).count()
        
        # 表情分布
        emotion_distribution = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        ).values('emotion').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence')
        ).order_by('-count')
        
        # 转换为字典
        emotion_stats = {}
        for stat in emotion_distribution:
            emotion_stats[stat['emotion']] = {
                'count': stat['count'],
                'avg_confidence': round(stat['avg_confidence'], 4),
                'percentage': round(stat['count'] / total_records * 100, 2) if total_records > 0 else 0
            }
        
        # 负面情绪统计
        negative_count = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date,
            emotion__in=['angry', 'disgust', 'sad', 'fear']
        ).count()
        
        # 计算平均情绪评分
        records = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        )
        
        avg_score = 0
        if records.exists():
            total_score = sum(record.emotion_score for record in records)
            avg_score = round(total_score / total_records, 2)
        
        # 最近7天的每日统计
        daily_stats = []
        for i in range(min(days, 7)):
            date = timezone.now().date() - timedelta(days=i)
            day_records = EmotionRecord.objects.filter(
                user=user,
                recorded_at__date=date
            )
            
            day_count = day_records.count()
            if day_count > 0:
                day_score = sum(record.emotion_score for record in day_records) / day_count
                dominant_emotion = day_records.values('emotion').annotate(
                    count=Count('id')
                ).order_by('-count').first()
                
                daily_stats.append({
                    'date': date.isoformat(),
                    'count': day_count,
                    'avg_score': round(day_score, 2),
                    'dominant_emotion': dominant_emotion['emotion'] if dominant_emotion else None
                })
        
        return Response({
            'period_days': days,
            'total_records': total_records,
            'emotion_distribution': emotion_stats,
            'negative_count': negative_count,
            'negative_percentage': round(negative_count / total_records * 100, 2) if total_records > 0 else 0,
            'avg_emotion_score': avg_score,
            'daily_stats': list(reversed(daily_stats))  # 按时间正序
        })


class EmotionTrendsAPIView(APIView):
    """情绪趋势分析"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        # 获取每天的情绪数据
        trends = []
        for i in range(days):
            date = timezone.now().date() - timedelta(days=days-1-i)
            
            # 当天的记录
            day_records = EmotionRecord.objects.filter(
                user=user,
                recorded_at__date=date
            )
            
            if day_records.exists():
                # 计算当天的情绪评分
                day_score = sum(record.emotion_score for record in day_records) / day_records.count()
                
                # 主要表情
                dominant = day_records.values('emotion').annotate(
                    count=Count('id')
                ).order_by('-count').first()
                
                # 负面情绪占比
                negative_count = day_records.filter(
                    emotion__in=['angry', 'disgust', 'sad', 'fear']
                ).count()
                negative_ratio = negative_count / day_records.count()
                
                trends.append({
                    'date': date.isoformat(),
                    'emotion_score': round(day_score, 2),
                    'record_count': day_records.count(),
                    'dominant_emotion': dominant['emotion'],
                    'negative_ratio': round(negative_ratio, 2)
                })
            else:
                trends.append({
                    'date': date.isoformat(),
                    'emotion_score': None,
                    'record_count': 0,
                    'dominant_emotion': None,
                    'negative_ratio': None
                })
        
        # 计算趋势方向
        recent_7days = [t for t in trends[-7:] if t['emotion_score'] is not None]
        older_7days = [t for t in trends[-14:-7] if t['emotion_score'] is not None]
        
        trend_direction = 'stable'
        if len(recent_7days) >= 3 and len(older_7days) >= 3:
            recent_avg = sum(t['emotion_score'] for t in recent_7days) / len(recent_7days)
            older_avg = sum(t['emotion_score'] for t in older_7days) / len(older_7days)
            
            if recent_avg > older_avg + 5:
                trend_direction = 'improving'
            elif recent_avg < older_avg - 5:
                trend_direction = 'declining'
        
        return Response({
            'period_days': days,
            'trends': trends,
            'trend_direction': trend_direction
        })