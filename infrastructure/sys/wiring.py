"""sys 限界上下文依赖装配。"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cases.sys.audit.audit_case import (
    OperationAuditCase,
)
from cases.sys.banner.banner_case import (
    BannerCase,
)
from cases.sys.codegen.codegen_case import (
    CodegenCase,
)
from cases.sys.config.config_case import ConfigCase
from cases.sys.dict.dict_case import DictCase
from cases.sys.feedback.feedback_case import (
    SysFeedbackCase,
)
from cases.sys.file.file_case import FileCase
from cases.sys.job.job_case import JobCase
from cases.sys.notice.notice_case import (
    SysNoticeCase,
)
from cases.sys.weak_password.weak_password_case import (
    WeakPasswordCase,
)
from cases.sys.workspace.workspace_case import (
    WorkspaceCase,
)
from infrastructure.sys.job.runner import JobRunnerImpl
from infrastructure.sys.dao.audit_repository import (
    OperationAuditRepositoryImpl,
)
from infrastructure.sys.dao.banner_repository import (
    BannerRepositoryImpl,
)
from infrastructure.sys.dao.codegen_repository import (
    CodegenRepositoryImpl,
)
from infrastructure.sys.dao.config_repository import (
    ConfigRepositoryImpl,
)
from infrastructure.sys.dao.dict_repository import (
    DictRepositoryImpl,
)
from infrastructure.sys.dao.feedback_repository import (
    SysFeedbackRepositoryImpl,
)
from infrastructure.sys.dao.file_repository import (
    FileRepositoryImpl,
)
from infrastructure.sys.dao.job_repository import (
    JobLogRepositoryImpl,
    JobRepositoryImpl,
)
from infrastructure.sys.dao.notice_repository import (
    SysNoticeRepositoryImpl,
)
from infrastructure.sys.dao.weak_password_repository import (
    WeakPasswordRepositoryImpl,
)
from infrastructure.sys.dao.workspace_repository import (
    WorkspaceShortcutRepositoryImpl,
)
from infrastructure.sys.read.account_identity_read_adapter import (
    AccountIdentityReadAdapter,
)
from infrastructure.sys.read.workspace_read_adapter import (
    WorkspaceReadAdapter,
)
from infrastructure.deps.db import get_db_session


def build_job_service(db: AsyncSession) -> JobCase:
    return JobCase(db, JobRepositoryImpl(db), JobLogRepositoryImpl(db), JobRunnerImpl())


def get_dict_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> DictCase:
    return DictCase(db, DictRepositoryImpl(db))


def get_weak_password_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> WeakPasswordCase:
    return WeakPasswordCase(db, WeakPasswordRepositoryImpl(db))


def get_config_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ConfigCase:
    return ConfigCase(db, ConfigRepositoryImpl(db))


def get_notice_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SysNoticeCase:
    return SysNoticeCase(db, SysNoticeRepositoryImpl(db))


def get_file_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> FileCase:
    return FileCase(db, FileRepositoryImpl(db))


def get_job_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> JobCase:
    return build_job_service(db)


def build_audit_service(db: AsyncSession) -> OperationAuditCase:
    return OperationAuditCase(db, OperationAuditRepositoryImpl(db))


def get_audit_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> OperationAuditCase:
    return build_audit_service(db)


def build_banner_service(db: AsyncSession) -> BannerCase:
    return BannerCase(db, BannerRepositoryImpl(db), FileCase(db, FileRepositoryImpl(db)))


def get_banner_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> BannerCase:
    return build_banner_service(db)


def get_feedback_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SysFeedbackCase:
    file_repo = FileRepositoryImpl(db)
    file_service = FileCase(db, file_repo)
    from infrastructure.profile.api.profile_read_adapter import (
        get_profile_read_port,
    )

    return SysFeedbackCase(
        db,
        SysFeedbackRepositoryImpl(db),
        file_repo,
        file_service,
        profile_read_port=get_profile_read_port(db),
    )


def get_codegen_service(db: Annotated[AsyncSession, Depends(get_db_session)]) -> CodegenCase:
    return CodegenCase(db, CodegenRepositoryImpl(db))


def get_workspace_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceCase:
    return WorkspaceCase(db, WorkspaceShortcutRepositoryImpl(db), WorkspaceReadAdapter(db))


def get_account_identity_reader(db: AsyncSession) -> AccountIdentityReadAdapter:
    return AccountIdentityReadAdapter(db)
