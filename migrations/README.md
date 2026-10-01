# 数据库迁移

Alembic 版本目录，只管理**表结构**增量变更。

- **MySQL 演示全量**（含种子）：[`scripts/voxel_fastapi.sql`](../scripts/voxel_fastapi.sql)
- **可移植建表**：空库执行 `alembic upgrade head`（种子需另行导入）

```bash
# 在项目根目录执行；DB__URL 支持 postgresql+asyncpg / mysql+aiomysql（或 asyncmy）
alembic upgrade head
alembic revision --autogenerate -m "describe schema change"
alembic check
```

连接串来自 `.env` 的 `DB__URL`（见 `alembic.ini` / `migrations/env.py`）。

应用启动（`entrypoint.sh`）不会执行迁移；以上命令仅在维护时手动执行。
