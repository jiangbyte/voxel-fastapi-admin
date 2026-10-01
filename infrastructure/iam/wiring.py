"""IAM 限界上下文依赖装配。"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cases.iam.account.account_case import (
    AccountCase,
)
from cases.iam.account.account_read_service import AccountReadService
from cases.iam.client.client_case import (
    ClientModuleCase,
    ClientResourceCase,
)
from cases.iam.dept.dept_case import DeptCase
from cases.iam.group.group_case import GroupCase
from cases.iam.position.position_case import (
    PositionCase,
)
from cases.iam.resource.resource_case import (
    ResourceModuleCase,
    ResourceCase,
)
from cases.iam.role.role_case import RoleCase
from infrastructure.profile.api.profile_read_adapter import (
    get_profile_read_port,
)
from infrastructure.iam.api.account_api_adapter import get_account_api
from infrastructure.iam.dao.account_repository import (
    AccountRepositoryImpl,
)
from infrastructure.iam.dao.client_repository import (
    ClientModuleRepository,
    ClientResourceRepository,
)
from infrastructure.iam.dao.dept_repository import (
    DeptRepositoryImpl,
)
from infrastructure.iam.dao.group_repository import (
    GroupRepositoryImpl,
)
from infrastructure.iam.dao.password_history_repository import (
    PasswordHistoryRepositoryImpl,
)
from infrastructure.iam.dao.position_repository import (
    PositionRepositoryImpl,
)
from infrastructure.iam.dao.relation_repository import (
    IamRelationRepositoryImpl,
)
from infrastructure.iam.dao.resource_repository import (
    ResourceModuleRepository,
    ResourceRepositoryImpl,
)
from infrastructure.iam.dao.role_repository import (
    RoleRepositoryImpl,
)
from infrastructure.iam.support.iam_audit_adapter import IamAuditAdapter
from infrastructure.profile.api.profile_read_adapter import (
    ProfileReadAdapter,
)
from infrastructure.profile.api.profile_upsert_adapter import (
    ProfileUpsertAdapter,
)
from infrastructure.deps.db import get_db_session

__all__ = ["get_account_api"]


def _audit(db: AsyncSession) -> IamAuditAdapter:
    return IamAuditAdapter(db)


def _relation(db: AsyncSession) -> IamRelationRepositoryImpl:
    return IamRelationRepositoryImpl(db)


def _account_repo(db: AsyncSession) -> AccountRepositoryImpl:
    return AccountRepositoryImpl(db)


def get_position_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PositionCase:
    return PositionCase(db, PositionRepositoryImpl(db))


def get_dept_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeptCase:
    return DeptCase(db, DeptRepositoryImpl(db))


def get_resource_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResourceCase:
    return ResourceCase(
        db,
        _audit(db),
        repo=ResourceRepositoryImpl(db),
        relation_repo=_relation(db),
    )


def get_resource_module_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResourceModuleCase:
    return ResourceModuleCase(db, ResourceModuleRepository(db))


def get_client_resource_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ClientResourceCase:
    return ClientResourceCase(db, _audit(db), repo=ClientResourceRepository(db))


def get_client_module_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ClientModuleCase:
    return ClientModuleCase(db, _audit(db), repo=ClientModuleRepository(db))


def get_role_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RoleCase:
    return RoleCase(
        db,
        _audit(db),
        repo=RoleRepositoryImpl(db),
        relation_repo=_relation(db),
        resource_service=get_resource_service(db),
        client_resource_service=get_client_resource_service(db),
        account_repo=_account_repo(db),
        profile_read_port=get_profile_read_port(db),
    )


def get_group_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> GroupCase:
    return GroupCase(
        db,
        _audit(db),
        repo=GroupRepositoryImpl(db),
        relation_repo=_relation(db),
        resource_service=get_resource_service(db),
        client_resource_service=get_client_resource_service(db),
        account_repo=_account_repo(db),
        role_repo=RoleRepositoryImpl(db),
    )


def get_account_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AccountCase:
    # 延迟导入，打断 iam.wiring ↔ profile.wiring 循环
    from infrastructure.profile.wiring import (
        build_profile_identity_service,
    )

    repo = AccountRepositoryImpl(db)
    return AccountCase(
        db,
        repo=repo,
        profile_port=ProfileUpsertAdapter(db),
        relation_repo=_relation(db),
        audit=_audit(db),
        read_service=AccountReadService(repo, ProfileReadAdapter(db)),
        resource_service=get_resource_service(db),
        client_resource_service=get_client_resource_service(db),
        role_repo=RoleRepositoryImpl(db),
        group_repo=GroupRepositoryImpl(db),
        identity_service=build_profile_identity_service(db),
    )


def get_password_history_port(db: AsyncSession) -> PasswordHistoryRepositoryImpl:
    return PasswordHistoryRepositoryImpl(db)
