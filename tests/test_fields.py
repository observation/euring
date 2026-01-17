"""Tests for EURING field definitions."""

import re

from euring.fields import EURING_FIELDS
from euring.types import (
    TYPE_ALPHABETIC,
    TYPE_ALPHANUMERIC,
    TYPE_INTEGER,
    TYPE_NUMERIC,
    TYPE_NUMERIC_SIGNED,
    TYPE_TEXT,
)


def test_field_uniqueness():
    keys = [field["key"] for field in EURING_FIELDS]
    names = [field["name"] for field in EURING_FIELDS]
    num_fields = len(EURING_FIELDS)
    assert num_fields > 0
    assert len(set(keys)) == num_fields
    assert len(set(names)) == num_fields
    assert len(set(keys + names)) == 2 * num_fields


def test_field_shape_and_types():
    allowed_types = {
        TYPE_ALPHABETIC,
        TYPE_ALPHANUMERIC,
        TYPE_INTEGER,
        TYPE_NUMERIC,
        TYPE_NUMERIC_SIGNED,
        TYPE_TEXT,
    }
    for field in EURING_FIELDS:
        assert field["name"]
        assert field["key"]
        assert field["type"] in allowed_types
        assert re.match(r"^[a-z0-9_]+$", field["key"]) is not None
        if "length" in field:
            assert isinstance(field["length"], int)
            assert field["length"] > 0
        for bound in ("min_length", "max_length"):
            if bound in field:
                assert isinstance(field[bound], int)
                assert field[bound] >= 0
        if "required" in field:
            assert isinstance(field["required"], bool)
