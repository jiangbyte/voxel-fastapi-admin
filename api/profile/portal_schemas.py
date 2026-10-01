""" Author: Charlie

门户用户中心与公开主页请求/响应模型。
"""

from datetime import datetime

from pydantic import Field

from api.auth.auth_schemas import OptionalStr
from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag
from infrastructure.security.transport import PasswordKeyMixin


class ProfileUserPortalResponse(ApiSchema):
    """门户账户扩展资料响应模型（remark 恒为 null，对齐 voxel-boot 线型）。"""

    account_id: str
    nickname: str | None = None
    avatar: str | None = None
    signature: str | None = None
    remark: str | None = None
    phone: str | None = None
    email: str | None = None
    phone_login_enabled: WireFlag = 0
    email_login_enabled: WireFlag = 0
    created_at: datetime | None = Field(default=None, examples=["2026-06-17T12:00:00Z"])
    updated_at: datetime | None = Field(default=None, examples=["2026-06-17T12:00:00Z"])


class PortalPublicProfileResponse(ApiSchema):
    """门户公开主页资料响应模型。"""

    account_id: str
    nickname: str | None = None
    avatar: str | None = None
    signature: str | None = None


class PortalPublicSpaceQuery(ApiSchema):
    """门户公开主页查询。"""

    account_id: str = Field(min_length=1, max_length=64)


class ProfileUserPortalUpsertPayload(ApiSchema):
    """门户账户资料写入载荷。"""

    account_id: str
    nickname: str | None = None
    avatar: str | None = None
    signature: str | None = None
    phone: str | None = None
    email: str | None = None


class PortalUserCenterProfileUpdateRequest(ApiSchema):
    """当前门户用户个人资料更新请求。"""

    nickname: str | None = Field(default=None, max_length=64)
    avatar: str | None = None
    signature: str | None = None
    remark: str | None = None


class PortalUserCenterPasswordUpdateRequest(PasswordKeyMixin):
    """当前门户用户修改密码请求。"""

    old_password: OptionalStr = Field(default=None, min_length=1, max_length=512)
    new_password: str = Field(min_length=1, max_length=512)
    otp_code: OptionalStr = Field(default=None, min_length=4, max_length=16)


class PortalUserCenterPhoneUpdateRequest(PasswordKeyMixin):
    """当前门户用户手机号绑定更新请求。"""

    password: str = Field(min_length=1, max_length=512)
    phone: str | None = Field(default=None, max_length=32)
    phone_login_enabled: WireFlag = 0
    otp_code: OptionalStr = Field(default=None, min_length=4, max_length=16)


class PortalUserCenterEmailUpdateRequest(PasswordKeyMixin):
    """当前门户用户邮箱绑定更新请求。"""

    password: str = Field(min_length=1, max_length=512)
    email: str | None = Field(default=None, max_length=128)
    email_login_enabled: WireFlag = 0
    otp_code: OptionalStr = Field(default=None, min_length=4, max_length=16)


class PortalUserCenterAvatarUpdateResponse(ApiSchema):
    """当前门户用户头像更新响应。"""

    avatar: str
    file_id: str
    object_name: str
    url: str
