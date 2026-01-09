"""
用户模型
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, username, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名不能为空')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        """创建超级管理员"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.SUPER_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置is_superuser=True')
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    支持三种角色: 超级管理员、家庭管理员、家庭成员
    """
    
    # 角色选择
    SUPER_ADMIN = 'super_admin'
    FAMILY_ADMIN = 'family_admin'
    FAMILY_MEMBER = 'family_member'
    
    ROLE_CHOICES = [
        (SUPER_ADMIN, '超级管理员'),
        (FAMILY_ADMIN, '家庭管理员'),
        (FAMILY_MEMBER, '家庭成员'),
    ]
    
    # 账户状态
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    
    STATUS_CHOICES = [
        (ACTIVE, '正常'),
        (INACTIVE, '未激活'),
        (SUSPENDED, '已停用'),
    ]
    
    # 基本信息
    username = models.CharField('用户名', max_length=50, unique=True, db_index=True)
    display_name = models.CharField('显示名称', max_length=100, blank=True)
    email = models.EmailField('邮箱', max_length=100, blank=True, null=True)
    phone = models.CharField('手机号', max_length=20, blank=True, null=True)
    
    # 角色与家庭
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default=FAMILY_MEMBER)
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='所属家庭'
    )
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_users',
        verbose_name='邀请人'
    )
    
    # 人脸识别
    face_registered = models.BooleanField('已注册人脸', default=False)
    face_encodings_count = models.IntegerField('人脸照片数量', default=0)
    
    # 账户状态
    status = models.CharField('账户状态', max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    is_active = models.BooleanField('账户激活', default=True)
    is_staff = models.BooleanField('管理员权限', default=False)
    
    # 时间戳
    date_joined = models.DateTimeField('注册时间', default=timezone.now)
    last_login = models.DateTimeField('最后登录', null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['family']),
        ]
    
    def __str__(self):
        return f"{self.display_name or self.username} ({self.get_role_display()})"
    
    @property
    def is_super_admin(self):
        """是否为超级管理员"""
        return self.role == self.SUPER_ADMIN
    
    @property
    def is_family_admin(self):
        """是否为家庭管理员"""
        return self.role == self.FAMILY_ADMIN
    
    @property
    def is_family_member(self):
        """是否为家庭成员"""
        return self.role == self.FAMILY_MEMBER
    
    def can_manage_family(self, family):
        """是否可以管理指定家庭"""
        if self.is_super_admin:
            return True
        if self.is_family_admin and self.family_id == family.id:
            return True
        return False