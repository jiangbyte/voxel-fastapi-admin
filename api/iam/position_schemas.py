""" Author: Charlie

职位 Schema：职位创建/更新/分页查询及响应结构。
"""

from datetime import datetime

from pydantic import Field

from infrastructure.config.enums import StatusEnum
from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag, WireInt
from infrastructure.web.pagination import PageQuery


class PositionCreateRequest(ApiSchema):
    """创建职位请求。"""

    name: str = Field(min_length=1, max_length=64)
    category: str = Field(min_length=1, max_length=32)
    owner_dept_id: str | None = Field(default=None, max_length=64)
    sort: WireInt = 99
    is_virtual: WireFlag = 0
    status: StatusEnum = StatusEnum.ENABLED
    description: str | None = None
    extra: dict = Field(default_factory=dict)


class PositionUpdateRequest(PositionCreateRequest):
    """更新职位请求。"""

    id: str = Field(min_length=1, max_length=64)


class PositionAdminPageQuery(PageQuery):
    """职位管理端分页查询条件。"""

    name: str | None = Field(default=None, max_length=64)
    category: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=32)


class SysPositionSchema(ApiSchema):
    """职位响应结构。"""

    id: str
    name: str
    category: str
    owner_dept_id: str | None = None
    sort: WireInt
    is_virtual: WireFlag
    status: str
    description: str | None = None
    extra: dict
    created_at: datetime
    created_by: str | None = None
    updated_at: datetime
    updated_by: str | None = None