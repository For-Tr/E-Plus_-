# 家庭情绪管理系统 - 部署指南

## 目录
- [快速开始](#快速开始)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [常见问题](#常见问题)

---

## 快速开始

### 前置要求
- Python 3.11+ (推荐3.11或3.12)
- Redis (用于Celery)
- Git

### 一键部署(推荐)

```bash
# 克隆项目
git clone <repository-url>
cd family-emotion-system

# 运行部署脚本
./deploy.sh

# 按提示操作,脚本会自动:
# 1. 创建虚拟环境
# 2. 安装依赖
# 3. 配置环境变量
# 4. 执行数据库迁移
# 5. 收集静态文件
```

---

## 开发环境部署

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install Django django-cors-headers djangorestframework djangorestframework-simplejwt python-dotenv celery django-celery-beat redis python-dateutil pytz

# 安装图像处理库(如需AI功能)
pip install opencv-python numpy pillow

# 可选: 安装TensorFlow(用于AI模型,较大)
# pip install tensorflow
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件,修改必要配置
nano .env
```

关键配置项:
```env
SECRET_KEY=生成一个随机密钥
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=你的邮箱
EMAIL_HOST_PASSWORD=你的邮箱密码
```

### 4. 数据库初始化

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 5. 启动服务

**启动Web服务**
```bash
python manage.py runserver 0.0.0.0:8000
```

**启动Celery Worker** (新终端)
```bash
celery -A config worker -l info
```

**启动Celery Beat** (新终端,用于定时任务)
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**访问应用**
- Web界面: http://localhost:8000
- Admin后台: http://localhost:8000/admin
- API文档: 见API_DOCUMENTATION.md

---

## 生产环境部署

### 1. 系统要求

- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.11+
- Redis
- Nginx (可选,推荐)
- Supervisor/Systemd (进程管理)

### 2. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip redis-server nginx supervisor
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install python311 python311-pip redis nginx supervisor
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. 部署应用

```bash
# 创建部署目录
sudo mkdir -p /opt/family-emotion-system
cd /opt/family-emotion-system

# 克隆代码
git clone <repository-url> .

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境变量
cp .env.example .env
nano .env
```

**生产环境.env配置:**
```env
SECRET_KEY=<生成的随机密钥>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip-address
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. 数据库和静态文件

```bash
# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户
python manage.py createsuperuser
```

### 5. 配置Gunicorn服务

使用Systemd管理Gunicorn:

```bash
sudo nano /etc/systemd/system/family-emotion-web.service
```

内容:
```ini
[Unit]
Description=Family Emotion System Web Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/family-emotion-system
Environment="PATH=/opt/family-emotion-system/venv/bin"
ExecStart=/opt/family-emotion-system/venv/bin/gunicorn config.wsgi:application --config /opt/family-emotion-system/gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl start family-emotion-web
sudo systemctl enable family-emotion-web
sudo systemctl status family-emotion-web
```

### 6. 配置Celery服务

**Celery Worker:**
```bash
sudo nano /etc/systemd/system/family-emotion-celery.service
```

```ini
[Unit]
Description=Family Emotion Celery Worker
After=network.target redis.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/family-emotion-system
Environment="PATH=/opt/family-emotion-system/venv/bin"
ExecStart=/opt/family-emotion-system/venv/bin/celery -A config worker -l info --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Beat:**
```bash
sudo nano /etc/systemd/system/family-emotion-celery-beat.service
```

```ini
[Unit]
Description=Family Emotion Celery Beat
After=network.target redis.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/family-emotion-system
Environment="PATH=/opt/family-emotion-system/venv/bin"
ExecStart=/opt/family-emotion-system/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl start family-emotion-celery
sudo systemctl start family-emotion-celery-beat
sudo systemctl enable family-emotion-celery
sudo systemctl enable family-emotion-celery-beat
```

### 7. 配置Nginx

```bash
sudo nano /etc/nginx/sites-available/family-emotion
```

复制nginx.conf内容,修改域名和路径,然后:

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/family-emotion /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 8. 配置SSL证书(推荐)

使用Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker部署

### 前置要求
- Docker
- Docker Compose

### 快速启动

```bash
# 克隆项目
git clone <repository-url>
cd family-emotion-system

# 配置环境变量
cp .env.example .env
nano .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 初始化

```bash
# 进入容器
docker-compose exec web bash

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 退出容器
exit
```

### 服务说明

Docker Compose会启动以下服务:
- **web**: Django Web应用 (端口8000)
- **redis**: Redis缓存和消息队列
- **celery-worker**: Celery任务处理器
- **celery-beat**: Celery定时任务调度器

---

## 常见问题

### 1. ModuleNotFoundError: No module named 'cv2'

```bash
pip install opencv-python
```

### 2. TensorFlow警告

如果不需要AI功能,可以忽略TensorFlow相关警告。如需使用:
```bash
pip install tensorflow
```

### 3. Redis连接失败

确保Redis正在运行:
```bash
# 检查状态
redis-cli ping
# 应返回: PONG

# 启动Redis
sudo systemctl start redis
```

### 4. 静态文件404

```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 检查STATIC_ROOT配置
```

### 5. 邮件发送失败

检查.env中的邮件配置:
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD (使用应用专用密码,不是账户密码)
- EMAIL_PORT和EMAIL_USE_TLS

Gmail用户需要:
1. 开启"两步验证"
2. 生成"应用专用密码"

### 6. 数据库迁移冲突

```bash
# 删除所有迁移文件(谨慎!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 重新生成迁移
python manage.py makemigrations
python manage.py migrate
```

### 7. 权限问题

```bash
# 给媒体目录适当权限
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/
```

---

## 维护命令

### 备份数据库

```bash
# SQLite备份
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### 查看日志

```bash
# Django日志
tail -f /var/log/nginx/family-emotion-error.log

# Celery日志
journalctl -u family-emotion-celery -f

# Systemd服务日志
sudo journalctl -u family-emotion-web -f
```

### 更新代码

```bash
cd /opt/family-emotion-system
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart family-emotion-web
sudo systemctl restart family-emotion-celery
```

---

## 性能优化建议

1. **使用PostgreSQL替代SQLite**(生产环境)
2. **配置Redis持久化**
3. **启用Nginx缓存**
4. **配置CDN加速静态文件**
5. **定期清理旧日志和通知**
6. **监控服务器资源使用**

---

**祝部署顺利! 如有问题,请查看项目文档或提交Issue。**