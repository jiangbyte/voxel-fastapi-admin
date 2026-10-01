""" Author: Charlie

HTTP JSON 线型：凡数字（int/float/金额等）出入参均为字符串；字符串/对象不强制转换。
业务 0/1 只是普通整数取值，线型与其它 int 相同（WireFlag = 带 0|1 校验的 WireInt）。
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any

from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema

from voxel_types.schema.datetime import format_utc_iso8601


def parse_wire_flag(value: Any) -> int:
    """解析 0|1 整数（业务标志语义）；线型仍是普通数字字符串。"""
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        if value in (0, 1):
            return value
        raise ValueError(f"Invalid flag wire value (expected 0 or 1): {value!r}")
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return 1
        if normalized in {"false", "0", "no", "n", "off", ""}:
            return 0
    raise ValueError(f"Invalid flag wire value: {value!r}")


def parse_wire_int(value: Any) -> int:
    """解析 wire/输入 int。仅进程内构造时允许原生 int。"""
    if isinstance(value, bool):
        raise ValueError("Boolean is not a valid integer wire value")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            raise ValueError("Empty string is not a valid integer")
        return int(text, 10)
    if isinstance(value, Decimal):
        return int(value)
    raise ValueError(f"Invalid integer wire value: {value!r}")


def parse_wire_float(value: Any) -> float:
    """解析 wire/输入 float。仅进程内构造时允许原生 int/float。"""
    if isinstance(value, bool):
        raise ValueError("Boolean is not a valid float wire value")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            raise ValueError("Empty string is not a valid float")
        return float(text)
    if isinstance(value, Decimal):
        return float(value)
    raise ValueError(f"Invalid float wire value: {value!r}")


def serialize_wire_scalar(value: Any) -> Any:
    """将单个 JSON 叶子值序列化为 wire 输出。"""
    if value is None:
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, datetime):
        return format_utc_iso8601(value)
    if isinstance(value, Enum):
        enum_value = value.value
        if isinstance(enum_value, bool):
            return "1" if enum_value else "0"
        if isinstance(enum_value, (int, float, Decimal)):
            return str(enum_value)
        return str(enum_value)
    if isinstance(value, Decimal):
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        rounded = round(value, 2)
        if abs(value - rounded) < 1e-9:
            return f"{rounded:.2f}"
        return str(value)
    return value


def serialize_wire_value(value: Any) -> Any:
    """递归将 JSON 标量（bool/int/float/datetime/Decimal/Enum）字符串化。"""
    if isinstance(value, dict):
        return {key: serialize_wire_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_wire_value(item) for item in value]
    return serialize_wire_scalar(value)


def _serialize_int(value: int) -> str:
    """int 序列化为十进制字符串。"""
    return str(value)


def _serialize_float(value: float) -> str:
    """float 序列化为字符串。"""
    return str(value)


def _serialize_money(value: float) -> str:
    """金额字段固定两位小数。"""
    return f"{value:.2f}"


# JSON Schema 元数据：标量在 wire 层均以字符串呈现。
_STRING_SCHEMA = WithJsonSchema({"type": "string"})
# 0|1 业务标志：线型序列化与 WireInt 相同（数字→字符串）；仅多一层 0|1 入参校验。
WireFlag = Annotated[
    int,
    BeforeValidator(parse_wire_flag),
    PlainSerializer(_serialize_int, return_type=str, when_used="json"),
    _STRING_SCHEMA,
]

# 线型整数：入站解析字符串/Decimal，出站输出字符串。
WireInt = Annotated[
    int,
    BeforeValidator(parse_wire_int),
    PlainSerializer(_serialize_int, return_type=str, when_used="json"),
    _STRING_SCHEMA,
]

# 线型浮点：入站解析字符串/Decimal，出站输出字符串。
WireFloat = Annotated[
    float,
    BeforeValidator(parse_wire_float),
    PlainSerializer(_serialize_float, return_type=str, when_used="json"),
    _STRING_SCHEMA,
]

# 金额字段：固定两位小数字符串（对齐 Boot BigDecimal JSON）。
WireMoney = Annotated[
    float,
    BeforeValidator(parse_wire_float),
    PlainSerializer(_serialize_money, return_type=str, when_used="json"),
    _STRING_SCHEMA,
]
