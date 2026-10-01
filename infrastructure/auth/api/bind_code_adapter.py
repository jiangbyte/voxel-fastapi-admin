"""Author: Charlie

AuthBindCodePort 适配器：委托 AuthCase 绑定验证码能力。
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from cases.auth.api.bind_code_port import AuthBindCodePort
from infrastructure.config.enums import AccountType


class AuthBindCodeAdapter:
    """将 AuthCase 适配为跨上下文绑定验证码端口。"""

    def __init__(self, auth_service) -> None:
        self._auth = auth_service

    async def send_bind_code(
        self,
        *,
        account_type: AccountType,
        channel: str,
        target: str,
        account_id: str,
    ) -> None:
        await self._auth.send_bind_code(
            account_type=account_type,
            channel=channel,
            target=target,
            account_id=account_id,
        )

    async def consume_bind_code(
        self,
        *,
        account_type: AccountType,
        channel: str,
        account_id: str,
        target: str,
        code: str | None,
    ) -> None:
        await self._auth.consume_bind_code(
            account_type=account_type,
            channel=channel,
            account_id=account_id,
            target=target,
            code=code,
        )


def get_bind_code_port(db: AsyncSession) -> AuthBindCodePort:
    # 延迟导入，避免 auth.wiring ↔ profile.wiring 循环依赖
    from infrastructure.auth.wiring import build_auth_service

    return AuthBindCodeAdapter(build_auth_service(db))
