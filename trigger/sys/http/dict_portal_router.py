""" Author: Charlie

系统字典公开端接口：树形查询。
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.dict_schemas import DictTreeQuery, SysDictTreeNode
from cases.sys.dict.dict_case import (
    DictCase,
    build_tree_nodes_from_records,
)
from cases.sys.dict.dto import DictTreeQuery as DictTreeQueryDto
from infrastructure.sys.wiring import get_dict_service
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.get(
    "/v1/portal/sys/dict/tree",
    response_model=ApiResponse[list[SysDictTreeNode]],
)
async def tree(
    query: Annotated[DictTreeQuery, Depends()],
    service: Annotated[DictCase, Depends(get_dict_service)],
) -> ApiResponse[list[SysDictTreeNode]]:
    """公开端按分类查询字典树。"""
    records = build_tree_nodes_from_records(
        await service.list_tree(DictTreeQueryDto.model_validate(query.model_dump()))
    )
    return success([SysDictTreeNode.model_validate(node) for node in records])
