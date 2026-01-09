"""
用户Web视图(Django模板)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from families.models import InviteCode


def index(request):
    """首页"""
    if request.user.is_authenticated:
        # 根据用户角色跳转到不同页面
        if request.user.is_super_admin:
            return redirect('/admin/')
        elif request.user.is_family_admin:
            return redirect('families:dashboard')
        else:
            return redirect('checkins:task_list')
    return render(request, 'users/index.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            messages.success(request, f'欢迎回来, {user.display_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """登出"""
    logout(request)
    messages.success(request, '已成功登出')
    return redirect('users:login')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """注册家庭管理员"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        display_name = request.POST.get('display_name')
        email = request.POST.get('email')
        family_name = request.POST.get('family_name')
        
        # 验证密码
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'users/register.html')
        
        # 检查用户名是否已存在
        from users.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'users/register.html')
        
        # 创建家庭
        from families.models import Family
        family = Family.objects.create(
            family_name=family_name,
            admin=None  # 临时设置为None，稍后更新
        )
        
        # 创建家庭管理员用户
        user = User.objects.create_user(
            username=username,
            password=password,
            display_name=display_name or username,
            email=email,
            role=User.FAMILY_ADMIN,
            family=family,
            is_staff=False
        )
        
        # 更新家庭管理员
        family.admin = user
        family.save()
        
        # 自动登录
        login(request, user)
        messages.success(request, '注册成功！欢迎使用家庭情绪管理系统')
        return redirect('families:dashboard')
    
    return render(request, 'users/register.html')


@require_http_methods(["GET", "POST"])
def register_member_view(request):
    """家庭成员注册(通过邀请码)"""
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 验证邀请码
        try:
            invite = InviteCode.objects.get(code=invite_code)
            if not invite.is_valid():
                messages.error(request, '邀请码无效或已过期')
                return render(request, 'users/register_member.html')
        except InviteCode.DoesNotExist:
            messages.error(request, '邀请码不存在')
            return render(request, 'users/register_member.html')
        
        # 验证密码
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'users/register_member.html')
        
        # 创建用户
        from users.models import User
        user = User.objects.create_user(
            username=invite.username_for,
            password=password,
            display_name=invite.display_name_for or invite.username_for,
            role=User.FAMILY_MEMBER,
            family=invite.family,
            created_by=invite.created_by
        )
        
        # 使用邀请码
        invite.use()
        
        # 自动登录
        login(request, user)
        messages.success(request, '注册成功!请先注册您的人脸')
        return redirect('users:register_face')
    
    # GET请求，可能带有邀请码参数
    invite_code = request.GET.get('code', '')
    return render(request, 'users/register_member.html', {'invite_code': invite_code})


def accept_invite(request, code):
    """接受邀请"""
    try:
        invite = InviteCode.objects.get(code=code)
        if not invite.is_valid():
            messages.error(request, '邀请码无效或已过期')
            return redirect('users:index')
        return redirect(f'/register/member/?code={code}')
    except InviteCode.DoesNotExist:
        messages.error(request, '邀请码不存在')
        return redirect('users:index')


@login_required
def profile(request):
    """用户资料"""
    return render(request, 'users/profile.html')


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """编辑资料"""
    if request.method == 'POST':
        display_name = request.POST.get('display_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        user = request.user
        user.display_name = display_name
        user.email = email
        user.phone = phone
        user.save()
        
        messages.success(request, '资料更新成功')
        return redirect('users:profile')
    
    return render(request, 'users/edit_profile.html')


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        user = request.user
        
        if not user.check_password(old_password):
            messages.error(request, '原密码错误')
            return render(request, 'users/change_password.html')
        
        if new_password != new_password_confirm:
            messages.error(request, '两次输入的新密码不一致')
            return render(request, 'users/change_password.html')
        
        user.set_password(new_password)
        user.save()
        
        # 重新登录
        login(request, user)
        messages.success(request, '密码修改成功')
        return redirect('users:profile')
    
    return render(request, 'users/change_password.html')


@login_required
@require_http_methods(["GET", "POST"])
def register_face(request):
    """注册人脸"""
    if request.method == 'POST':
        # 这里通过AJAX处理，实际逻辑在前端JavaScript中
        pass
    
    return render(request, 'users/register_face.html')