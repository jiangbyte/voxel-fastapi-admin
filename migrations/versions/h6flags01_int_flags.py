"""Author: Charlie

业务标志列 tinyint(1) → INT(0/1)；sys_config BOOL 值迁移为 NUMBER 0/1。
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h6flags01"
down_revision: Union[str, Sequence[str], None] = "h5sysconfig01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 读取手工维护的 DDL（与 scripts/migrate_flags_to_int.sql 一致）
    # 2. 按语句拆分执行，便于在部分列已迁移时重复跑 revision
    sql_path = Path(__file__).resolve().parents[2] / "scripts" / "migrate_flags_to_int.sql"
    raw = sql_path.read_text(encoding="utf-8")
    statements = [
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.strip().startswith("--")
    ]
    conn = op.get_bind()
    for stmt in statements:
        conn.execute(sa.text(stmt))


def downgrade() -> None:
    # 标志列回退为 BOOLEAN/tinyint 不做自动降级（避免数据语义丢失）
    pass
