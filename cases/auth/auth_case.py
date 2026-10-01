""" Author: Charlie

认证应用服务门面：按登录、注册、绑定、重置、生命周期拆分 mixin，对外仍暴露 AuthCase。
"""

from cases.auth.base import AuthServiceBase
from cases.auth.base import _audit_record as _audit_record
from cases.auth.base import session_expires_in as session_expires_in
from cases.auth.bind_service import BindCodeMixin
from cases.auth.lifecycle_service import LifecycleMixin
from cases.auth.login_service import LoginMixin
from cases.auth.password_reset_service import PasswordResetMixin
from cases.auth.register_service import RegisterMixin


class AuthCase(
    LoginMixin,
    RegisterMixin,
    BindCodeMixin,
    PasswordResetMixin,
    LifecycleMixin,
    AuthServiceBase,
):
    """认证服务门面；由 `auth.infrastructure.wiring.build_auth_service` 装配依赖。"""


__all__ = ["AuthCase", "session_expires_in", "_audit_record"]
