""" Author: Charlie

消息通知路由：管理端消息管理接口，及动态注册的当前用户消息接口。
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.notice_schemas import (
    MyNoticePageQuery,
    NoticeReadRequest,
    PinNoticeRequest,
    SysNoticeAdminPageQuery,
    SysNoticeCreateRequest,
    SysNoticeSchema,
    SysNoticeUpdateRequest,
)
from cases.sys.notice.dto import (
    MyNoticePageQuery as MyNoticePageQueryDto,
    NoticeAdminPageQuery,
    NoticeCreateCommand,
    NoticeReadCommand,
    NoticeUpdateCommand,
    PinNoticeCommand,
)
from cases.sys.notice.notice_case import (
    SysNoticeCase,
)
from infrastructure.sys.wiring import get_notice_service
from infrastructure.config.enums import AccountType, account_type_url_segment
from infrastructure.deps.auth import (
    get_current_session,
    require_account_type,
    require_permission,
)
from voxel_types.schema.base import IdQuery, IdsRequest
from voxel_types.schema.wire import WireInt
from infrastructure.security.session import SessionPayload
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

admin_router = APIRouter()


def _map_page(page_data: PageData[dict]) -> PageData[SysNoticeSchema]:
    records = [SysNoticeSchema.model_validate(row) for row in page_data.records]
    return PageData(
        size=page_data.size,
        current=page_data.current,
        total=page_data.total,
        pages=page_data.pages,
        records=records,
    )


@admin_router.post(
    "/v1/admin/sys/notice/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: SysNoticeCreateRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[None]:
    """管理端创建消息。"""
    await service.create(NoticeCreateCommand.model_validate(payload.model_dump()))
    return success()


@admin_router.post(
    "/v1/admin/sys/notice/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: SysNoticeUpdateRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[None]:
    """管理端更新消息。"""
    await service.update(NoticeUpdateCommand.model_validate(payload.model_dump()))
    return success()


@admin_router.post(
    "/v1/admin/sys/notice/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[None]:
    """管理端批量删除消息。"""
    await service.delete(list(payload.ids))
    return success()


@admin_router.get(
    "/v1/admin/sys/notice/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:detail")),
    ],
    response_model=ApiResponse[SysNoticeSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[SysNoticeSchema]:
    """管理端查询消息详情。"""
    return success(SysNoticeSchema.model_validate(await service.detail(query.id)))


@admin_router.get(
    "/v1/admin/sys/notice/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:page")),
    ],
    response_model=ApiResponse[PageData[SysNoticeSchema]],
)
async def page(
    query: Annotated[SysNoticeAdminPageQuery, Depends()],
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[PageData[SysNoticeSchema]]:
    """管理端分页查询消息。"""
    page_data = await service.page_admin(
        NoticeAdminPageQuery.model_validate(query.model_dump())
    )
    return success(_map_page(page_data))


@admin_router.post(
    "/v1/admin/sys/notice/publish",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:publish")),
    ],
    response_model=ApiResponse[None],
)
async def publish(
    payload: IdsRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    session: Annotated[SessionPayload, Depends(get_current_session)],
) -> ApiResponse[None]:
    """管理端发布消息。"""
    await service.publish(list(payload.ids), session)
    return success()


@admin_router.post(
    "/v1/admin/sys/notice/revoke",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:revoke")),
    ],
    response_model=ApiResponse[None],
)
async def revoke(
    payload: IdsRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[None]:
    """管理端撤回消息。"""
    await service.revoke(list(payload.ids))
    return success()


@admin_router.post(
    "/v1/admin/sys/notice/pin",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:notice:pin")),
    ],
    response_model=ApiResponse[None],
)
async def pin(
    payload: PinNoticeRequest,
    service: Annotated[SysNoticeCase, Depends(get_notice_service)],
) -> ApiResponse[None]:
    """管理端置顶/取消置顶公告。"""
    await service.pin(PinNoticeCommand.model_validate(payload.model_dump()))
    return success()


def register_current_user_routes(router: APIRouter, account_type: AccountType) -> None:
    """为指定账户类型动态注册「我的消息」相关路由。"""
    base = f"/v1/{account_type_url_segment(account_type)}/sys/notice"
    deps = [Depends(require_account_type(account_type))]

    @router.get(
        f"{base}/my-page",
        dependencies=deps,
        response_model=ApiResponse[PageData[SysNoticeSchema]],
    )
    async def my_page(
        session: Annotated[SessionPayload, Depends(get_current_session)],
        query: Annotated[MyNoticePageQuery, Depends()],
        service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    ) -> ApiResponse[PageData[SysNoticeSchema]]:
        """当前用户分页查询可见消息。"""
        page_data = await service.page_my(
            MyNoticePageQueryDto.model_validate(query.model_dump()), session
        )
        return success(_map_page(page_data))

    @router.get(
        f"{base}/my-detail",
        dependencies=deps,
        response_model=ApiResponse[SysNoticeSchema],
    )
    async def my_detail(
        query: Annotated[IdQuery, Depends()],
        session: Annotated[SessionPayload, Depends(get_current_session)],
        service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    ) -> ApiResponse[SysNoticeSchema]:
        """当前用户查询消息详情。"""
        row = await service.my_detail(query.id, session)
        return success(SysNoticeSchema.model_validate(row))

    @router.get(
        f"{base}/unread-count",
        dependencies=deps,
        response_model=ApiResponse[WireInt],
    )
    async def unread_count(
        session: Annotated[SessionPayload, Depends(get_current_session)],
        service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    ) -> ApiResponse[WireInt]:
        """当前用户未读消息数。"""
        return success(await service.count_unread(session))

    @router.post(
        f"{base}/read",
        dependencies=deps,
        response_model=ApiResponse[None],
    )
    async def read(
        payload: NoticeReadRequest,
        session: Annotated[SessionPayload, Depends(get_current_session)],
        service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    ) -> ApiResponse[None]:
        """当前用户标记指定消息为已读。"""
        await service.mark_read(
            NoticeReadCommand(ids=[str(i) for i in payload.ids]), session
        )
        return success()

    @router.post(
        f"{base}/read-all",
        dependencies=deps,
        response_model=ApiResponse[None],
    )
    async def read_all(
        session: Annotated[SessionPayload, Depends(get_current_session)],
        service: Annotated[SysNoticeCase, Depends(get_notice_service)],
    ) -> ApiResponse[None]:
        """当前用户标记全部消息为已读。"""
        await service.mark_all_read(session)
        return success()


register_current_user_routes(admin_router, AccountType.ADMIN)
