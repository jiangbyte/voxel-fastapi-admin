""" Author: Charlie

认证路由：登录、注册、验证码、密码密钥、注销与账号注销等 HTTP 端点。
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.auth_schemas import (
    AuthOptionsApiResponse,
    AuthOptionsResponse,
    CancelAccountApiResponse,
    CancelAccountRequest,
    ForgotPasswordByPhoneRequest,
    ForgotPasswordRequest,
    LoginApiResponse,
    LoginPayload,
    LoginRequest,
    LoginResponse,
    LogoutApiResponse,
    RegisterApiResponse,
    RegisterRequest,
    ResetPasswordByPhoneRequest,
    ResetPasswordRequest,
    SendLoginCodeRequest,
    SendRegisterCodeRequest,
    SiteFooterResponse,
)
from cases.auth.auth_case import (
    session_expires_in,
)
from cases.auth.dto import LoginPayload, RegisterCommand
from infrastructure.auth.wiring import build_auth_service
from domain.auth.policy import get_auth_options, get_register_policy
from cases.sys.public.site_footer import resolve_site_footer
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import get_current_session, require_account_type
from infrastructure.deps.db import get_db_session
from infrastructure.network.client_ip import get_client_ip
from infrastructure.security.session import SessionPayload
from infrastructure.security.session_token import (
    clear_session_cookie,
    extract_session_token,
    set_session_cookie,
)
from infrastructure.security.transport import (
    CaptchaApiResponse,
    PasswordKeyApiResponse,
    create_captcha,
    create_password_key,
    decrypt_password,
    verify_captcha,
)
from infrastructure.web.schema import ApiResponse, success
from voxel_types.business import BusinessError

admin_router = APIRouter()


@admin_router.get("/v1/admin/auth/public/auth-options", response_model=AuthOptionsApiResponse)
async def admin_auth_options() -> AuthOptionsApiResponse:
    """返回管理端登录/注册策略选项。"""
    return success(_auth_options_response(AccountType.ADMIN))


def _auth_options_response(account_type: AccountType) -> AuthOptionsResponse:
    """将登录策略转换为对外的 AuthOptions 响应模型。"""
    from api.auth.oauth_schemas import (
        OauthProviderOptionSchema,
    )

    opts = get_auth_options(account_type)
    return AuthOptionsResponse(
        account_type=opts.account_type,
        allow_account=opts.allow_account,
        allow_email=opts.allow_email,
        allow_phone=opts.allow_phone,
        allow_otp=opts.allow_otp,
        register_enabled=opts.register_enabled,
        register_require_phone=opts.register_require_phone,
        register_require_email=opts.register_require_email,
        register_allow_account=opts.register_allow_account,
        register_allow_email=opts.register_allow_email,
        register_allow_phone=opts.register_allow_phone,
        force_bind_email=opts.force_bind_email,
        force_bind_phone=opts.force_bind_phone,
        password_change_verify_method=opts.password_change_verify_method,
        copyright_text=opts.copyright_text,
        copyright_url=opts.copyright_url,
        site_footer=SiteFooterResponse.model_validate(resolve_site_footer()),
        oauth_providers=[
            OauthProviderOptionSchema(**item) for item in opts.oauth_providers
        ],
    )


@admin_router.get("/v1/admin/auth/session/captcha", response_model=CaptchaApiResponse)
async def captcha() -> CaptchaApiResponse:
    """生成图形验证码。"""
    return success(await create_captcha())


@admin_router.get("/v1/admin/auth/session/password-key", response_model=PasswordKeyApiResponse)
async def password_key() -> PasswordKeyApiResponse:
    """生成一次性密码传输密钥（RSA 公钥）。"""
    return success(await create_password_key())


async def _login(
    *,
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession,
    account_type: AccountType,
) -> LoginApiResponse:
    """统一登录流程：校验验证码、解密密码并签发会话。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    login_mode = (payload.login_mode or "PASSWORD").strip().upper()
    password: str | None = None
    if login_mode != "OTP":
        if not payload.password or not payload.password_key_id:
            raise BusinessError("Password is required")
        password = await decrypt_password(payload.password_key_id, payload.password)
    service = build_auth_service(db)
    session = await service.login(
        LoginPayload(
            account=payload.account,
            password=password or "",
            account_type=account_type,
            identity_type=payload.identity_type,
            login_mode=login_mode,
            otp_code=payload.otp_code,
            remember_me=payload.remember_me,
            client_ip=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            device_label=_device_label(request.headers.get("user-agent")),
        )
    )
    set_session_cookie(
        response,
        session.token,
        request=request,
        remember_me=payload.remember_me,
    )
    warning = await service.password_expiry_warning_days(session.account_id)
    return success(
        LoginResponse(
            token=session.token,
            account_id=session.account_id,
            account_type=AccountType(str(session.account_type)),
            password_expired=session.password_expired,
            password_expiry_warning_days=warning,
            expires_in=session_expires_in(session),
            force_bind_email=session.force_bind_email,
            force_bind_phone=session.force_bind_phone,
        )
    )


