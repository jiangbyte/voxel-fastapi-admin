""" Author: Charlie

资源管理 HTTP 路由：资源树、资源模块、按钮与资源权限相关接口。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.iam.iam_schemas import PermissionRegistryItem
from api.iam.resource_schemas import (
    ResourceAdminPageQuery,
    ResourceButtonCreateRequest,
    ResourceButtonPageQuery,
    ResourceButtonSchema,
    ResourceButtonUpdateRequest,
    ResourceCreateRequest,
    ResourceModuleAdminPageQuery,
    ResourceModuleCreateRequest,
    ResourceModuleUpdateRequest,
    ResourcePermissionBindRequest,
    ResourceTreeNode,
    ResourceTreeQuery,
    ResourceUpdateRequest,
    SysResourceModuleSchema,
    SysResourceSchema,
)
from cases.iam.resource.resource_case import (
    ResourceModuleCase,
    ResourceCase,
)
from infrastructure.iam.wiring import (
    get_resource_module_service,
    get_resource_service,
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

router = APIRouter()


@router.post(
    "/v1/admin/iam/resource/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: ResourceCreateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await service.create(payload.model_dump())
    return success()


@router.post(
    "/v1/admin/iam/resource/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: ResourceUpdateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await service.update(payload.model_dump())
    return success()


@router.post(
    "/v1/admin/iam/resource/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await service.delete(payload)
    return success()


@router.get(
    "/v1/admin/iam/resource/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:detail")),
    ],
    response_model=ApiResponse[SysResourceSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[SysResourceSchema]:
    return success(await service.detail(query))


@router.get(
    "/v1/admin/iam/resource/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:page")),
    ],
    response_model=ApiResponse[PageData[SysResourceSchema]],
)
async def page(
    query: Annotated[ResourceAdminPageQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PageData[SysResourceSchema]]:
    return success(await service.page_admin(query.model_dump()))


@router.get(
    "/v1/admin/iam/resource/current",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
    ],
    response_model=ApiResponse[list[SysResourceSchema]],
)
async def current_resources(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[list[SysResourceSchema]]:
    return success(
        await service.list_current_resources(
            session,
            module_client=AccountType.ADMIN,
        )
    )


@router.get(
    "/v1/admin/iam/resource/tree",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:list")),
    ],
    response_model=ApiResponse[list[ResourceTreeNode]],
)
async def list_resource_tree(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[ResourceTreeQuery, Depends()],
) -> ApiResponse[list[ResourceTreeNode]]:
    return success(await service.list_resource_tree(session, query.model_dump()))


@router.post(
    "/v1/admin/resource-permissions",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:grant")),
    ],
    response_model=ApiResponse[None],
)
async def bind_resource_permission(
    payload: ResourcePermissionBindRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.bind_resource_permission(payload.model_dump(), session)
    return success()


@router.get(
    "/v1/admin/iam/permission/registry",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:grant")),
    ],
    response_model=ApiResponse[list[PermissionRegistryItem]],
)
async def permission_registry(
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[list[PermissionRegistryItem]]:
    return success(await service.list_permission_registry_items())


@router.post(
    "/v1/admin/iam/resource-button/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:create")),
    ],
    response_model=ApiResponse[None],
)
async def create_button(
    payload: ResourceButtonCreateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.create_button(payload.model_dump(), session)
    return success()


@router.post(
    "/v1/admin/iam/resource-button/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:update")),
    ],
    response_model=ApiResponse[None],
)
async def update_button(
    payload: ResourceButtonUpdateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    await service.update_button(payload.model_dump(), session)
    return success()


@router.post(
    "/v1/admin/iam/resource-button/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete_button(
    payload: IdsRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await service.delete_button(payload)
    return success()


@router.get(
    "/v1/admin/iam/resource-button/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resource:list")),
    ],
    response_model=ApiResponse[PageData[ResourceButtonSchema]],
)
async def button_page(
    query: Annotated[ResourceButtonPageQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PageData[ResourceButtonSchema]]:
    return success(await service.page_buttons(query.model_dump()))


@router.post(
    "/v1/admin/iam/resource-module/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:create")),
    ],
    response_model=ApiResponse[None],
)
async def create_resource_module(
    payload: ResourceModuleCreateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await module_service.create(payload.model_dump())
    return success()


@router.post(
    "/v1/admin/iam/resource-module/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:update")),
    ],
    response_model=ApiResponse[None],
)
async def update_resource_module(
    payload: ResourceModuleUpdateRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await module_service.update(payload.model_dump())
    return success()


@router.post(
    "/v1/admin/iam/resource-module/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete_resource_module(
    payload: IdsRequest,
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[None]:
    await module_service.delete(payload)
    return success()


@router.get(
    "/v1/admin/iam/resource-module/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:detail")),
    ],
    response_model=ApiResponse[SysResourceModuleSchema],
)
async def resource_module_detail(
    query: Annotated[IdQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[SysResourceModuleSchema]:
    return success(await module_service.detail(query))


@router.get(
    "/v1/admin/iam/resource-module/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:page")),
    ],
    response_model=ApiResponse[PageData[SysResourceModuleSchema]],
)
async def resource_module_page(
    query: Annotated[ResourceModuleAdminPageQuery, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ApiResponse[PageData[SysResourceModuleSchema]]:
    return success(await module_service.page_admin(query.model_dump()))


@router.get(
    "/v1/admin/iam/resource-module/selector",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("iam:resourcemodule:page")),
    ],
    response_model=ApiResponse[list[SysResourceModuleSchema]],
)
async def resource_module_selector(
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[list[SysResourceModuleSchema]]:
    return success(await module_service.selector())
