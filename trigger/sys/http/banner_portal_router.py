"""展示图公开端接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.banner_schemas import (
    BannerPublicListQuery,
    SysBannerSchema,
)
from cases.sys.banner.banner_case import (
    BannerCase,
)
from cases.sys.banner.dto import (
    BannerPublicListQuery as BannerPublicListQueryDto,
)
from infrastructure.sys.wiring import get_banner_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import get_optional_session
from voxel_types.schema.base import IdQuery
from infrastructure.security.session import SessionPayload
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.get("/v1/portal/sys/banner/list", response_model=ApiResponse[list[SysBannerSchema]])
async def list_public_banners(
    query: Annotated[BannerPublicListQuery, Depends()],
    service: Annotated[BannerCase, Depends(get_banner_service)],
    session: Annotated[SessionPayload | None, Depends(get_optional_session)] = None,
) -> ApiResponse[list[SysBannerSchema]]:
    account_type = AccountType(session.account_type) if session else AccountType.PORTAL
    rows = await service.list_visible(
        BannerPublicListQueryDto.model_validate(query.model_dump()),
        account_type=account_type,
    )
    return success([SysBannerSchema.model_validate(r) for r in rows])


@router.post("/v1/portal/sys/banner/interaction", response_model=ApiResponse[None])
async def record_banner_interaction(
    payload: IdQuery,
    service: Annotated[BannerCase, Depends(get_banner_service)],
    session: Annotated[SessionPayload | None, Depends(get_optional_session)] = None,
) -> ApiResponse[None]:
    account_type = AccountType(session.account_type) if session else AccountType.PORTAL
    await service.record_interaction(payload.id, account_type=account_type)
    return success()
