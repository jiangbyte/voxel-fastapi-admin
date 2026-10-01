"""门户端操作审计。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.audit_schemas import (
    OperationAuditPageQuery,
    OperationAuditRecord,
)
from cases.sys.audit.audit_case import (
    OperationAuditCase,
)
from cases.sys.audit.dto import (
    OperationAuditPageQuery as OperationAuditPageQueryDto,
)
from infrastructure.sys.wiring import get_audit_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import get_current_session, require_account_type
from voxel_types.schema.base import IdQuery
from infrastructure.security.session import SessionPayload
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


def _map_page(page: PageData[dict]) -> PageData[OperationAuditRecord]:
    return PageData(
        current=page.current,
        size=page.size,
        total=page.total,
        records=[OperationAuditRecord.model_validate(r) for r in page.records],
    )


@router.get(
    "/v1/portal/sys/audit/my-page",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[PageData[OperationAuditRecord]],
    response_model_exclude_none=False,
)
async def my_page(
    query: Annotated[OperationAuditPageQuery, Depends()],
    session: Annotated[SessionPayload, Depends(get_current_session)],
    service: Annotated[OperationAuditCase, Depends(get_audit_service)],
) -> ApiResponse[PageData[OperationAuditRecord]]:
    return success(
        _map_page(
            await service.my_page(
                OperationAuditPageQueryDto.model_validate(query.model_dump()),
                session.account_id,
            )
        )
    )


@router.get(
    "/v1/portal/sys/audit/my-detail",
    dependencies=[Depends(require_account_type(AccountType.PORTAL))],
    response_model=ApiResponse[OperationAuditRecord],
    response_model_exclude_none=False,
)
async def my_detail(
    query: Annotated[IdQuery, Depends()],
    session: Annotated[SessionPayload, Depends(get_current_session)],
    service: Annotated[OperationAuditCase, Depends(get_audit_service)],
) -> ApiResponse[OperationAuditRecord]:
    return success(
        OperationAuditRecord.model_validate(
            await service.my_detail(query.id, session.account_id)
        )
    )
