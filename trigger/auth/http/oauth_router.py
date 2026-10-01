""" Author: Charlie

三方登录路由：管理端与门户端的授权/回调/兑换/绑定/解绑。
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.oauth_schemas import (
    AdminOauthUnbindRequest,
    OauthAuthorizeResult,
    OauthBindingResult,
    OauthExchangeRequest,
)
from cases.auth.oauth.oauth_case import (
    AuthOauthCase,
)
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import (
    get_current_session,
    get_optional_session,
    require_permission,
)
from infrastructure.auth.wiring import get_auth_oauth_service
from infrastructure.deps.db import get_db_session
from infrastructure.security.session import SessionPayload
from infrastructure.web.schema import ApiResponse, success

admin_router = APIRouter()

SessionDep = Annotated[SessionPayload, Depends(get_current_session)]
OptionalSessionDep = Annotated[SessionPayload | None, Depends(get_optional_session)]


def _oauth_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> AuthOauthCase:
    """构造 OAuth 服务实例。"""
    return get_auth_oauth_service(db)


ServiceDep = Annotated[AuthOauthCase, Depends(_oauth_service)]


@admin_router.get(
    "/v1/admin/auth/oauth/{provider}/authorize",
    response_model=ApiResponse[OauthAuthorizeResult],
)
async def admin_oauth_authorize(
    provider: str,
    service: ServiceDep,
    session: OptionalSessionDep,
    intent: str | None = None,
    redirect: str | None = None,
) -> ApiResponse[OauthAuthorizeResult]:
    """发起管理端三方登录/绑定授权。"""
    result = await service.authorize(
        AccountType.ADMIN, provider, intent, redirect, session
    )
    return success(OauthAuthorizeResult(**result))


@admin_router.get("/v1/admin/auth/oauth/{provider}/callback")
async def admin_oauth_callback(
    provider: str,
    service: ServiceDep,
    code: str | None = None,
    state: str | None = None,
) -> RedirectResponse:
    """管理端三方登录回调：302 跳回前端回调页。"""
    location = await service.handle_callback(
        AccountType.ADMIN, provider, code, state
    )
    return RedirectResponse(url=location)


@admin_router.post(
    "/v1/admin/auth/oauth/exchange",
    response_model=ApiResponse,
)
async def admin_oauth_exchange(
    payload: OauthExchangeRequest,
    service: ServiceDep,
) -> ApiResponse:
    """用一次性兑换码换取登录结果。"""
    return success(await service.exchange(payload.code))


@admin_router.get(
    "/v1/admin/auth/oauth/bindings",
    response_model=ApiResponse[list[OauthBindingResult]],
)
async def admin_oauth_bindings(
    service: ServiceDep,
    session: SessionDep,
) -> ApiResponse[list[OauthBindingResult]]:
    """列出当前管理端账号三方绑定。"""
    return success(await service.list_current_bindings(session.account_id))


@admin_router.post(
    "/v1/admin/auth/oauth/{provider}/bind/authorize",
    response_model=ApiResponse[OauthAuthorizeResult],
)
async def admin_oauth_bind_authorize(
    provider: str,
    service: ServiceDep,
    session: SessionDep,
) -> ApiResponse[OauthAuthorizeResult]:
    """发起管理端三方绑定授权。"""
    result = await service.bind_authorize(
        AccountType.ADMIN, provider, session
    )
    return success(OauthAuthorizeResult(**result))


@admin_router.post(
    "/v1/admin/auth/oauth/{provider}/unbind",
    response_model=ApiResponse[None],
)
async def admin_oauth_unbind(
    provider: str,
    service: ServiceDep,
    session: SessionDep,
) -> ApiResponse[None]:
    """解绑当前管理端账号指定提供商。"""
    await service.unbind(session.account_id, provider)
    return success()


@admin_router.post(
    "/v1/admin/iam/account/oauth/unbind",
    dependencies=[Depends(require_permission("iam:account:update"))],
    response_model=ApiResponse[None],
)
async def admin_accounts_oauth_unbind(
    payload: AdminOauthUnbindRequest,
    service: ServiceDep,
) -> ApiResponse[None]:
    """管理端强制解绑指定账号的三方绑定。"""
    await service.admin_unbind(payload.account_id, payload.provider)
    return success()
