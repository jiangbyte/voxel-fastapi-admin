"""Author: Charlie

认证应用层命令/结果模型（与 HTTP api schema 解耦）。
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from domain.iam.enums import AccountIdentityType
from infrastructure.config.enums import AccountType
from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag, WireInt


class LoginPayload(ApiSchema):
    """登录用例载荷。"""

    account: str
    password: str | None = None
    account_type: AccountType
    identity_type: AccountIdentityType = AccountIdentityType.ACCOUNT
    login_mode: str = "PASSWORD"
    otp_code: str | None = None
    remember_me: WireFlag = 1
    client_ip: str | None = None
    user_agent: str | None = None
    device_label: str | None = None


class LoginResult(ApiSchema):
    """登录成功结果。"""

    token: str | None = None
    account_id: str | None = None
    account_type: AccountType | None = None
    password_expired: WireFlag = 0
    password_expiry_warning_days: WireInt | None = None
    expires_in: WireInt | None = None
    force_bind_email: WireFlag = 0
    force_bind_phone: WireFlag = 0


class RegisterCommand(ApiSchema):
    """门户注册命令。"""

    register_channel: Literal["ACCOUNT", "EMAIL", "PHONE"]
    account: str | None = None
    password: str
    email: str | None = None
    phone: str | None = None
    otp_code: str | None = None


class RegisterResult(ApiSchema):
    """注册成功结果。"""

    account_id: str
    account: str
    account_type: AccountType


class ForgotPasswordCommand(ApiSchema):
    email: str


class ResetPasswordCommand(ApiSchema):
    token: str
    password: str


class ForgotPasswordByPhoneCommand(ApiSchema):
    phone: str


class ResetPasswordByPhoneCommand(ApiSchema):
    phone: str
    otp_code: str
    password: str


class CancelAccountCommand(ApiSchema):
    cancel_reason: str | None = Field(default=None, max_length=500)
