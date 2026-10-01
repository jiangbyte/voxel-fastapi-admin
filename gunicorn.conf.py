from app.core.config.settings import settings

bind = f"{settings.app.host}:{settings.app.port}"
worker_class = "uvicorn.workers.UvicornWorker"
# 多 worker 各自运行内置任务调度器；同一任务的执行由 Redis 锁（sys:job:run:*）串行化，
# 保证不会重复执行（对齐 voxel-boot 调度模型）。
max_requests = 10000
max_requests_jitter = 1000
timeout = 30
graceful_timeout = 30
keepalive = 5
accesslog = None  # App AccessLogMiddleware owns access logging
errorlog = "-"
loglevel = "info"
