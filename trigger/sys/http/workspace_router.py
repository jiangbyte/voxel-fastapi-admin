"""工作台 API。"""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.sys.workspace_schemas import (
    WorkspaceOverviewResponse,
    WorkspaceShortcutResult,
    WorkspaceShortcutSaveRequest,
)
from cases.sys.workspace.dto import WorkspaceShortcutSaveCommand
from cases.sys.workspace.workspace_case import (
    WorkspaceCase,
)
from infrastructure.sys.wiring import get_workspace_service
from infrastructure.config.enums import AccountType
from infrastructure.deps.auth import get_current_session, require_account_type
from infrastructure.security.session import SessionPayload
from infrastructure.web.schema import ApiResponse, success

router = APIRouter()


@router.get(
    "/v1/admin/sys/workspace/overview",
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
    response_model=ApiResponse[WorkspaceOverviewResponse],
)
async def overview(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    service: Annotated[WorkspaceCase, Depends(get_workspace_service)],
) -> ApiResponse[WorkspaceOverviewResponse]:
    return success(
        WorkspaceOverviewResponse.model_validate(await service.overview(session))
    )


@router.get(
    "/v1/admin/sys/workspace/shortcuts",
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
    response_model=ApiResponse[list[WorkspaceShortcutResult]],
)
async def list_shortcuts(
    session: Annotated[SessionPayload, Depends(get_current_session)],
    service: Annotated[WorkspaceCase, Depends(get_workspace_service)],
) -> ApiResponse[list[WorkspaceShortcutResult]]:
    rows = await service.list_shortcuts(session)
    return success([WorkspaceShortcutResult.model_validate(r) for r in rows])


@router.post(
    "/v1/admin/sys/workspace/shortcuts",
    dependencies=[Depends(require_account_type(AccountType.ADMIN))],
    response_model=ApiResponse[list[WorkspaceShortcutResult]],
)
async def save_shortcuts(
    payload: WorkspaceShortcutSaveRequest,
    session: Annotated[SessionPayload, Depends(get_current_session)],
    service: Annotated[WorkspaceCase, Depends(get_workspace_service)],
) -> ApiResponse[list[WorkspaceShortcutResult]]:
    rows = await service.replace_shortcuts(
        session,
        WorkspaceShortcutSaveCommand.model_validate(payload.model_dump()),
    )
    return success([WorkspaceShortcutResult.model_validate(r) for r in rows])
