""" Author: Charlie

应用生命周期：启动/关闭时初始化与清理各平台组件。
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.audit.queue import (
    start_operation_audit_queue,
    stop_operation_audit_queue,
)
from infrastructure.config.apply import apply_all_config
from infrastructure.config.reader import config_reader
from infrastructure.config.sync import start_config_sync_listener, stop_config_sync_listener
from infrastructure.http.client import close_http_client, init_http_client
from infrastructure.messaging import emit
from infrastructure.observability.tracing import shutdown_tracing
from infrastructure.dao.session import close_engine, init_engine
from infrastructure.redis.redis import close_redis, init_redis
from infrastructure.secrets.validate import validate_secrets_config
from infrastructure.security.auth_whitelist import get_auth_whitelist_patterns
from infrastructure.security.permission_registry import sync_permission_registry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期：启动初始化各组件，关闭时依次清理。"""
    logger.info("lifespan startup: app.routes count = %d", len(app.routes))

    # 1. 基础设施：DB、Redis、密钥校验、审计队列
    init_engine()
    await init_redis()
    validate_secrets_config()
    await start_operation_audit_queue()

    # 2. 运行时配置加载与跨进程同步
    await config_reader.load_all()
    apply_all_config()
    await start_config_sync_listener()

    # 3. 鉴权白名单缓存、权限注册表、HTTP 客户端
    get_auth_whitelist_patterns()
    await sync_permission_registry(app)
    await init_http_client()

    # 4. 任务调度（上下文就绪后可选启动）
    try:
        from infrastructure.sys.job_scheduler import (
            start_job_scheduler,
            stop_job_scheduler,
        )

        await start_job_scheduler()
        job_scheduler_ready = True
    except ImportError:
        job_scheduler_ready = False
        stop_job_scheduler = None  # type: ignore[assignment]
        logger.debug("job scheduler not available yet")

    await emit("on_db_ready")

    try:
        yield
    finally:
        # 5. 逆序清理
        if job_scheduler_ready and stop_job_scheduler is not None:
            await stop_job_scheduler()
        await stop_config_sync_listener()
        await stop_operation_audit_queue()
        await close_http_client()
        await close_redis()
        await close_engine()
        shutdown_tracing()
