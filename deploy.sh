#!/bin/bash
# 部署脚本 - 用于快速部署家庭情绪管理系统

set -e  # 遇到错误立即退出

echo "========================================="
echo "家庭情绪管理系统 - 部署脚本"
echo "========================================="

# 检查Python版本
echo "检查Python版本..."
python --version || python3 --version

# 创建虚拟环境(如果不存在)
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip setuptools wheel

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在,从.env.example复制..."
    cp .env.example .env
    echo "请编辑.env文件配置必要的环境变量!"
fi

# 生成SECRET_KEY
if grep -q "your-secret-key-here" .env; then
    echo "生成新的SECRET_KEY..."
    NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-in-production/$NEW_SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-in-production/$NEW_SECRET_KEY/" .env
    fi
    echo "SECRET_KEY已生成并保存到.env"
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p media/faces_db media/emotion_photos media/uploads staticfiles

# 数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户(可选)
read -p "是否创建超级用户? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo "========================================="
echo "部署完成!"
echo "========================================="
echo ""
echo "启动开发服务器:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "启动Celery Worker:"
echo "  celery -A config worker -l info"
echo ""
echo "启动Celery Beat:"
echo "  celery -A config beat -l info"
echo ""
echo "生产环境启动(Gunicorn):"
echo "  gunicorn config.wsgi:application --config gunicorn_config.py"
echo ""
echo "Docker方式启动:"
echo "  docker-compose up -d"
echo ""