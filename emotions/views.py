"""
表情记录Web视图(Django模板)
"""
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from collections import defaultdict

from emotions.models import EmotionRecord
from users.models import User


@login_required
def record_list(request):
    """表情记录列表"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    # 获取情绪记录
    if user.is_family_admin:
        records = EmotionRecord.objects.filter(family=user.family)
    else:
        records = EmotionRecord.objects.filter(user=user)
    
    # 筛选条件
    emotion_filter = request.GET.get('emotion')
    member_filter = request.GET.get('member')
    days_filter = request.GET.get('days', '7')
    
    try:
        days = int(days_filter)
        since_date = timezone.now() - timedelta(days=days)
        records = records.filter(recorded_at__gte=since_date)
    except ValueError:
        pass
    
    if emotion_filter:
        records = records.filter(emotion=emotion_filter)
    
    if member_filter and user.is_family_admin:
        records = records.filter(user_id=member_filter)
    
    records = records.select_related('user').order_by('-recorded_at')[:100]
    
    # 获取成员列表(用于筛选)
    members = []
    if user.is_family_admin:
        members = User.objects.filter(
            family=user.family,
            status='active'
        )
    
    context = {
        'records': records,
        'members': members,
        'can_view_all': user.is_family_admin,
        'emotion_filter': emotion_filter,
        'member_filter': member_filter,
        'days_filter': days_filter,
    }
    
    return render(request, 'emotions/record_list.html', context)


@login_required
def record_detail(request, record_id):
    """表情记录详情"""
    user = request.user
    
    if user.is_family_admin:
        record = get_object_or_404(EmotionRecord, id=record_id, family=user.family)
    else:
        record = get_object_or_404(EmotionRecord, id=record_id, user=user)
    
    context = {
        'record': record,
    }
    
    return render(request, 'emotions/record_detail.html', context)


@login_required
def statistics(request):
    """表情统计"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    # 时间范围
    days = int(request.GET.get('days', '30'))
    since_date = timezone.now() - timedelta(days=days)
    
    # 获取情绪记录
    if user.is_family_admin:
        records = EmotionRecord.objects.filter(
            family=user.family,
            recorded_at__gte=since_date
        )
    else:
        records = EmotionRecord.objects.filter(
            user=user,
            recorded_at__gte=since_date
        )
    
    # 情绪统计
    emotion_counts = records.values('emotion').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 每日情绪统计
    daily_stats = defaultdict(lambda: defaultdict(int))
    for record in records:
        date_key = record.recorded_at.date().isoformat()
        daily_stats[date_key][record.emotion] += 1
    
    # 转换为图表数据
    daily_data = []
    for date_str in sorted(daily_stats.keys()):
        daily_data.append({
            'date': date_str,
            'data': dict(daily_stats[date_str])
        })
    
    # 成员情绪统计(仅管理员)
    member_stats = []
    if user.is_family_admin:
        members = User.objects.filter(
            family=user.family,
            status='active'
        )
        for member in members:
            member_records = records.filter(user=member)
            total = member_records.count()
            if total > 0:
                emotions = member_records.values('emotion').annotate(
                    count=Count('id')
                ).order_by('-count')
                member_stats.append({
                    'member': member,
                    'total': total,
                    'emotions': emotions,
                })
    
    context = {
        'emotion_counts': emotion_counts,
        'daily_data': daily_data,
        'member_stats': member_stats,
        'days': days,
        'can_view_all': user.is_family_admin,
    }
    
    return render(request, 'emotions/statistics.html', context)


@login_required
def trends(request):
    """情绪趋势"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    # 时间范围
    days = int(request.GET.get('days', '30'))
    member_id = request.GET.get('member')
    
    # 检查权限
    if member_id:
        if not user.is_family_admin and user.id != int(member_id):
            messages.error(request, '您没有权限查看此成员的数据')
            return redirect('emotions:statistics')
        member = get_object_or_404(User, id=member_id, family=user.family)
    else:
        member = user
    
    since_date = timezone.now() - timedelta(days=days)
    
    # 获取情绪记录
    records = EmotionRecord.objects.filter(
        user=member,
        recorded_at__gte=since_date
    ).order_by('recorded_at')
    
    # 每日情绪趋势
    daily_emotions = defaultdict(list)
    for record in records:
        date_key = record.recorded_at.date().isoformat()
        daily_emotions[date_key].append(record.emotion)
    
    # 计算每日主导情绪和情绪分布
    daily_trend = []
    for date_str in sorted(daily_emotions.keys()):
        emotions = daily_emotions[date_str]
        emotion_count = defaultdict(int)
        for emotion in emotions:
            emotion_count[emotion] += 1
        dominant_emotion = max(emotion_count.items(), key=lambda x: x[1]) if emotion_count else ('neutral', 0)
        daily_trend.append({
            'date': date_str,
            'emotion': dominant_emotion[0],
            'count': len(emotions),
            'distribution': dict(emotion_count)
        })
    
    # 异常情绪检测
    negative_emotions = ['angry', 'sad', 'fear', 'disgust']
    negative_count = records.filter(emotion__in=negative_emotions).count()
    total_count = records.count()
    negative_rate = round(negative_count / total_count * 100, 1) if total_count > 0 else 0
    
    # 获取成员列表(用于筛选)
    members = []
    if user.is_family_admin:
        members = User.objects.filter(
            family=user.family,
            status='active'
        )
    
    context = {
        'member': member,
        'daily_trend': daily_trend,
        'days': days,
        'total_count': total_count,
        'negative_count': negative_count,
        'negative_rate': negative_rate,
        'is_alert': negative_rate > 50,
        'members': members,
        'can_view_all': user.is_family_admin,
    }
    
    return render(request, 'emotions/trends.html', context)