"""Author: Charlie

职位管理 HTTP 路由：Schema ↔ Command，经 wiring 注入服务。
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.iam.position_schemas import (
    PositionAdminPageQuery,
    PositionCreateRequest,
    PositionUpdateRequest,
    SysPositionSchema,
)
from cases.iam.position.dto import (
    PositionCreateCommand,
    PositionPageQuery,
    PositionUpdateCommand,
)
from cases.iam.position.position_case import (
    PositionCase,
)
from infrastructure.iam.wiring import get_position_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import (
    get_current_session,
    require_account_type,
    require_permission,
)
from voxel_types.schema.base import IdQuery, IdsRequest, to_schema, to_schema_list
from infrastructure.security.session import SessionPayload
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.post(
    "/v1/admin/iam/position/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:position:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: PositionCreateRequest,
    service: Annotated[PositionCase, Depends(get_position_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.create(
        PositionCreateCommand.model_validate(payload.model_dump()),
        session=session,
    )
    return success()


@router.post(
    "/v1/admin/iam/position/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:position:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: PositionUpdateRequest,
    service: Annotated[PositionCase, Depends(get_position_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.update(
        PositionUpdateCommand.model_validate(payload.model_dump()),
        session=session,
    )
    return success()


@router.post(
    "/v1/admin/iam/position/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:position:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[PositionCase, Depends(get_position_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.delete(payload, session=session)
    return success()


@router.get(
    "/v1/admin/iam/position/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:position:detail")),
    ],
    response_model=ApiResponse[SysPositionSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    service: Annotated[PositionCase, Depends(get_position_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[SysPositionSchema]:
    row = await service.detail(query, session=session)
    return success(to_schema(SysPositionSchema, row))


@router.get(
    "/v1/admin/iam/position/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:position:page")),
    ],
    response_model=ApiResponse[PageData[SysPositionSchema]],
)
async def page(
    query: Annotated[PositionAdminPageQuery, Depends()],
    service: Annotated[PositionCase, Depends(get_position_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[PageData[SysPositionSchema]]:
    page_data = await service.page_admin(
        PositionPageQuery.model_validate(query.model_dump()),
        session=session,
    )
    return success(
        PageData(
            records=to_schema_list(SysPositionSchema, page_data.records),
            total=page_data.total,
            current=page_data.current,
            size=page_data.size,
        )
    )
