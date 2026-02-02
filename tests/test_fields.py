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
    """Test the number of EURING fields, there should be 64."""
    assert len(EURING_FIELDS) == 64


def test_euring2020_fields():
    """Test the number of EURING2020 fields, there should be 64."""
    assert len(EURING2020_FIELDS) == len(EURING_FIELDS)
    assert len(EURING2020_FIELDS) == 64
    assert EURING2020_FIELDS == EURING_FIELDS


def test_euring2000plus_fields():
    """Test the number of EURING2000+ fields, there should be 60."""
    assert len(EURING2000PLUS_FIELDS) == 60
    assert EURING2000PLUS_FIELDS == EURING_FIELDS[:60]


def test_euring2000_fields():
    """Test the number of EURING2000 fields, there should be 33."""
    assert len(EURING2000_FIELDS) == 33
    assert EURING2000_FIELDS == EURING_FIELDS[:33]


def test_euring2000_record_length():
    """
    Test the start, end and length attributes of the EURING2000 fields.

    The record length for EURING2000 is exactly 94 characters.
    Every EURING2000 field has start, end and length.
    The values for start and end are a based, inclusive.
    """
    length = 0
    last_end = 0
    for field in EURING2000_FIELDS:
        assert field.start > 0
        assert field.end >= field.start
        assert field.length == field.end - field.start + 1
        length += field.length
        last_end = field.end
    assert length == 94
    assert last_end == 94


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
        assert field["euring_type"] in allowed_types
        assert re.match(r"^[a-z0-9_]+$", field["key"]) is not None
        if "length" in field:
            assert isinstance(field["length"], int)
            assert field["length"] > 0
        if "variable_length" in field:
            assert isinstance(field["variable_length"], bool)
        if "required" in field:
            assert isinstance(field["required"], bool)


def test_fields_with_variable_length_have_length():
    for field in EURING_FIELDS:
        if field.get("variable_length"):
            assert "length" in field
