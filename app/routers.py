""" Author: Charlie

API 路由装配：显式挂载全部限界上下文路由（对齐 voxel-fastapi explicit deps）。

完整路径写在各路由装饰器上（``/v1/admin/...``），这里统一挂 ``/api`` 前缀并保留
OpenAPI tags（admin / portal / internal / public）。
"""

from __future__ import annotations

from functools import cache

from fastapi import APIRouter

from trigger.auth.http.auth_router import (
    admin_router as auth_admin_router,
)
from trigger.auth.http.oauth_router import (
    admin_router as oauth_admin_router,
)
from trigger.auth.http.session_admin_router import (
    router as auth_session_admin_router,
)
from trigger.iam.http.account_router import router as iam_account_router
from trigger.iam.http.client_router import router as iam_client_router
from trigger.iam.http.dept_router import router as iam_dept_router
from trigger.iam.http.group_router import router as iam_group_router
from trigger.iam.http.position_router import (
    router as iam_position_router,
)
from trigger.iam.http.resource_router import (
    router as iam_resource_router,
)
from trigger.iam.http.role_router import router as iam_role_router
from trigger.profile.http.admin_router import (
    router as profile_admin_router,
)
from trigger.profile.http.identity_router import (
    admin_manage_router as profile_identity_manage_router,
)
from trigger.profile.http.identity_router import (
    admin_user_router as profile_identity_admin_router,
)
from trigger.sys.http.audit_router import router as sys_audit_router
from trigger.sys.http.banner_router import router as banner_router
from trigger.sys.http.codegen_router import router as sys_codegen_router
from trigger.sys.http.config_router import router as sys_config_router
from trigger.sys.http.dict_router import router as sys_dict_router
from trigger.sys.http.feedback_router import (
    admin_router as feedback_admin_router,
)
from trigger.sys.http.file_router import router as sys_file_router
from trigger.sys.http.health_router import (
    router as internal_health_router,
)
from trigger.sys.http.job_router import router as sys_job_router
from trigger.sys.http.notice_router import (
    admin_router as notice_admin_router,
)
from trigger.sys.http.public_router import router as sys_public_router
from trigger.sys.http.weak_password_router import (
    router as weak_password_router,
)
from trigger.sys.http.workspace_router import router as workspace_router
from infrastructure.paths import API_ROOT_PREFIX
from infrastructure.router import enable_response_exclude_none

# (tags, router) 挂载清单，顺序与历史注册顺序一致。
_ROUTERS: list[tuple[str, APIRouter]] = [
    ("admin", workspace_router),
    ("admin", auth_admin_router),
    ("admin", auth_session_admin_router),
    ("admin", oauth_admin_router),
    ("admin", iam_account_router),
    ("admin", iam_client_router),
    ("admin", iam_dept_router),
    ("admin", iam_group_router),
    ("admin", iam_position_router),
    ("admin", iam_resource_router),
    ("admin", iam_role_router),
    ("internal", internal_health_router),
    ("admin", feedback_admin_router),
    ("admin", notice_admin_router),
    ("admin", sys_audit_router),
    ("public", sys_public_router),
    ("admin", banner_router),
    ("admin", sys_codegen_router),
    ("admin", sys_config_router),
    ("admin", sys_dict_router),
    ("admin", sys_file_router),
    ("admin", sys_job_router),
    ("admin", weak_password_router),
    ("admin", profile_admin_router),
    ("admin", profile_identity_admin_router),
    ("admin", profile_identity_manage_router),
]


@cache
def get_api_router() -> APIRouter:
    """构建并缓存 API 根路由。"""
    api_router = APIRouter()
    for tags, router in _ROUTERS:
        api_router.include_router(router, prefix=API_ROOT_PREFIX, tags=[tags])
    enable_response_exclude_none(api_router)
    return api_router
