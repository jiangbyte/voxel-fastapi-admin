""" Author: Charlie

门户资源 HTTP 路由：向 Portal 端公开当前可见资源。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.iam.resource_schemas import SysResourceSchema
from cases.iam.resource.resource_case import (
    ResourceCase,
)
from infrastructure.iam.wiring import get_resource_service
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.get(
    "/v1/portal/iam/resource/current",
    response_model=ApiResponse[list[SysResourceSchema]],
)
async def current_resources(
    service: Annotated[ResourceCase, Depends(get_resource_service)],
) -> ApiResponse[list[SysResourceSchema]]:
    return success(await service.list_public_portal_resources())
