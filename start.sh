#!/bin/bash

# 家庭情绪管理系统 - 启动脚本

echo "======================================"
echo "  家庭情绪管理系统启动脚本"
echo "======================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[错误] 未找到虚拟环境,请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "[1/6] 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "[2/6] 检查依赖..."
pip list | grep -q Django || {
    echo "[提示] 正在安装依赖..."
    pip install -r requirements.txt
}

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "[3/6] 创建.env文件..."
    cp .env.example .env
    echo "[提示] 请编辑.env文件配置必要参数"
fi

# 执行数据库迁移
echo "[4/6] 执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员(如果不存在)
echo "[5/6] 检查超级管理员..."
python manage.py shell -c "
from users.models import User
if not User.objects.filter(role='super_admin').exists():
    print('[提示] 首次运行,请创建超级管理员账户')
    import sys
    sys.exit(1)
" 2>/dev/null || {
    echo "[提示] 即将创建超级管理员账户..."
    python manage.py createsuperuser
}

# 启动服务
echo "[6/6] 启动Django服务..."
echo ""
echo "======================================"
echo "  服务启动成功!"
echo "  Web管理端: http://localhost:8000"
echo "  管理后台: http://localhost:8000/admin"
echo "  API接口: http://localhost:8000/api/v1/"
echo "======================================"
echo ""

python manage.py runserver 0.0.0.0:8000