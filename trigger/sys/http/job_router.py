"""定时任务管理端接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.job_schemas import (
    JobAdminPageQuery,
    JobCreateRequest,
    JobEnabledRequest,
    JobLogAdminPageQuery,
    JobUpdateRequest,
    SysJobLogSchema,
    SysJobSchema,
)
from cases.sys.job.dto import (
    JobAdminPageQuery as JobAdminPageQueryDto,
    JobCreateCommand,
    JobEnabledCommand,
    JobLogAdminPageQuery as JobLogAdminPageQueryDto,
    JobUpdateCommand,
)
from cases.sys.job.job_case import JobCase
from infrastructure.sys.wiring import get_job_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import (
    get_current_account,
    require_account_type,
    require_permission,
)
from voxel_types.schema.base import IdQuery, IdsRequest
from infrastructure.web.pagination import PageData
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


def _map_job_page(page: PageData[dict]) -> PageData[SysJobSchema]:
    return PageData(
        current=page.current,
        size=page.size,
        total=page.total,
        records=[SysJobSchema.model_validate(r) for r in page.records],
    )


def _map_log_page(page: PageData[dict]) -> PageData[SysJobLogSchema]:
    return PageData(
        current=page.current,
        size=page.size,
        total=page.total,
        records=[SysJobLogSchema.model_validate(r) for r in page.records],
    )


@router.get(
    "/v1/admin/sys/job/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:page")),
    ],
    response_model=ApiResponse[PageData[SysJobSchema]],
)
async def page(
    query: Annotated[JobAdminPageQuery, Depends()],
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[PageData[SysJobSchema]]:
    return success(
        _map_job_page(
            await service.page_admin(
                JobAdminPageQueryDto.model_validate(query.model_dump())
            )
        )
    )


@router.get(
    "/v1/admin/sys/job/detail",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:detail")),
    ],
    response_model=ApiResponse[SysJobSchema],
)
async def detail(
    query: Annotated[IdQuery, Depends()],
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[SysJobSchema]:
    return success(SysJobSchema.model_validate(await service.detail(query.id)))


@router.post(
    "/v1/admin/sys/job/create",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:create")),
    ],
    response_model=ApiResponse[None],
)
async def create(
    payload: JobCreateRequest,
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[None]:
    await service.create(JobCreateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/job/update",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:update")),
    ],
    response_model=ApiResponse[None],
)
async def update(
    payload: JobUpdateRequest,
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[None]:
    await service.update(JobUpdateCommand.model_validate(payload.model_dump()))
    return success()


@router.post(
    "/v1/admin/sys/job/delete",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:delete")),
    ],
    response_model=ApiResponse[None],
)
async def delete(
    payload: IdsRequest,
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[None]:
    await service.delete(payload.ids)
    return success()


@router.post(
    "/v1/admin/sys/job/enabled",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:update")),
    ],
    response_model=ApiResponse[None],
)
async def enabled(
    payload: JobEnabledRequest,
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[None]:
    await service.update_enabled(
        JobEnabledCommand.model_validate(payload.model_dump())
    )
    return success()


@router.post(
    "/v1/admin/sys/job/run",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:job:run")),
    ],
    response_model=ApiResponse[None],
)
async def run(
    payload: IdQuery,
    service: Annotated[JobCase, Depends(get_job_service)],
    account=Depends(get_current_account),
) -> ApiResponse[None]:
    await service.run_now(payload.id, executor=str(account.id))
    return success()


@router.get(
    "/v1/admin/sys/job-log/page",
    dependencies=[
        Depends(require_account_type(AccountType.ADMIN)),
        Depends(require_permission("sys:joblog:page")),
    ],
    response_model=ApiResponse[PageData[SysJobLogSchema]],
)
async def log_page(
    query: Annotated[JobLogAdminPageQuery, Depends()],
    service: Annotated[JobCase, Depends(get_job_service)],
) -> ApiResponse[PageData[SysJobLogSchema]]:
    return success(
        _map_log_page(
            await service.page_logs(
                JobLogAdminPageQueryDto.model_validate(query.model_dump())
            )
        )
    )
