"""auth 限界上下文依赖装配。"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cases.auth.auth_case import AuthCase
from cases.auth.oauth.oauth_case import (
    AuthOauthCase,
)
from cases.auth.session_admin_service import SessionAdminCase
from cases.auth.session_service import AccountSessionService
from infrastructure.auth.api.oauth_adapters import (
    get_oauth_binding_repository_port,
    get_oauth_client_port,
    get_oauth_exchange_store_port,
    get_oauth_state_store_port,
)
from cases.iam.api.account_api import AccountApi
from domain.iam.account.password_port import AccountPasswordPort
from domain.iam.relation.repository import IamRelationRepositoryPort
from infrastructure.iam.api.account_api_adapter import get_account_api
from infrastructure.iam.dao.relation_repository import (
    IamRelationRepositoryImpl,
)
from infrastructure.iam.wiring import get_password_history_port
from cases.profile.api.profile_upsert_port import ProfileUpsertPort
from infrastructure.profile.api.profile_read_adapter import (
    get_profile_read_port,
)
from infrastructure.profile.api.profile_upsert_adapter import (
    get_profile_upsert_port,
)
from infrastructure.deps.db import get_db_session


def get_account_session_service(
    db: AsyncSession,
    *,
    account_api: AccountApi | None = None,
    relation_repo: IamRelationRepositoryPort | None = None,
) -> AccountSessionService:
    return AccountSessionService(
        db,
        account_api=account_api or get_account_api(db),
        relation_repo=relation_repo or IamRelationRepositoryImpl(db),
    )


def build_auth_service(db: AsyncSession) -> AuthCase:
    account_api = get_account_api(db)
    relation_repo = IamRelationRepositoryImpl(db)
    return AuthCase(
        db,
        account_api=account_api,
        relation_repo=relation_repo,
        session_service=get_account_session_service(
            db, account_api=account_api, relation_repo=relation_repo
        ),
        profile_port=get_profile_upsert_port(db),
        password_port=get_password_history_port(db),
        profile_read_port=get_profile_read_port(db),
    )


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthCase:
    return build_auth_service(db)


def get_auth_oauth_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthOauthCase:
    auth = build_auth_service(db)
    return AuthOauthCase(
        db,
        auth_service=auth,
        oauth_client=get_oauth_client_port(),
        state_store=get_oauth_state_store_port(),
        exchange_store=get_oauth_exchange_store_port(),
        binding_repo=get_oauth_binding_repository_port(db),
    )


def get_session_admin_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionAdminCase:
    return SessionAdminCase(db, account_api=get_account_api(db))

