"""展示图定时任务处理器。"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from cases.sys.job.registry import job_handler
from infrastructure.sys.dao.banner_repository import (
    BannerRepositoryImpl,
)
from infrastructure.sys.wiring import build_banner_service
from infrastructure.dao.session import get_session_factory
from infrastructure.redis.redis import get_redis

logger = logging.getLogger(__name__)


@job_handler("sys_banner_flush_interactions")
async def flush_banner_interactions(params: dict | None) -> str:
    redis = get_redis()
    if redis is None:
        return "flushed=0"
    factory = get_session_factory()
    async with factory() as session:
        count = await build_banner_service(session).flush_interaction_deltas(redis)
    return f"flushed={count}"


@job_handler("sys_banner_status_sync")
async def sync_banner_status(params: dict | None) -> str:
    now = datetime.now(UTC)
    factory = get_session_factory()
    async with factory() as session:
        result = await BannerRepositoryImpl(session).sync_status(now)
        await session.commit()
    return f"expired={result['expired']},activated={result['activated']}"
