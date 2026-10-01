"""角色管理 HTTP 路由：Schema ↔ Command。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.iam.role_schemas import (
    RoleAdminPageQuery,
    RoleCreateRequest,
    RoleGrantClientResourceRequest,
    RoleGrantResourceRequest,
    RoleGrantUserRequest,
    RoleOwnClientResourceQuery,
    RoleOwnClientResourceResponse,
    RoleOwnResourceQuery,
    RoleOwnResourceResponse,
    RoleOwnUserResponse,
    RoleUpdateRequest,
    SysRoleSchema,
)
from cases.iam.role.dto import (
    RoleCreateCommand,
    RoleGrantClientResourceCommand,
    RoleGrantResourceCommand,
    RoleGrantUserCommand,
    RoleOwnClientResourceQuery as RoleOwnClientResourceQueryCmd,
    RoleOwnResourceQuery as RoleOwnResourceQueryCmd,
    RolePageQuery,
    RoleUpdateCommand,
)
from cases.iam.role.role_case import RoleCase
from infrastructure.iam.wiring import get_role_service
from trigger.iam.assembler.account_assembler import AccountAssembler
from trigger.iam.assembler.role_assembler import (
    to_own_client_resource,
    to_own_resource,
    to_own_user,
    to_role_page,
    to_role_schema,
)
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import (
    get_current_session,
    require_account_type,
    require_permission,
)
from infrastructure.deps.db import get_db_session
from voxel_types.schema.base import IdQuery, IdsRequest
from infrastructure.security.session import SessionPayload
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/v1/admin/iam/role/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: RoleCreateRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.create(RoleCreateCommand.model_validate(payload.model_dump()), session=session)
    return success()


@router.post(
    "/v1/admin/iam/role/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: RoleUpdateRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.update(RoleUpdateCommand.model_validate(payload.model_dump()), session=session)
    return success()


@router.post(
    "/v1/admin/iam/role/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.delete(payload, session)
    return success()


@router.get(
    "/v1/admin/iam/role/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:detail")),
    ],
    response_model=ApiResponse[SysRoleSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[SysRoleSchema]:
    row = await service.detail(query, session)
    return success(to_role_schema(row))


@router.get(
    "/v1/admin/iam/role/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:page")),
    ],
    response_model=ApiResponse[PageData[SysRoleSchema]],
)
async def page(
    query: Annotated[RoleAdminPageQuery, Depends()],
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[PageData[SysRoleSchema]]:
    page_query = RolePageQuery.model_validate(query.model_dump())
    data = await service.page_admin(page_query, session)
    return success(to_role_page(data))


@router.get(
    "/v1/admin/iam/role/own-resource",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:ownresource")),
    ],
    response_model=ApiResponse[RoleOwnResourceResponse],
    summary="获取角色拥有资源",
)
async def own_resource(
    query: Annotated[RoleOwnResourceQuery, Depends()],
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[RoleOwnResourceResponse]:
    cmd = RoleOwnResourceQueryCmd.model_validate(query.model_dump())
    return success(to_own_resource(await service.own_resource(cmd, session)))


@router.post(
    "/v1/admin/iam/role/grant-resource",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:grantresource")),
    ],
    response_model=ApiResponse[None],
    summary="给角色授权资源",
)
async def grant_resource(
    payload: RoleGrantResourceRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.grant_resource(
        RoleGrantResourceCommand.model_validate(payload.model_dump()),
        session,
    )
    return success()


@router.get(
    "/v1/admin/iam/role/own-client-resource",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:ownclientresource")),
    ],
    response_model=ApiResponse[RoleOwnClientResourceResponse],
    summary="获取角色拥有客户端资源",
)
async def own_client_resource(
    query: Annotated[RoleOwnClientResourceQuery, Depends()],
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[RoleOwnClientResourceResponse]:
    cmd = RoleOwnClientResourceQueryCmd.model_validate(query.model_dump())
    return success(to_own_client_resource(await service.own_client_resource(cmd, session)))


@router.post(
    "/v1/admin/iam/role/grant-client-resource",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:grantclientresource")),
    ],
    response_model=ApiResponse[None],
    summary="给角色授权客户端资源",
)
async def grant_client_resource(
    payload: RoleGrantClientResourceRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.grant_client_resource(
        RoleGrantClientResourceCommand.model_validate(payload.model_dump()),
        session,
    )
    return success()


@router.get(
    "/v1/admin/iam/role/own-user",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:ownuser")),
    ],
    response_model=ApiResponse[RoleOwnUserResponse],
    summary="获取角色拥有用户",
)
async def own_user(
    query: Annotated[IdQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[RoleOwnUserResponse]:
    view = await service.own_user(query, session)
    return success(await to_own_user(AccountAssembler(db), view))


@router.post(
    "/v1/admin/iam/role/grant-user",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:role:grantuser")),
    ],
    response_model=ApiResponse[None],
    summary="给角色授权用户",
)
async def grant_user(
    payload: RoleGrantUserRequest,
    service: Annotated[RoleCase, Depends(get_role_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.grant_user(
        RoleGrantUserCommand.model_validate(payload.model_dump()),
        session,
    )
    return success()
