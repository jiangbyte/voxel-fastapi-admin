""" Author: Charlie

角色领域模型：角色表，作为授权主载体，通过资源授权间接获得权限与数据范围。
"""

from sqlalchemy import JSON, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from domain.iam.enums import RoleScopeType
from infrastructure.config.enums import StatusEnum, SysBizCategory
from infrastructure.id_generator.snowflake import generate_snowflake_id
from infrastructure.dao.base import Base
from infrastructure.dao.mixins import TimestampMixin


class SysRole(Base, TimestampMixin):
    """角色表，作为授权主载体，通过资源授权间接获得权限和数据范围。"""

    __tablename__ = "sys_role"
    __table_args__ = (UniqueConstraint("code", name="uq_sys_role_code"),)

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_snowflake_id, comment="主键"
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色编码")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色名称")
    category: Mapped[str] = mapped_column(
        String(64), default=SysBizCategory.SYS.value, nullable=False, comment="角色分类"
    )
    scope_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=RoleScopeType.PLATFORM.value,
        comment="角色作用域类型",
    )
    owner_dept_id: Mapped[str | None] = mapped_column(String(64), comment="所属部门ID")
    sort: Mapped[int] = mapped_column(Integer, default=99, nullable=False, comment="排序")
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=StatusEnum.ENABLED.value,
        comment="状态",
    )
    is_builtin: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="是否内置角色"
    )
    description: Mapped[str | None] = mapped_column(Text, comment="描述")
    extra: Mapped[dict] = mapped_column(JSON, default=dict, comment="扩展信息")
