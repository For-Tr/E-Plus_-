# 快速启动指南

## 5分钟快速上手

### 1. 进入项目目录

```bash
cd /Users/xiangbingzhou/nan/family-emotion-system
```

### 2. 激活虚拟环境

```bash
source venv/bin/activate
```

### 3. 安装依赖(如果尚未安装)

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑.env文件(可选,开发环境可直接使用默认值)
# vim .env
```

### 5. 初始化数据库

```bash
# 创建数据库迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
# 按提示输入: 用户名、密码
```

### 6. 启动服务

```bash
# 方式1: 使用启动脚本(推荐)
./start.sh

# 方式2: 手动启动
python manage.py runserver 0.0.0.0:8000
```

### 7. 访问系统

打开浏览器访问:

- **Web首页**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin
- **API文档**: http://localhost:8000/api/v1/

---

## 常见问题

### Q1: 虚拟环境已存在但依赖未安装

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q2: 数据库迁移失败

```bash
# 删除旧的迁移文件和数据库
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
rm db.sqlite3

# 重新创建
python manage.py makemigrations
python manage.py migrate
```

### Q3: AI模型文件缺失

```bash
# 从旧项目复制
cp /path/to/old/project/mobilefacenet.tflite ml_models/
cp /path/to/old/project/fer.weights.h5 ml_models/
```

### Q4: 端口被占用

```bash
# 使用其他端口
python manage.py runserver 0.0.0.0:8080
```

---

## 下一步

### 创建测试数据

```python
# 进入Django Shell
python manage.py shell

# 创建家庭
from families.models import Family
from users.models import User

admin = User.objects.get(username='admin')
family = Family.objects.create(
    family_name='测试家庭',
    admin=admin,
    description='这是一个测试家庭'
)
print(f'家庭邀请码: {family.family_code}')
```

### 开发API

参考 `PROJECT_SUMMARY.md` 的"下一步工作建议"章节

### 部署到生产环境

参考 `README.md` 的"部署"章节

---

祝您使用愉快! 🎉