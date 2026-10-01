"""Author: Charlie

sys_config：config_json + version 列，JSON 行迁移，INT 别名归一为 NUMBER。
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h5sysconfig01"
down_revision: Union[str, Sequence[str], None] = "h4boot_align03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> set[str]:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if table not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table)}


def upgrade() -> None:
    cols = _columns("sys_config")
    if not cols:
        return
    if "config_json" not in cols:
        op.add_column(
            "sys_config",
            sa.Column(
                "config_json",
                sa.JSON(),
                nullable=True,
                comment="复杂配置（JSON：list/object）",
            ),
        )
    cols = _columns("sys_config")
    if "version" not in cols:
        op.add_column(
            "sys_config",
            sa.Column(
                "version",
                sa.Integer(),
                nullable=False,
                server_default="0",
                comment="乐观锁版本",
            ),
        )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE sys_config SET value_type = 'NUMBER' "
            "WHERE UPPER(value_type) IN ('INT', 'INTEGER', 'LONG')"
        )
    )
    conn.execute(
        sa.text(
            "UPDATE sys_config SET "
            "config_json = CAST(config_value AS JSON), "
            "config_value = NULL, "
            "value_type = 'JSON' "
            "WHERE config_json IS NULL "
            "AND config_value IS NOT NULL "
            "AND config_value <> '' "
            "AND ( "
            "UPPER(value_type) = 'JSON' "
            "OR ( "
            "UPPER(value_type) IN ('STRING', 'TEXT') "
            "AND JSON_VALID(config_value) "
            "AND (TRIM(config_value) LIKE '{%' OR TRIM(config_value) LIKE '[%') "
            ") "
            ")"
        )
    )


def downgrade() -> None:
    cols = _columns("sys_config")
    if not cols:
        return
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE sys_config SET config_value = CAST(config_json AS CHAR) "
            "WHERE config_value IS NULL AND config_json IS NOT NULL"
        )
    )
    if "version" in cols:
        op.drop_column("sys_config", "version")
    cols = _columns("sys_config")
    if "config_json" in cols:
        op.drop_column("sys_config", "config_json")
