"""profile 限界上下文依赖装配。"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.auth.api.bind_code_adapter import get_bind_code_port
from infrastructure.iam.api.account_api_adapter import get_account_api
from infrastructure.iam.api.org_read_adapter import get_iam_org_read_api
from infrastructure.iam.dao.relation_repository import (
    IamRelationRepositoryImpl,
)
from infrastructure.iam.wiring import get_password_history_port
from cases.profile.admin.admin_case import (
    ProfileUserAdminCase,
)
from cases.profile.identity.identity_case import (
    ProfileIdentityCase,
    RealNameWorkflowCase,
)
from cases.profile.portal.portal_case import (
    ProfileUserPortalCase,
)
from infrastructure.profile.api.identity_provider_registry_adapter import (
    get_identity_provider_registry_port,
)
from infrastructure.profile.dao.admin_repository import (
    ProfileUserAdminRepositoryImpl,
)
from infrastructure.profile.dao.identity_repository import (
    ProfileIdentityRepositoryImpl,
    RealNameCaseRecordRepositoryImpl,
    RealNameCaseRepositoryImpl,
)
from infrastructure.profile.dao.portal_repository import (
    ProfileUserPortalRepositoryImpl,
)
from infrastructure.deps.db import get_db_session


def build_profile_user_admin_service(db: AsyncSession) -> ProfileUserAdminCase:
    # 延迟导入，打断 auth.wiring ↔ profile.wiring 循环
    from infrastructure.auth.wiring import get_account_session_service

    account_api = get_account_api(db)
    relation_repo = IamRelationRepositoryImpl(db)
    return ProfileUserAdminCase(
        db,
        repo=ProfileUserAdminRepositoryImpl(db),
        account_api=account_api,
        org_read_api=get_iam_org_read_api(db),
        password_port=get_password_history_port(db),
        session_service=get_account_session_service(
            db, account_api=account_api, relation_repo=relation_repo
        ),
        bind_code_port=get_bind_code_port(db),
    )


def get_profile_user_admin_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileUserAdminCase:
    return build_profile_user_admin_service(db)


def build_profile_user_portal_service(db: AsyncSession) -> ProfileUserPortalCase:
    from infrastructure.auth.wiring import get_account_session_service

    account_api = get_account_api(db)
    relation_repo = IamRelationRepositoryImpl(db)
    return ProfileUserPortalCase(
        db,
        repo=ProfileUserPortalRepositoryImpl(db),
        account_api=account_api,
        org_read_api=get_iam_org_read_api(db),
        password_port=get_password_history_port(db),
        session_service=get_account_session_service(
            db, account_api=account_api, relation_repo=relation_repo
        ),
        bind_code_port=get_bind_code_port(db),
    )


def get_profile_user_portal_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileUserPortalCase:
    return build_profile_user_portal_service(db)


def build_profile_identity_service(db: AsyncSession) -> ProfileIdentityCase:
    account_api = get_account_api(db)
    return ProfileIdentityCase(
        db,
        identity_repo=ProfileIdentityRepositoryImpl(db),
        case_repo=RealNameCaseRepositoryImpl(db),
        account_api=account_api,
    )


def build_real_name_case_service(db: AsyncSession) -> RealNameWorkflowCase:
    account_api = get_account_api(db)
    identity_repo = ProfileIdentityRepositoryImpl(db)
    case_repo = RealNameCaseRepositoryImpl(db)
    return RealNameWorkflowCase(
        db,
        account_api=account_api,
        identity_repo=identity_repo,
        case_repo=case_repo,
        case_record_repo=RealNameCaseRecordRepositoryImpl(db),
        provider_registry=get_identity_provider_registry_port(),
    )


def get_profile_identity_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileIdentityCase:
    return build_profile_identity_service(db)
