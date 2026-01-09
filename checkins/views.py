"""
打卡管理Web视图(Django模板)
"""
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count

from checkins.models import CheckinTask, CheckinRecord
from users.models import User


@login_required
def task_list(request):
    """任务列表"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    # 获取任务列表
    if user.is_family_admin:
        tasks = CheckinTask.objects.filter(family=user.family).order_by('-created_at')
    else:
        # 普通成员只能看到与自己相关的任务
        tasks = CheckinTask.objects.filter(
            family=user.family,
            is_active=True
        ).order_by('-created_at')
    
    # 添加统计信息
    for task in tasks:
        task.total_records = CheckinRecord.objects.filter(task=task).count()
        task.today_records = CheckinRecord.objects.filter(
            task=task,
            checkin_time__date=timezone.now().date()
        ).count()
    
    context = {
        'tasks': tasks,
        'family': user.family,
        'can_manage': user.is_family_admin,
    }
    
    return render(request, 'checkins/task_list.html', context)


@login_required
def create_task(request):
    """创建任务"""
    user = request.user
    
    if not user.is_family_admin:
        messages.error(request, '只有家庭管理员才能创建任务')
        return redirect('checkins:task_list')
    
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        task_type = request.POST.get('task_type')
        target_members = request.POST.getlist('target_members')
        
        if not task_name:
            messages.error(request, '任务名称不能为空')
        else:
            # 创建任务
            task = CheckinTask.objects.create(
                task_name=task_name,
                family=user.family,
                task_type=task_type,
                target_members=[int(m) for m in target_members] if target_members else [],
                created_by=user,
                schedule_config={'time': request.POST.get('schedule_time', '09:00')},
                reminder_config={'enabled': True},
            )
            
            messages.success(request, f'任务"{task_name}"创建成功!')
            return redirect('checkins:task_detail', task_id=task.id)
    
    # 获取家庭成员列表
    members = User.objects.filter(
        family=user.family,
        status='active',
        role='family_member'
    )
    
    context = {
        'members': members,
        'family': user.family,
    }
    
    return render(request, 'checkins/create_task.html', context)


@login_required
def task_detail(request, task_id):
    """任务详情"""
    user = request.user
    
    task = get_object_or_404(CheckinTask, id=task_id, family=user.family)
    
    # 获取打卡记录
    records = CheckinRecord.objects.filter(
        task=task
    ).select_related('user').order_by('-checkin_time')[:50]
    
    # 统计数据
    total_records = CheckinRecord.objects.filter(task=task).count()
    on_time_records = CheckinRecord.objects.filter(
        task=task,
        status=CheckinRecord.STATUS_ON_TIME
    ).count()
    
    context = {
        'task': task,
        'records': records,
        'total_records': total_records,
        'on_time_records': on_time_records,
        'can_manage': user.is_family_admin,
    }
    
    return render(request, 'checkins/task_detail.html', context)


@login_required
def edit_task(request, task_id):
    """编辑任务"""
    user = request.user
    
    if not user.is_family_admin:
        messages.error(request, '只有家庭管理员才能编辑任务')
        return redirect('checkins:task_list')
    
    task = get_object_or_404(CheckinTask, id=task_id, family=user.family)
    
    if request.method == 'POST':
        task.task_name = request.POST.get('task_name')
        task.task_type = request.POST.get('task_type')
        task.is_active = request.POST.get('is_active') == 'on'
        
        target_members = request.POST.getlist('target_members')
        task.target_members = [int(m) for m in target_members] if target_members else []
        
        task.save()
        
        messages.success(request, '任务更新成功!')
        return redirect('checkins:task_detail', task_id=task.id)
    
    # 获取家庭成员列表
    members = User.objects.filter(
        family=user.family,
        status='active',
        role='family_member'
    )
    
    context = {
        'task': task,
        'members': members,
        'family': user.family,
    }
    
    return render(request, 'checkins/edit_task.html', context)


@login_required
def record_list(request):
    """打卡记录列表"""
    user = request.user
    
    if not user.family:
        messages.warning(request, '您还没有加入任何家庭')
        return redirect('users:index')
    
    # 获取打卡记录
    if user.is_family_admin:
        records = CheckinRecord.objects.filter(family=user.family)
    else:
        records = CheckinRecord.objects.filter(user=user)
    
    records = records.select_related('user', 'task').order_by('-checkin_time')[:100]
    
    context = {
        'records': records,
        'family': user.family,
    }
    
    return render(request, 'checkins/record_list.html', context)


@login_required
def record_detail(request, record_id):
    """打卡记录详情"""
    user = request.user
    
    if user.is_family_admin:
        record = get_object_or_404(CheckinRecord, id=record_id, family=user.family)
    else:
        record = get_object_or_404(CheckinRecord, id=record_id, user=user)
    
    context = {
        'record': record,
    }
    
    return render(request, 'checkins/record_detail.html', context)