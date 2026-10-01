""" Author: Charlie

门户用户中心路由：当前账户信息、资料、头像、密码、手机与邮箱维护，及公开主页。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from domain.iam.enums import AccountIdentityBindStatus
from infrastructure.iam.dao.account_repository import (
    AccountRepository,
)
from api.profile.portal_schemas import (
    PortalPublicProfileResponse,
    PortalPublicSpaceQuery,
    PortalUserCenterAvatarUpdateResponse,
    PortalUserCenterEmailUpdateRequest,
    PortalUserCenterPasswordUpdateRequest,
    PortalUserCenterPhoneUpdateRequest,
    PortalUserCenterProfileUpdateRequest,
    ProfileUserPortalResponse,
)
from api.profile.profile_schemas import (
    BindTargetRequest,
    PortalMeResponse,
)
from cases.profile.portal.portal_case import (
    AVATAR_MAX_SIZE,
    ProfileUserPortalCase,
)
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import get_current_session, require_account_type
from infrastructure.deps.db import get_db_session
from infrastructure.security.session import SessionPayload
from infrastructure.security.transport import decrypt_passwords
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.get(
    "/v1/portal/auth/session/me",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[PortalMeResponse],
)
async def get_me(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PortalMeResponse]:
    """查询当前门户用户的扩展资料信息。"""
    account_repo = AccountRepository(db)
    await account_repo.get_required(session.account_id)
    identities = await account_repo.list_identities_by_account_ids([session.account_id])
    primary_identity = next(
        (item for item in identities if item.identity_type == "ACCOUNT" and item.is_primary == 1),
        None,
    ) or next((item for item in identities if item.identity_type == "ACCOUNT"), None)
    email_identity = next((item for item in identities if item.identity_type == "EMAIL"), None)
    phone_identity = next((item for item in identities if item.identity_type == "PHONE"), None)
    profile = await build_profile_user_portal_service(db).get_profile(session.account_id)
    from cases.sys.file.file_case import FileCase

    avatar = await FileCase(db).resolve_access_url(profile.avatar if profile else None)
    from infrastructure.auth.wiring import build_auth_service
    from cases.iam.account.password_helper import is_password_expired

    account_entity = await account_repo.get_required(session.account_id)
    role_id_names, dept_id_names, group_id_names = (
        await build_profile_user_portal_service(db).get_id_name_groups(
            session.role_ids,
            session.dept_ids,
            session.group_ids,
        )
    )
    force_bind_email, force_bind_phone = await build_auth_service(db)._force_bind_flags(
        account_entity, AccountType.PORTAL
    )
    auth_service = build_auth_service(db)
    from cases.profile.identity.identity_case import (
        ProfileIdentityCase,
    )

    identity = await build_profile_identity_service(db).get_user_status_for_account(session.account_id)
    return success(
        PortalMeResponse(
            account_id=session.account_id,
            account=getattr(primary_identity, "identifier", ""),
            account_type=AccountType(str(session.account_type)),
            nickname=profile.nickname if profile else None,
            avatar=avatar,
            role_ids=session.role_ids,
            dept_ids=session.dept_ids,
            group_ids=session.group_ids,
            role_id_names=role_id_names,
            dept_id_names=dept_id_names,
            group_id_names=group_id_names,
            permission_keys=session.permission_keys,
            password_expired=await is_password_expired(db, session.account_id),
            force_bind_email=force_bind_email,
            force_bind_phone=force_bind_phone,
            force_bind_identity=await auth_service.force_bind_identity_flag(
                session.account_id, AccountType.PORTAL
            ),
            identity=identity,
            profile=ProfileUserPortalResponse(
                account_id=session.account_id,
                nickname=profile.nickname if profile else None,
                avatar=avatar,
                signature=profile.signature if profile else None,
                phone=profile.phone if profile else None,
                email=profile.email if profile else None,
                phone_login_enabled=_identity_login_enabled(phone_identity),
                email_login_enabled=_identity_login_enabled(email_identity),
                created_at=profile.created_at if profile else None,
                updated_at=profile.updated_at if profile else None,
            ),
        )
    )


@router.post(
    "/v1/portal/profile/account/update",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def update_user_center_profile(
    payload: PortalUserCenterProfileUpdateRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """更新当前门户用户个人资料。"""
    await build_profile_user_portal_service(db).update_current_profile(payload, session)
    return success()


@router.post(
    "/v1/portal/profile/account/avatar/upload",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[PortalUserCenterAvatarUpdateResponse],
)
async def upload_user_center_avatar(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PortalUserCenterAvatarUpdateResponse]:
    """上传并更新当前门户用户头像。"""
    content = await file.read(AVATAR_MAX_SIZE + 1)
    return success(
        await build_profile_user_portal_service(db).update_current_avatar(
            content=content,
            content_type=file.content_type or "",
            session=session,
        )
    )


@router.post(
    "/v1/portal/profile/account/phone/send-code",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def send_user_center_phone_code(
    payload: BindTargetRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """向待绑定手机号发送验证码。"""
    from infrastructure.auth.wiring import build_auth_service

    await build_auth_service(db).send_bind_code(
        account_type=AccountType.PORTAL,
        channel="PHONE",
        target=payload.target,
        account_id=session.account_id,
    )
    return success()


@router.post(
    "/v1/portal/profile/account/email/send-code",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def send_user_center_email_code(
    payload: BindTargetRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """向待绑定邮箱发送验证码。"""
    from infrastructure.auth.wiring import build_auth_service

    await build_auth_service(db).send_bind_code(
        account_type=AccountType.PORTAL,
        channel="EMAIL",
        target=payload.target,
        account_id=session.account_id,
    )
    return success()


@router.post(
    "/v1/portal/profile/account/password/send-code",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def send_user_center_password_code(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """向当前门户用户发送改密验证码。"""
    from cases.auth.password_change import send_change_password_code
    from infrastructure.iam.dao.account_repository import (
        AccountRepository,
    )

    account = await AccountRepository(db).get_required(session.account_id)
    await send_change_password_code(
        db, account=account, account_type=AccountType.PORTAL
    )
    return success()


@router.post(
    "/v1/portal/profile/account/password/update",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def update_user_center_password(
    payload: PortalUserCenterPasswordUpdateRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """修改当前门户用户密码。"""
    old_password, new_password = await decrypt_passwords(
        payload.password_key_id,
        payload.old_password,
        payload.new_password,
    )
    await build_profile_user_portal_service(db).update_current_password(
        payload.model_copy(
            update={
                "old_password": old_password,
                "new_password": new_password or "",
            }
        ),
        session,
    )
    return success()


@router.post(
    "/v1/portal/profile/account/phone/update",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def update_user_center_phone(
    payload: PortalUserCenterPhoneUpdateRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """更新当前门户用户手机号绑定。"""
    password = (await decrypt_passwords(payload.password_key_id, payload.password))[0]
    await build_profile_user_portal_service(db).update_current_phone(
        payload.model_copy(update={"password": password or ""}),
        session,
    )
    return success()


@router.post(
    "/v1/portal/profile/account/email/update",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[None],
)
async def update_user_center_email(
    payload: PortalUserCenterEmailUpdateRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[None]:
    """更新当前门户用户邮箱绑定。"""
    password = (await decrypt_passwords(payload.password_key_id, payload.password))[0]
    await build_profile_user_portal_service(db).update_current_email(
        payload.model_copy(update={"password": password or ""}),
        session,
    )
    return success()


@router.get(
    "/v1/portal/sys/space/detail",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[PortalPublicProfileResponse],
)
async def get_public_space(
    query: Annotated[PortalPublicSpaceQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PortalPublicProfileResponse]:
    """查询门户用户公开主页资料（要求 PORTAL 会话，对齐 voxel-boot）。"""
    return success(await build_profile_user_portal_service(db).get_public_profile(query))


def _identity_login_enabled(identity) -> bool:
    """判断绑定身份是否可用于登录（仅要求 BOUND，对齐 voxel-boot）。"""
    return bool(
        identity
        and identity.identifier
        and identity.bind_status == AccountIdentityBindStatus.BOUND.value
    )
