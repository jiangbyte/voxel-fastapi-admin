""" Author: Charlie

账户资料公共响应模型：管理端与门户端的「我的信息」响应。
"""


from pydantic import Field

from api.profile.admin_schemas import ProfileUserAdminResponse
from api.profile.identity_schemas import IdentityStatusResponse
from api.profile.portal_schemas import (
    ProfileUserPortalResponse,
)
from infrastructure.config.enums import AccountType
from voxel_types.schema.base import ApiSchema
from voxel_types.schema.common_schema import IdNameResponse
from voxel_types.schema.wire import WireFlag


class BindTargetRequest(ApiSchema):
    """发送绑定验证码的目标地址（邮箱或手机号）。"""

    target: str = Field(min_length=3, max_length=128)


class AdminMeResponse(ApiSchema):
    """管理端当前登录账户信息响应模型。"""

    account_id: str
    account: str
    account_type: AccountType
    nickname: str | None = None
    avatar: str | None = None
    role_ids: list[str]
    dept_ids: list[str]
    group_ids: list[str]
    role_id_names: list[IdNameResponse] = Field(default_factory=list)
    dept_id_names: list[IdNameResponse] = Field(default_factory=list)
    group_id_names: list[IdNameResponse] = Field(default_factory=list)
    permission_keys: list[str]
    password_expired: WireFlag = 0
    force_bind_email: WireFlag = 0
    force_bind_phone: WireFlag = 0
    force_bind_identity: WireFlag = 0
    identity: IdentityStatusResponse | None = None
    profile: ProfileUserAdminResponse


class PortalMeResponse(ApiSchema):
    """门户端当前登录账户信息响应模型。"""

    account_id: str
    account: str
    account_type: AccountType
    nickname: str | None = None
    avatar: str | None = None
    role_ids: list[str] = Field(default_factory=list)
    dept_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
    role_id_names: list[IdNameResponse] = Field(default_factory=list)
    dept_id_names: list[IdNameResponse] = Field(default_factory=list)
    group_id_names: list[IdNameResponse] = Field(default_factory=list)
    permission_keys: list[str] = Field(default_factory=list)
    password_expired: WireFlag = 0
    force_bind_email: WireFlag = 0
    force_bind_phone: WireFlag = 0
    force_bind_identity: WireFlag = 0
    identity: IdentityStatusResponse | None = None
    profile: ProfileUserPortalResponse
