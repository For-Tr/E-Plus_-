"""
Gunicorn配置文件
用于生产环境部署
"""
import multiprocessing

# 监听地址和端口
bind = "0.0.0.0:8000"

# Worker进程数(建议CPU核心数*2+1)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker类型(sync/gevent/eventlet)
worker_class = "sync"

# 每个worker的线程数
threads = 2

# Worker超时时间(秒)
timeout = 120

# 保持连接时间(秒)
keepalive = 5

# 最大请求数(超过后重启worker,防止内存泄漏)
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "-"  # 访问日志输出到stdout
errorlog = "-"   # 错误日志输出到stderr
loglevel = "info"

# 进程名称
proc_name = "family_emotion_system"

# 守护进程(生产环境建议使用systemd或supervisor管理,不启用)
daemon = False

# 预加载应用(减少内存占用)
preload_app = True

# 优雅重启超时时间
graceful_timeout = 30