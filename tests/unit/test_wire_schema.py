""" Author: Charlie

HTTP JSON 的 wire 标量序列化/解析。
"""
from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag, parse_wire_flag, parse_wire_int, serialize_wire_value


class SampleSchema(ApiSchema):
    enabled: WireFlag = 1
    count: int = 0


def test_wire_flag_serializes_as_zero_one():
    payload = SampleSchema(enabled=0, count=1).model_dump(mode="json")
    assert payload == {"enabled": "0", "count": "1"}


def test_parse_wire_flag_accepts_legacy_bool_strings():
    assert parse_wire_flag("true") == 1
    assert parse_wire_flag("false") == 0
    assert parse_wire_flag("1") == 1
    assert parse_wire_int("42") == 42


def test_serialize_wire_value_uses_one_zero_for_bool():
    assert serialize_wire_value({"a": True, "b": [1, False]}) == {"a": "1", "b": ["1", "0"]}
