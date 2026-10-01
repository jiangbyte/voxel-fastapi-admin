""" Author: Charlie

系统字典管理端接口：字典增删改查、分页与树形查询。
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.dict_schemas import (
    DictAdminPageQuery,
    DictCreateRequest,
    DictIdQuery,
    DictIdsRequest,
    DictTreeQuery,
    DictUpdateRequest,
    SysDictSchema,
    SysDictTreeNode,
)
from cases.sys.dict.dict_case import (
    DictCase,
    build_tree_nodes_from_records,
)
from cases.sys.dict.dto import (
    DictAdminPageQuery as DictAdminPageQueryDto,
)
from cases.sys.dict.dto import (
    DictCreateCommand,
    DictIdQuery as DictIdQueryDto,
    DictIdsCommand,
    DictTreeQuery as DictTreeQueryDto,
    DictUpdateCommand,
)
from infrastructure.sys.wiring import get_dict_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import require_account_type, require_permission
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.post(
    "/v1/admin/sys/dict/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:dict:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: DictCreateRequest,
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[None]:
    """新增字典。"""
    await service.create(DictCreateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/dict/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:dict:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: DictUpdateRequest,
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[None]:
    """更新字典。"""
    await service.update(DictUpdateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/dict/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:dict:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: DictIdsRequest,
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[None]:
    """批量删除字典。"""
    await service.delete(DictIdsCommand(ids=list(payload.ids)))
    return success()


@router.get(
    "/v1/admin/sys/dict/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:dict:detail")),
    ],
    response_model=ApiResponse[SysDictSchema],
)
async def get(
    query: Annotated[DictIdQuery, Depends()],
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[SysDictSchema]:
    """查询字典详情。"""
    row = await service.get(DictIdQueryDto(id=query.id))
    return success(SysDictSchema.model_validate(row))


@router.get(
    "/v1/admin/sys/dict/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:dict:page")),
    ],
    response_model=ApiResponse[PageData[SysDictSchema]],
)
async def page(
    query: Annotated[DictAdminPageQuery, Depends()],
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[PageData[SysDictSchema]]:
    """分页查询字典。"""
    page_data = await service.page_admin(
        DictAdminPageQueryDto.model_validate(query.model_dump())
    )
    records = [SysDictSchema.model_validate(row) for row in page_data.records]
    return success(
        PageData(
            size=page_data.size,
            current=page_data.current,
            total=page_data.total,
            pages=page_data.pages,
            records=records,
        )
    )


@router.get(
    "/v1/admin/sys/dict/tree",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
    ],
    response_model=ApiResponse[list[SysDictTreeNode]],
)
async def tree(
    query: Annotated[DictTreeQuery, Depends()],
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[list[SysDictTreeNode]]:
    """查询字典树。"""
    records = build_tree_nodes_from_records(
        await service.list_tree(DictTreeQueryDto.model_validate(query.model_dump()))
    )
    return success([SysDictTreeNode.model_validate(node) for node in records])