@admin_router.post("/v1/admin/auth/session/login", response_model=LoginApiResponse)
async def admin_login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginApiResponse:
    """管理端登录端点。"""
    return await _login(
        payload=payload,
        request=request,
        response=response,
        db=db,
        account_type=AccountType.ADMIN,
    )


@admin_router.post(
    "/v1/admin/auth/session/refresh",
    response_model=LoginApiResponse,
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
)
async def auth_refresh(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginApiResponse:
    """刷新当前会话（滑动 TTL）并返回最新登录信息。"""
    return success(
        await build_auth_service(db).refresh_session(session.token, AccountType.ADMIN)
    )


@admin_router.post("/v1/admin/auth/session/send-login-code", response_model=ApiResponse[None])
async def send_login_code(
    payload: SendLoginCodeRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """发送邮箱/短信登录验证码。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    await build_auth_service(db).send_login_code(
        account_type=AccountType.ADMIN,
        channel=payload.channel,
        target=payload.target,
        client_ip=get_client_ip(request),
    )
    return success()


@admin_router.post("/v1/admin/auth/session/forgot-password", response_model=ApiResponse[None])
async def admin_forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """管理端忘记密码，发送重置邮件。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    await build_auth_service(db).forgot_password(
        payload,
        AccountType.ADMIN,
        client_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return success()


@admin_router.post("/v1/admin/auth/session/reset-password", response_model=ApiResponse[None])
async def admin_reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """管理端重置密码端点。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    password = await decrypt_password(payload.password_key_id, payload.password)
    await build_auth_service(db).reset_password(
        payload.model_copy(update={"password": password or ""}),
        AccountType.ADMIN,
        client_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return success()


@admin_router.post("/v1/admin/auth/session/forgot-password/phone", response_model=ApiResponse[None])
async def admin_forgot_password_by_phone(
    payload: ForgotPasswordByPhoneRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """管理端通过手机找回密码，发送重置 OTP。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    await build_auth_service(db).forgot_password_by_phone(
        payload,
        AccountType.ADMIN,
        client_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return success()


@admin_router.post("/v1/admin/auth/session/reset-password/phone", response_model=ApiResponse[None])
async def admin_reset_password_by_phone(
    payload: ResetPasswordByPhoneRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """管理端通过手机 OTP 重置密码。"""
    await verify_captcha(payload.captcha_id, payload.captcha_value)
    password = await decrypt_password(payload.password_key_id, payload.password)
    await build_auth_service(db).reset_password_by_phone(
        payload.model_copy(update={"password": password or ""}),
        AccountType.ADMIN,
        client_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return success()


@admin_router.post(
    "/v1/admin/auth/session/logout",
    response_model=LogoutApiResponse,
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
)
async def logout(
    request: Request,
    response: Response,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> LogoutApiResponse:
    """统一退出登录接口，优先读取 cookie / 请求头中的原始 token。"""
    token = extract_session_token(request, authorization) or session.token
    await build_auth_service(db).logout(token)
    clear_session_cookie(response, request=request)
    return success()


def _device_label(user_agent: str | None) -> str | None:
    """根据 User-Agent 粗略推断设备类型标签。"""
    if not user_agent:
        return None
    value = user_agent.lower()
    if "mobile" in value or "android" in value or "iphone" in value:
        return "Mobile"
    if "ipad" in value or "tablet" in value:
        return "Tablet"
    return "Desktop"


@admin_router.post(
    "/v1/admin/auth/session/cancel",
    response_model=CancelAccountApiResponse,
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
)
async def cancel_account(
    request: Request,
    response: Response,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    payload: Annotated[CancelAccountRequest, Body()] = CancelAccountRequest(),
) -> CancelAccountApiResponse:
    """统一账号注销接口，只注销当前登录账号（请求体可省略）。"""
    from cases.auth.dto import CancelAccountCommand
    await build_auth_service(db).cancel_current_account(
        CancelAccountCommand.model_validate(payload.model_dump()), session
    )
    clear_session_cookie(response, request=request)
    return success()
