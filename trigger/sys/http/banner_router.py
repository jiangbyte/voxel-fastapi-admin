"""展示图管理端接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.banner_schemas import (
    BannerAdminPageQuery,
    BannerCreateRequest,
    BannerPublicListQuery,
    BannerUpdateRequest,
    SysBannerSchema,
)
from cases.sys.banner.banner_case import (
    BannerCase,
)
from cases.sys.banner.dto import (
    BannerAdminPageQuery as BannerAdminPageQueryDto,
)
from cases.sys.banner.dto import (
    BannerCreateCommand,
    BannerPublicListQuery as BannerPublicListQueryDto,
    BannerUpdateCommand,
)
from infrastructure.sys.wiring import get_banner_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import require_account_type, require_permission
from voxel_types.schema.base import IdQuery, IdsRequest
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


def _map_page(page: PageData[dict]) -> PageData[SysBannerSchema]:
    return PageData(
        current=page.current,
        size=page.size,
        total=page.total,
        records=[SysBannerSchema.model_validate(r) for r in page.records],
    )


@router.get(
    "/v1/admin/sys/banner/list",
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
    response_model=ApiResponse[list[SysBannerSchema]],
)
async def list_admin_banners(
    query: Annotated[BannerPublicListQuery, Depends()],
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[list[SysBannerSchema]]:
    rows = await service.list_visible(
        BannerPublicListQueryDto.model_validate(query.model_dump()),
        account_type=AccountType.ADMIN,
    )
    return success([SysBannerSchema.model_validate(r) for r in rows])


@router.post(
    "/v1/admin/sys/banner/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:banner:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: BannerCreateRequest,
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[None]:
    await service.create(BannerCreateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/banner/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:banner:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: BannerUpdateRequest,
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[None]:
    await service.update(BannerUpdateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/banner/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:banner:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[None]:
    await service.delete(payload.ids)
    return success()


@router.get(
    "/v1/admin/sys/banner/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:banner:detail")),
    ],
    response_model=ApiResponse[SysBannerSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[SysBannerSchema]:
    return success(SysBannerSchema.model_validate(await service.detail(query.id)))


@router.get(
    "/v1/admin/sys/banner/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:banner:page")),
    ],
    response_model=ApiResponse[PageData[SysBannerSchema]],
)
async def page(
    query: Annotated[BannerAdminPageQuery, Depends()],
    service: Annotated[BannerCase, Depends(get_banner_service)],
) -> ApiResponse[PageData[SysBannerSchema]]:
    return success(
        _map_page(
            await service.page_admin(
                BannerAdminPageQueryDto.model_validate(query.model_dump())
            )
        )
    )
