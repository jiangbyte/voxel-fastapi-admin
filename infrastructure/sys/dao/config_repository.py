"""系统配置仓储实现。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.sys_config_storage import (
    VERSION_CONFLICT_MESSAGE,
    apply_external_to_columns,
)
from infrastructure.id_generator.snowflake import generate_snowflake_id
from infrastructure.dao.batch import chunked
from infrastructure.dao.compat import ci_like
from infrastructure.dao.models.sys_config import SysConfig
from voxel_types.business import ConflictError, NotFoundError
from voxel_types.schema.wire import parse_wire_flag


def _flag_int(value: Any) -> int:
    """将入参归一化为 0/1 标志位。"""
    if value is None:
        return 0
    return parse_wire_flag(value)


def _row(entity: SysConfig) -> dict[str, Any]:
    from sqlalchemy import inspect

    mapper = inspect(entity).mapper
    return {attr.key: getattr(entity, attr.key) for attr in mapper.column_attrs}


class ConfigRepositoryImpl:
    """系统配置仓储实现。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Mapping[str, Any]) -> dict[str, Any]:
        if await self.get_by_key(str(data["config_key"])) is not None:
            raise ConflictError("Config key already exists")
        payload = apply_external_to_columns(dict(data))
        payload.pop("version", None)
        entity = SysConfig(**payload)
        self.db.add(entity)
        await self.db.flush()
        return _row(entity)

    async def get_by_id(self, config_id: str) -> SysConfig | None:
        return await self.db.get(SysConfig, config_id)

    async def get_required(self, config_id: str) -> dict[str, Any]:
        entity = await self.get_by_id(config_id)
        if entity is None:
            raise NotFoundError("Config not found")
        return _row(entity)

    async def list_by_ids(self, config_ids: list[str]) -> list[dict[str, Any]]:
        unique_ids = list(dict.fromkeys(config_ids))
        if not unique_ids:
            return []
        entities_by_id: dict[str, SysConfig] = {}
        for batch in chunked(unique_ids):
            rows = (
                (await self.db.execute(select(SysConfig).where(SysConfig.id.in_(batch))))
                .scalars()
                .all()
            )
            for entity in rows:
                entities_by_id[entity.id] = entity
        return [
            _row(entities_by_id[config_id])
            for config_id in unique_ids
            if config_id in entities_by_id
        ]

    async def update(self, config_id: str, data: Mapping[str, Any]) -> None:
        """按主键更新；可选 version 乐观锁。"""
        # 1. 校验存在与 config_key 唯一
        entity = await self.get_by_id(config_id)
        if entity is None:
            raise NotFoundError("Config not found")
        duplicate = await self._get_po_by_key(str(data.get("config_key", entity.config_key)))
        if duplicate is not None and duplicate.id != config_id:
            raise ConflictError("Config key already exists")
        payload = apply_external_to_columns(dict(data))
        expected_version = payload.pop("version", None)
        payload.pop("id", None)
        # 2. 带 version 时用条件 UPDATE；否则 ORM 更新并自增 version
        if expected_version is not None:
            values = dict(payload)
            values["version"] = SysConfig.version + 1
            stmt = (
                update(SysConfig)
                .where(SysConfig.id == config_id, SysConfig.version == expected_version)
                .values(**values)
            )
            result = await self.db.execute(stmt)
            if result.rowcount == 0:
                raise ConflictError(VERSION_CONFLICT_MESSAGE)
            return
        for key, value in payload.items():
            setattr(entity, key, value)
        entity.version = (entity.version or 0) + 1
        await self.db.flush()

    async def delete_many(self, config_ids: list[str]) -> None:
        unique_ids = list(dict.fromkeys(config_ids))
        if not unique_ids:
            return
        await self.db.execute(delete(SysConfig).where(SysConfig.id.in_(unique_ids)))

    async def list_by_category(
        self,
        category: str | None = None,
        scope: str | None = None,
    ) -> list[dict[str, Any]]:
        stmt = select(SysConfig).order_by(SysConfig.sort_code.asc())
        if category:
            stmt = stmt.where(SysConfig.category == category)
        if scope:
            stmt = stmt.where(SysConfig.scope == scope)
        items = list((await self.db.execute(stmt)).scalars().all())
        return [_row(item) for item in items]

    async def get_by_key(self, config_key: str) -> dict[str, Any] | None:
        po = await self._get_po_by_key(config_key)
        return _row(po) if po is not None else None

    async def batch_save(self, items: Sequence[Mapping[str, Any]]) -> None:
        """按 config_key upsert；可选 version 乐观锁。"""
        if not items:
            return
        keys = [str(item["config_key"]) for item in items]
        stmt = select(SysConfig).where(SysConfig.config_key.in_(keys))
        existing = {row.config_key: row for row in (await self.db.execute(stmt)).scalars().all()}
        for item in items:
            raw = dict(item)
            entity = existing.get(str(item["config_key"]))
            if entity is not None and raw.get("value_type") is None:
                raw["value_type"] = entity.value_type
            payload = apply_external_to_columns(raw)
            expected_version = payload.pop("version", None)
            if entity is None:
                payload.pop("version", None)
                self.db.add(
                    SysConfig(
                        id=generate_snowflake_id(),
                        config_key=str(item["config_key"]),
                        config_value=payload.get("config_value"),
                        config_json=payload.get("config_json"),
                        category=payload.get("category"),
                        remark=payload.get("remark"),
                        value_type=payload.get("value_type") or "STRING",
                        label=payload.get("label"),
                        scope=payload.get("scope"),
                        scene=payload.get("scene"),
                        is_builtin=_flag_int(payload.get("is_builtin"))
                        if payload.get("is_builtin") is not None
                        else 0,
                        sort_code=int(payload.get("sort_code") or 0),
                    )
                )
                continue
            if expected_version is not None:
                values: dict[str, Any] = {}
                if "config_value" in payload or "config_json" in payload:
                    values["config_value"] = payload.get("config_value")
                    values["config_json"] = payload.get("config_json")
                if payload.get("category") is not None:
                    values["category"] = payload.get("category")
                if payload.get("remark") is not None:
                    values["remark"] = payload.get("remark")
                if payload.get("value_type") is not None:
                    values["value_type"] = str(payload.get("value_type"))
                for field in ("label", "scope", "scene"):
                    if field in payload:
                        values[field] = payload.get(field)
                if payload.get("is_builtin") is not None:
                    values["is_builtin"] = _flag_int(payload.get("is_builtin"))
                if payload.get("sort_code") is not None:
                    values["sort_code"] = int(payload.get("sort_code"))
                values["version"] = SysConfig.version + 1
                stmt_up = (
                    update(SysConfig)
                    .where(SysConfig.id == entity.id, SysConfig.version == expected_version)
                    .values(**values)
                )
                result = await self.db.execute(stmt_up)
                if result.rowcount == 0:
                    raise ConflictError(VERSION_CONFLICT_MESSAGE)
                continue
            if "config_value" in payload or "config_json" in payload:
                entity.config_value = payload.get("config_value")
                entity.config_json = payload.get("config_json")
            if payload.get("category") is not None:
                entity.category = payload.get("category")
            if payload.get("remark") is not None:
                entity.remark = payload.get("remark")
            if payload.get("value_type") is not None:
                entity.value_type = str(payload.get("value_type"))
            for field in ("label", "scope", "scene"):
                if field in payload:
                    setattr(entity, field, payload.get(field))
            if payload.get("is_builtin") is not None:
                entity.is_builtin = _flag_int(payload.get("is_builtin"))
            if payload.get("sort_code") is not None:
                entity.sort_code = int(payload.get("sort_code"))
            entity.version = (entity.version or 0) + 1
        await self.db.flush()

    async def page_admin(
        self,
        filters: Mapping[str, Any],
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        stmt: Select[tuple[SysConfig]] = select(SysConfig)
        count_stmt = select(func.count(SysConfig.id))
        sql_filters = []
        config_key = filters.get("config_key")
        category = filters.get("category")
        if config_key:
            sql_filters.append(ci_like(SysConfig.config_key, str(config_key)))
        if category:
            sql_filters.append(SysConfig.category == category)
        if sql_filters:
            stmt = stmt.where(*sql_filters)
            count_stmt = count_stmt.where(*sql_filters)
        stmt = (
            stmt.order_by(SysConfig.sort_code.asc(), SysConfig.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        total = (await self.db.execute(count_stmt)).scalar_one()
        return [_row(item) for item in items], total

    async def _get_po_by_key(self, config_key: str) -> SysConfig | None:
        stmt = select(SysConfig).where(SysConfig.config_key == config_key)
        return (await self.db.execute(stmt)).scalar_one_or_none()
