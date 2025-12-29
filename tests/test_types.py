"""Tests for EURING type validation functions."""

from euring import (
    TYPE_ALPHABETIC,
    TYPE_INTEGER,
    TYPE_NUMERIC_SIGNED,
    is_alphabetic,
    is_alphanumeric,
    is_integer,
    is_numeric,
    is_numeric_signed,
    is_text,
    is_valid_type,
)


class TestTypes:
    def test_alphabetic(self):
        assert is_alphabetic("ABC")
        assert is_alphabetic("A-Z")
        assert is_alphabetic("")
        assert not is_alphabetic("abc")
        assert not is_alphabetic("123")
        assert is_alphabetic("A-B")

    def test_alphanumeric(self):
        assert is_alphanumeric("ABC123")
        assert is_alphanumeric("A+B-C*D")
        assert is_alphanumeric("")
        assert not is_alphanumeric("abc")
        assert is_alphanumeric("A.B")

    def test_integer(self):
        assert is_integer("123")
        assert is_integer("---")
        assert not is_integer("")
        assert not is_integer("12.3")
        assert not is_integer("abc")

    def test_numeric(self):
        assert is_numeric("123")
        assert is_numeric("12.3")
        assert is_numeric("0.5")
        assert not is_numeric("12.")
        assert not is_numeric(".12")

    def test_numeric_signed(self):
        assert is_numeric_signed("123")
        assert is_numeric_signed("12.3")
        assert is_numeric_signed("-12.3")
        assert not is_numeric_signed("-0")
        assert not is_numeric_signed("-0.0")
        assert not is_numeric_signed("12.")
        assert not is_numeric_signed(".12")

    def test_text(self):
        assert is_text("Hello World")
        assert is_text("123!@#")
        assert not is_text("Hello\x00World")
        assert not is_text("Hello|World")

    def test_is_valid_type(self):
        assert is_valid_type("ABC", TYPE_ALPHABETIC)
        assert is_valid_type("123", TYPE_INTEGER)
        assert is_valid_type("-12.3", TYPE_NUMERIC_SIGNED)
        assert not is_valid_type("-0", TYPE_NUMERIC_SIGNED)
        assert not is_valid_type("abc", TYPE_ALPHABETIC)
        assert is_valid_type("ABC", "Unknown") is False
