"""Author: Charlie

OAuth 应用层结果模型（与 HTTP api schema 解耦）。
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag


class OauthBindingResult(ApiSchema):
    provider: str
    label: str
    open_id_masked: str
    nickname: str | None = None
    avatar: str | None = None
    bound_at: datetime | None = None


class OauthProviderOptionResult(ApiSchema):
    provider: str
    label: str
    enabled: WireFlag = 0
    web_oauth: WireFlag = 1
