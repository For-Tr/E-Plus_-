"""
家庭管理Web视图(Django模板)
"""
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from families.models import Family, InviteCode
from users.models import User
from checkins.models import CheckinRecord, CheckinTask
from emotions.models import EmotionRecord
import secrets
import string


@login_required
def dashboard(request):
    """家庭仪表板"""
    user = request.user
    
    # 检查是否有家庭
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    family = user.family
    
    # 统计数据
    member_count = User.objects.filter(family=family, status='active').count()
    
    # 最近7天打卡统计
    since_date = timezone.now() - timedelta(days=7)
    total_checkins = CheckinRecord.objects.filter(
        family=family,
        checkin_time__gte=since_date
    ).count()
    
    on_time_checkins = CheckinRecord.objects.filter(
        family=family,
        checkin_time__gte=since_date,
        status=CheckinRecord.STATUS_ON_TIME
    ).count()
    
    # 表情统计
    emotion_stats = EmotionRecord.objects.filter(
        family=family,
        recorded_at__gte=since_date
    ).values('emotion').annotate(count=Count('id')).order_by('-count')[:5]
    
    # 最近打卡记录
    recent_checkins = CheckinRecord.objects.filter(
        family=family
    ).select_related('user', 'task').order_by('-checkin_time')[:10]
    
    # 活跃任务数
    active_tasks = CheckinTask.objects.filter(family=family, is_active=True).count()
    
    context = {
        'family': family,
        'member_count': member_count,
        'total_checkins': total_checkins,
        'on_time_checkins': on_time_checkins,
        'checkin_rate': round(on_time_checkins / total_checkins * 100, 1) if total_checkins > 0 else 0,
        'emotion_stats': emotion_stats,
        'recent_checkins': recent_checkins,
        'active_tasks': active_tasks,
    }
    
    return render(request, 'families/dashboard.html', context)


@login_required
def invite_list(request):
    """邀请码列表"""
    user = request.user
    
    if not user.is_family_admin:
        messages.error(request, '只有家庭管理员才能管理邀请码')
        return redirect('families:dashboard')
    
    if not user.family:
        messages.warning(request, '您还没有管理的家庭')
        return redirect('users:index')
    
    invites = InviteCode.objects.filter(
        family=user.family
    ).order_by('-created_at')
    
    context = {
        'invites': invites,
        'family': user.family,
    }
    
    return render(request, 'families/invite_list.html', context)


@login_required
def generate_invite(request):
    """生成邀请码"""
    user = request.user
    
    if not user.is_family_admin:
        messages.error(request, '只有家庭管理员才能生成邀请码')
        return redirect('families:dashboard')
    
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '')
        expires_days = int(request.POST.get('expires_days', 7))
        
        if not display_name:
            messages.error(request, '家庭成员姓名不能为空')
        else:
            # 自动生成用户名(使用时间戳确保唯一)
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            username = f"user_{user.family.family_code}_{timestamp}"
            
            # 确保用户名唯一
            while User.objects.filter(username=username).exists():
                import random
                username = f"user_{user.family.family_code}_{timestamp}_{random.randint(1000, 9999)}"
            
            # 生成随机密码(16位,包含字母和数字)
            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            # 创建用户账号
            new_user = User.objects.create_user(
                username=username,
                password=random_password,
                display_name=display_name,
                role=User.FAMILY_MEMBER,
                family=user.family,
                created_by=user
            )
            
            # 生成邀请码
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            while InviteCode.objects.filter(code=code).exists():
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            invite = InviteCode.objects.create(
                code=code,
                family=user.family,
                created_by=user,
                username_for=username,
                display_name_for=display_name,
                expires_at=timezone.now() + timedelta(days=expires_days)
            )
            
            # 使用邀请码关联到新创建的用户
            invite.used_by = new_user
            invite.used_at = timezone.now()
            invite.save()
            
            messages.success(request, f'邀请码 {code} 生成成功! 家庭成员 {display_name} 的账号已自动创建。')
            return redirect('families:invite_list')
    
    return render(request, 'families/generate_invite.html', {'family': user.family})


@login_required
def member_list(request):
    """成员列表"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    members = User.objects.filter(
        family=user.family,
        status='active'
    ).order_by('-date_joined')
    
    # 为每个成员添加统计数据
    for member in members:
        member.total_checkins = CheckinRecord.objects.filter(user=member).count()
        recent_emotion = EmotionRecord.objects.filter(user=member).order_by('-recorded_at').first()
        member.recent_emotion = recent_emotion
    
    context = {
        'members': members,
        'family': user.family,
    }
    
    return render(request, 'families/member_list.html', context)


@login_required
def member_detail(request, member_id):
    """成员详情"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    member = get_object_or_404(User, id=member_id, family=user.family)
    
    # 最近30天的打卡记录
    since_date = timezone.now() - timedelta(days=30)
    checkin_records = CheckinRecord.objects.filter(
        user=member,
        checkin_time__gte=since_date
    ).select_related('task').order_by('-checkin_time')
    
    # 情绪记录
    emotion_records = EmotionRecord.objects.filter(
        user=member,
        recorded_at__gte=since_date
    ).order_by('-recorded_at')[:20]
    
    # 统计
    total_checkins = checkin_records.count()
    on_time_count = checkin_records.filter(status=CheckinRecord.STATUS_ON_TIME).count()
    
    context = {
        'member': member,
        'checkin_records': checkin_records,
        'emotion_records': emotion_records,
        'total_checkins': total_checkins,
        'on_time_count': on_time_count,
        'checkin_rate': round(on_time_count / total_checkins * 100, 1) if total_checkins > 0 else 0,
    }
    
    return render(request, 'families/member_detail.html', context)