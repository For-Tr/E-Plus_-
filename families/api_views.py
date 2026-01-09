"""
家庭管理REST API视图
"""
import secrets
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from families.models import Family, InviteCode
from users.models import User
from checkins.models import CheckinRecord
from emotions.models import EmotionRecord


class GenerateInviteCodeAPIView(APIView):
    """生成邀请码API（仅家庭管理员）"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # 权限检查
        if not user.is_family_admin:
            return Response({
                'error': '只有家庭管理员才能生成邀请码'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not user.family:
            return Response({
                'error': '您还没有管理的家庭'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取参数
        username = request.data.get('username')
        display_name = request.data.get('display_name', '')
        expires_days = int(request.data.get('expires_days', 7))
        
        if not username:
            return Response({
                'error': '用户名不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已被使用
        if User.objects.filter(username=username).exists():
            return Response({
                'error': '该用户名已被使用'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已有该用户名的有效邀请码
        existing = InviteCode.objects.filter(
            family=user.family,
            username_for=username,
            status=InviteCode.STATUS_ACTIVE
        ).first()
        
        if existing:
            return Response({
                'error': '该用户名已有有效的邀请码',
                'existing_code': existing.code
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成邀请码
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # 确保唯一性
        while InviteCode.objects.filter(code=code).exists():
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # 创建邀请码
        invite = InviteCode.objects.create(
            code=code,
            family=user.family,
            created_by=user,
            username_for=username,
            display_name_for=display_name,
            expires_at=timezone.now() + timedelta(days=expires_days)
        )
        
        return Response({
            'message': '邀请码生成成功',
            'invite_code': {
                'code': invite.code,
                'username': invite.username_for,
                'display_name': invite.display_name_for,
                'expires_at': invite.expires_at,
                'status': invite.status
            }
        }, status=status.HTTP_201_CREATED)


class InviteCodeListAPIView(APIView):
    """邀请码列表API（仅家庭管理员）"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 权限检查
        if not user.is_family_admin:
            return Response({
                'error': '只有家庭管理员才能查看邀请码列表'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not user.family:
            return Response({
                'error': '您还没有管理的家庭'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取邀请码列表
        invites = InviteCode.objects.filter(
            family=user.family
        ).order_by('-created_at')
        
        result = []
        for invite in invites:
            result.append({
                'id': invite.id,
                'code': invite.code,
                'username': invite.username_for,
                'display_name': invite.display_name_for,
                'status': invite.status,
                'status_display': invite.get_status_display(),
                'used_count': invite.used_count,
                'max_uses': invite.max_uses,
                'expires_at': invite.expires_at,
                'created_at': invite.created_at,
                'is_valid': invite.is_valid()
            })
        
        return Response({
            'invites': result,
            'total': len(result)
        })


class RevokeInviteCodeAPIView(APIView):
    """撤销邀请码API（仅家庭管理员）"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, code):
        user = request.user
        
        # 权限检查
        if not user.is_family_admin:
            return Response({
                'error': '只有家庭管理员才能撤销邀请码'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            invite = InviteCode.objects.get(code=code, family=user.family)
            invite.status = InviteCode.STATUS_REVOKED
            invite.save()
            
            return Response({
                'message': '邀请码已撤销'
            })
            
        except InviteCode.DoesNotExist:
            return Response({
                'error': '邀请码不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class FamilyMembersAPIView(APIView):
    """家庭成员列表API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.family:
            return Response({
                'members': [],
                'message': '您还没有加入任何家庭'
            })
        
        # 获取家庭成员
        members = User.objects.filter(
            family=user.family,
            status='active'
        ).order_by('-date_joined')
        
        result = []
        for member in members:
            # 获取成员统计
            total_checkins = CheckinRecord.objects.filter(user=member).count()
            recent_emotion = EmotionRecord.objects.filter(user=member).order_by('-recorded_at').first()
            
            result.append({
                'id': member.id,
                'username': member.username,
                'display_name': member.display_name,
                'role': member.role,
                'role_display': member.get_role_display(),
                'face_registered': member.face_registered,
                'last_login': member.last_login,
                'date_joined': member.date_joined,
                'stats': {
                    'total_checkins': total_checkins,
                    'recent_emotion': {
                        'emotion': recent_emotion.emotion,
                        'emotion_display': recent_emotion.get_emotion_display(),
                        'recorded_at': recent_emotion.recorded_at
                    } if recent_emotion else None
                }
            })
        
        return Response({
            'family': {
                'id': user.family.id,
                'name': user.family.family_name,
                'code': user.family.family_code,
                'admin': {
                    'id': user.family.admin.id,
                    'username': user.family.admin.username,
                    'display_name': user.family.admin.display_name
                }
            },
            'members': result,
            'total': len(result)
        })


class FamilyDetailAPIView(APIView):
    """家庭详情API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.family:
            return Response({
                'error': '您还没有加入任何家庭'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        family = user.family
        
        # 统计数据
        member_count = User.objects.filter(family=family, status='active').count()
        total_checkins = CheckinRecord.objects.filter(family=family).count()
        
        # 最近7天打卡统计
        since_date = timezone.now() - timedelta(days=7)
        recent_checkins = CheckinRecord.objects.filter(
            family=family,
            checkin_time__gte=since_date
        ).count()
        
        # 表情统计
        emotion_stats = EmotionRecord.objects.filter(
            family=family,
            recorded_at__gte=since_date
        ).values('emotion').annotate(count=Count('id'))
        
        emotion_distribution = {stat['emotion']: stat['count'] for stat in emotion_stats}
        
        return Response({
            'id': family.id,
            'name': family.family_name,
            'code': family.family_code,
            'description': family.description,
            'admin': {
                'id': family.admin.id,
                'username': family.admin.username,
                'display_name': family.admin.display_name
            },
            'stats': {
                'member_count': member_count,
                'max_members': family.max_members,
                'total_checkins': total_checkins,
                'recent_checkins_7days': recent_checkins,
                'emotion_distribution': emotion_distribution
            },
            'created_at': family.created_at
        })


class RemoveMemberAPIView(APIView):
    """移除家庭成员API（仅家庭管理员）"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, member_id):
        user = request.user
        
        # 权限检查
        if not user.is_family_admin:
            return Response({
                'error': '只有家庭管理员才能移除成员'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            member = User.objects.get(id=member_id, family=user.family)
            
            # 不能移除管理员自己
            if member.id == user.id:
                return Response({
                    'error': '不能移除自己'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 将成员从家庭中移除
            member.family = None
            member.status = 'inactive'
            member.save()
            
            return Response({
                'message': f'已将 {member.display_name} 移出家庭'
            })
            
        except User.DoesNotExist:
            return Response({
                'error': '成员不存在'
            }, status=status.HTTP_404_NOT_FOUND)