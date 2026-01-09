"""
表情记录模型
"""
from django.db import models
from django.utils import timezone
from django.conf import settings


class EmotionRecord(models.Model):
    """表情记录模型"""
    
    # 7种表情
    EMOTION_ANGRY = 'angry'
    EMOTION_DISGUST = 'disgust'
    EMOTION_FEAR = 'fear'
    EMOTION_HAPPY = 'happy'
    EMOTION_SAD = 'sad'
    EMOTION_SURPRISE = 'surprise'
    EMOTION_NEUTRAL = 'neutral'
    
    EMOTION_CHOICES = [
        (EMOTION_ANGRY, '愤怒'),
        (EMOTION_DISGUST, '厌恶'),
        (EMOTION_FEAR, '恐惧'),
        (EMOTION_HAPPY, '快乐'),
        (EMOTION_SAD, '悲伤'),
        (EMOTION_SURPRISE, '惊讶'),
        (EMOTION_NEUTRAL, '中性'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emotion_records',
        verbose_name='用户'
    )
    family = models.ForeignKey(
        'families.Family',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='emotion_records',
        verbose_name='家庭'
    )
    checkin_record = models.ForeignKey(
        'checkins.CheckinRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emotion_records',
        verbose_name='关联打卡记录'
    )
    
    emotion = models.CharField('主要表情', max_length=50, choices=EMOTION_CHOICES)
    confidence = models.FloatField('置信度')
    all_probabilities = models.JSONField('所有表情概率', default=dict)
    photo_path = models.CharField('照片路径', max_length=255, blank=True)
    face_encoding_match = models.BooleanField('人脸匹配', default=False)
    ai_analysis = models.JSONField('AI分析', default=dict)
    context_info = models.JSONField('上下文信息', default=dict)
    
    recorded_at = models.DateTimeField('记录时间', default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'emotion_records'
        verbose_name = '表情记录'
        verbose_name_plural = '表情记录'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'recorded_at']),
            models.Index(fields=['family', 'recorded_at']),
            models.Index(fields=['emotion']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.get_emotion_display()} ({self.confidence:.2f})"
    
    @property
    def emotion_score(self):
        """情绪评分(0-100)"""
        scores = {
            self.EMOTION_HAPPY: 90,
            self.EMOTION_SURPRISE: 85,
            self.EMOTION_NEUTRAL: 65,
            self.EMOTION_SAD: 40,
            self.EMOTION_FEAR: 35,
            self.EMOTION_ANGRY: 20,
            self.EMOTION_DISGUST: 15,
        }
        return scores.get(self.emotion, 50)
    
    @property
    def is_negative(self):
        """是否为负面情绪"""
        return self.emotion in [self.EMOTION_ANGRY, self.EMOTION_DISGUST, self.EMOTION_SAD, self.EMOTION_FEAR]


class FaceEncoding(models.Model):
    """人脸特征编码模型"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='face_encodings',
        verbose_name='用户'
    )
    encoding_vector = models.BinaryField('特征向量')
    encoding_json = models.JSONField('特征向量JSON', default=dict, blank=True)
    photo_path = models.CharField('照片路径', max_length=255)
    quality_score = models.FloatField('质量评分', null=True, blank=True)
    is_primary = models.BooleanField('主要特征', default=False)
    
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    
    class Meta:
        db_table = 'face_encodings'
        verbose_name = '人脸特征'
        verbose_name_plural = '人脸特征'
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {'主要' if self.is_primary else '备用'}特征"