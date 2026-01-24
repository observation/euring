"""Tests for EURING field definitions."""

import re

from euring.fields import EURING2000_FIELDS, EURING2000PLUS_FIELDS, EURING2020_FIELDS, EURING_FIELDS
from euring.types import (
    TYPE_ALPHABETIC,
    TYPE_ALPHANUMERIC,
    TYPE_INTEGER,
    TYPE_NUMERIC,
    TYPE_NUMERIC_SIGNED,
    TYPE_TEXT,
)


def test_euring_fields():
    assert len(EURING_FIELDS) == 64


def test_euring2020_fields():
    assert len(EURING2020_FIELDS) == len(EURING_FIELDS)
    assert len(EURING2020_FIELDS) == 64
    assert EURING2020_FIELDS == EURING_FIELDS


def test_euring2000plus_fields():
    assert len(EURING2000PLUS_FIELDS) == 60
    assert EURING2000PLUS_FIELDS == EURING_FIELDS[:60]


def test_euring2000_fields():
    assert len(EURING2000_FIELDS) == 33
    assert EURING2000_FIELDS == EURING_FIELDS[:33]


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
        assert field["type_name"] in allowed_types
        assert re.match(r"^[a-z0-9_]+$", field["key"]) is not None
        if "length" in field:
            assert isinstance(field["length"], int)
            assert field["length"] > 0
        if "variable_length" in field:
            assert isinstance(field["variable_length"], bool)
        if "required" in field:
            assert isinstance(field["required"], bool)


def test_field_length_exclusivity():
    for field in EURING_FIELDS:
        if field.get("variable_length"):
            assert "length" in field
        if "length" in field:
            assert "min_length" not in field
            assert "max_length" not in field


def test_field_min_length_zero_not_required():
    for field in EURING_FIELDS:
        assert field.get("min_length") is None
