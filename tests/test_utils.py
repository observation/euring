"""Tests for EURING utility functions."""

import pytest

from euring import (
    euring_identification_display_format,
    euring_identification_export_format,
    euring_scheme_export_format,
    euring_species_export_format,
)
from euring.utils import is_all_hyphens, is_empty


def test_identification_format():
    assert euring_identification_display_format("ab.12-3") == "AB123"
    assert euring_identification_export_format("AB123") == "AB.....123"


def test_scheme_format():
    assert euring_scheme_export_format("GB") == " GB"
    assert euring_scheme_export_format("ABCDE") == "ABC"


def test_species_format():
    assert euring_species_export_format("123") == "00123"
    assert euring_species_export_format("12345") == "12345"
    with pytest.raises(ValueError):
        euring_species_export_format("123456")
    with pytest.raises(ValueError):
        euring_species_export_format("not-a-number")


def test_is_empty():
    assert is_empty("")
    assert is_empty(None)
    assert not is_empty(0)
    assert not is_empty(False)


def test_is_all_hyphens():
    assert is_all_hyphens("-")
    assert not is_all_hyphens("")
