"""
Celery配置
"""
import os
from celery import Celery
from celery.schedules import crontab

# 设置Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('family_emotion_system')

# 从Django settings中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有应用中的tasks
app.autodiscover_tasks()


# 配置定时任务
app.conf.beat_schedule = {
    # 每天早上8点发送打卡提醒
    'send-checkin-reminders-morning': {
        'task': 'checkins.tasks.send_checkin_reminders',
        'schedule': crontab(hour=8, minute=0),
        'args': (),
    },
    # 每天晚上8点发送打卡提醒
    'send-checkin-reminders-evening': {
        'task': 'checkins.tasks.send_checkin_reminders',
        'schedule': crontab(hour=20, minute=0),
        'args': (),
    },
    # 每天晚上10点检测未打卡
    'detect-missed-checkins': {
        'task': 'checkins.tasks.detect_missed_checkins',
        'schedule': crontab(hour=22, minute=0),
        'args': (),
    },
    # 每天晚上11点检测情绪异常
    'detect-emotion-anomalies': {
        'task': 'notifications.tasks.detect_emotion_anomalies',
        'schedule': crontab(hour=23, minute=0),
        'args': (),
    },
    # 每周一早上9点发送周报
    'send-weekly-report': {
        'task': 'notifications.tasks.send_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
        'args': (),
    },
}


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')