"""Author: Charlie

账户读侧组装：返回 dict 视图，不依赖 api / infrastructure。
"""

from __future__ import annotations

from domain.iam.account.repository import AccountRepository
from domain.iam.enums import AccountIdentityBindStatus
from cases.profile.api.profile_read_port import ProfileReadPort
from infrastructure.config.enums import AccountType


class AccountReadService:
    """合并账户、登录标识与资料为统一 dict 视图。"""

    def __init__(self, repo: AccountRepository, profile_read: ProfileReadPort):
        self.repo = repo
        self.profile_read = profile_read

    async def build_account_views(self, accounts: list[dict], *, full: bool = True) -> list[dict]:
        """批量组装账户详情/列表/选择器视图。"""
        if not accounts:
            return []
        account_ids = [str(a["id"]) for a in accounts]
        identities = await self.repo.list_identities_by_account_ids(account_ids)
        admin_profiles = await self.profile_read.list_admin_by_account_ids(account_ids)
        portal_profiles = await self.profile_read.list_portal_by_account_ids(account_ids)
        identity_map: dict[str, list[dict]] = {}
        for identity in identities:
            identity_map.setdefault(str(identity["account_id"]), []).append(identity)
        admin_map = {str(p["account_id"]): p for p in admin_profiles}
        portal_map = {str(p["account_id"]): p for p in portal_profiles}

        items: list[dict] = []
        for account in accounts:
            account_id = str(account["id"])
            account_identities = identity_map.get(account_id, [])
            primary_identity = _primary_account_identity(account_identities)
            profile = _pick_profile(account, admin_map, portal_map)
            email_identity, phone_identity = _email_phone_identities(account_identities)
            view = {
                **account,
                "account": (primary_identity or {}).get("identifier", ""),
                "nickname": (profile or {}).get("nickname"),
                "avatar": (profile or {}).get("avatar"),
                "signature": (profile or {}).get("signature"),
                "phone": (profile or {}).get("phone"),
                "email": (profile or {}).get("email"),
                "bio": (profile or {}).get("bio"),
                "level": (profile or {}).get("level"),
                "remark": (profile or {}).get("remark"),
                "email_login_enabled": _identity_login_enabled(email_identity),
                "phone_login_enabled": _identity_login_enabled(phone_identity),
                "email_identity": (email_identity or {}).get("identifier"),
                "phone_identity": (phone_identity or {}).get("identifier"),
                "email_identity_verified": 1 if (email_identity or {}).get("verified") == 1 else 0,
                "phone_identity_verified": 1 if (phone_identity or {}).get("verified") == 1 else 0,
                "email_identity_bind_status": (email_identity or {}).get("bind_status"),
                "phone_identity_bind_status": (phone_identity or {}).get("bind_status"),
            }
            if full:
                view["identities"] = account_identities
                view["oauth_bindings"] = []
            items.append(view)
        return items


def _pick_profile(account: dict, admin_map: dict, portal_map: dict) -> dict | None:
    match account.get("account_type"):
        case AccountType.ADMIN.value:
            return admin_map.get(str(account["id"]))
        case AccountType.PORTAL.value:
            return portal_map.get(str(account["id"]))
        case _:
            return None


def _primary_account_identity(identities: list[dict]) -> dict | None:
    primary = next(
        (i for i in identities if i.get("identity_type") == "ACCOUNT" and i.get("is_primary") == 1),
        None,
    )
    return primary or next((i for i in identities if i.get("identity_type") == "ACCOUNT"), None)


def _email_phone_identities(identities: list[dict]) -> tuple[dict | None, dict | None]:
    email = next((i for i in identities if i.get("identity_type") == "EMAIL"), None)
    phone = next((i for i in identities if i.get("identity_type") == "PHONE"), None)
    return email, phone


def _identity_login_enabled(identity: dict | None) -> int:
    # 1. 有标识且已验证且为 BOUND 时视为启用登录
    if (
        identity
        and identity.get("identifier")
        and identity.get("verified") == 1
        and identity.get("bind_status") == AccountIdentityBindStatus.BOUND.value
    ):
        return 1
    return 0
