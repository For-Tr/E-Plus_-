"""
家庭相关模型
"""
import secrets
import string
from django.db import models
from django.utils import timezone
from django.conf import settings


def generate_family_code():
    """生成6位家庭邀请码"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class Family(models.Model):
    """家庭模型"""
    
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, '正常'),
        (STATUS_INACTIVE, '停用'),
    ]
    
    family_name = models.CharField('家庭名称', max_length=100)
    family_code = models.CharField(
        '家庭邀请码',
        max_length=20,
        unique=True,
        default=generate_family_code,
        db_index=True
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='managed_families',
        verbose_name='家庭管理员'
    )
    max_members = models.IntegerField('最大成员数', default=20)
    description = models.TextField('家庭描述', blank=True)
    settings_json = models.JSONField('家庭设置', default=dict, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'families'
        verbose_name = '家庭'
        verbose_name_plural = '家庭'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.family_name} ({self.family_code})"
    
    @property
    def member_count(self):
        """成员数量"""
        return self.members.filter(status='active').count()
    
    def can_add_member(self):
        """是否可以添加成员"""
        return self.member_count < self.max_members


class InviteCode(models.Model):
    """邀请码模型"""
    
    STATUS_ACTIVE = 'active'
    STATUS_USED = 'used'
    STATUS_EXPIRED = 'expired'
    STATUS_REVOKED = 'revoked'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, '有效'),
        (STATUS_USED, '已使用'),
        (STATUS_EXPIRED, '已过期'),
        (STATUS_REVOKED, '已撤销'),
    ]
    
    code = models.CharField('邀请码', max_length=20, unique=True, db_index=True)
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='invite_codes',
        verbose_name='所属家庭'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_invites',
        verbose_name='创建者'
    )
    username_for = models.CharField('指定用户名', max_length=50)
    display_name_for = models.CharField('指定显示名称', max_length=100, blank=True)
    max_uses = models.IntegerField('最大使用次数', default=1)
    used_count = models.IntegerField('已使用次数', default=0)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'invite_codes'
        verbose_name = '邀请码'
        verbose_name_plural = '邀请码'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['family', 'status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.username_for}"
    
    def is_valid(self):
        """检查邀请码是否有效"""
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.used_count >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            self.status = self.STATUS_EXPIRED
            self.save()
            return False
        return True
    
    def use(self):
        """使用邀请码"""
        self.used_count += 1
        if self.used_count >= self.max_uses:
            self.status = self.STATUS_USED
        self.save()