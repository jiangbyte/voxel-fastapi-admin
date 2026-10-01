""" Author: Charlie

示例任务处理器：回显执行参数，用于验证调度链路（对齐 voxel-boot SysJobSample）。
"""

import logging

from cases.sys.job.registry import job_handler

logger = logging.getLogger(__name__)


@job_handler("sys_job_sample")
async def sys_job_sample(params: dict | None) -> str:
    """回显执行参数，便于人工验证任务是否被正确触发。"""
    logger.info("SysJobSample execute, params=%s", params)
    return f"echo: {params if params is not None else '(无参数)'}"
