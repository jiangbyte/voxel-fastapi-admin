"""Author: Charlie

sys_config 列存储拆分：HTTP 统一 config_value，落库按 value_type 写入 config_value 或 config_json。
"""

from __future__ import annotations

import json
from typing import Any

VERSION_CONFLICT_MESSAGE = "配置已被他人修改，请刷新后重试"


def normalize_value_type(value_type: str | None) -> str:
    """归一化 value_type（INT/INTEGER/LONG/BOOL → NUMBER）。"""
    vt = (value_type or "STRING").strip().upper()
    if vt in ("INT", "INTEGER", "LONG", "BOOL"):
        return "NUMBER"
    return vt or "STRING"


def external_value_from_row(
    config_value: str | None,
    config_json: Any,
    value_type: str | None,
) -> str | None:
    """将 DB 列合并为对外统一的 config_value 字符串。"""
    if normalize_value_type(value_type) == "JSON":
        if config_json is not None:
            return json.dumps(config_json, ensure_ascii=False, separators=(",", ":"))
        return config_value
    return config_value


def apply_external_to_columns(payload: dict[str, Any]) -> dict[str, Any]:
    """按 value_type 将统一 config_value 拆分到 config_value / config_json 列字段。"""
    # 1. 归一化类型并拷贝，避免污染调用方 dict
    out = dict(payload)
    value_type = normalize_value_type(str(out.get("value_type") or "STRING"))
    out["value_type"] = value_type
    if "config_value" not in out:
        return out
    external = out.get("config_value")
    # 2. JSON 写入 config_json 并清空标量列；标量相反
    if value_type == "JSON":
        if external is None or (isinstance(external, str) and external.strip() == ""):
            out["config_json"] = None
            out["config_value"] = None
        elif isinstance(external, str):
            out["config_json"] = json.loads(external)
            out["config_value"] = None
        else:
            out["config_json"] = external
            out["config_value"] = None
    else:
        out["config_value"] = None if external is None else str(external)
        out["config_json"] = None
    return out
