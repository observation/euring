"""Tests for EURING format normalization helpers."""

import pytest

from euring.formats import (
    EURING2000,
    EURING2000PLUS,
    EURING2020,
    normalize_format,
    normalize_format_hint,
    normalize_source_format,
    normalize_target_format,
)


def test_normalize_format_accepts_aliases():
    assert normalize_format("euring2000") == EURING2000
    assert normalize_format("EURING2000") == EURING2000
    assert normalize_format("2000") == EURING2000
    assert normalize_format("2000+") == EURING2000PLUS
    assert normalize_format("2000plus") == EURING2000PLUS
    assert normalize_format("2000p") == EURING2000PLUS
    assert normalize_format("2020") == EURING2020
    assert normalize_format("euring2020") == EURING2020


def test_normalize_format_rejects_unknown():
    with pytest.raises(ValueError, match="Unknown format"):
        normalize_format("euring1999")


def test_normalize_format_hint_accepts_aliases():
    assert normalize_format_hint("EURING2000") == "EURING2000"
    assert normalize_format_hint("EURING2000+") == "EURING2000+"
    assert normalize_format_hint("EURING2000PLUS") == "EURING2000+"
    assert normalize_format_hint("EURING2000P") == "EURING2000+"
    assert normalize_format_hint("EURING2020") == "EURING2020"


def test_normalize_format_hint_rejects_missing_prefix():
    with pytest.raises(Exception, match="Unknown format hint"):
        normalize_format_hint("2020")


def test_normalize_target_format_accepts_aliases():
    assert normalize_target_format("EURING2000") == "EURING2000"
    assert normalize_target_format("EURING2000+") == "EURING2000+"
    assert normalize_target_format("EURING2000PLUS") == "EURING2000+"
    assert normalize_target_format("EURING2000P") == "EURING2000+"
    assert normalize_target_format("EURING2020") == "EURING2020"


def test_normalize_target_format_rejects_unknown():
    with pytest.raises(ValueError, match="Unknown target format"):
        normalize_target_format("2020")


def test_normalize_source_format_infers_fixed_width():
    record = "A" * 94
    assert normalize_source_format(None, record) == "EURING2000"


def test_normalize_source_format_infers_2000plus():
    record = "|".join(["A"] * 42)
    assert normalize_source_format(None, record) == "EURING2000+"


def test_normalize_source_format_infers_2020_when_accuracy_alpha():
    record = "|".join([""] * 25 + ["A"] + [""] * 40)
    assert normalize_source_format(None, record) == "EURING2020"


def test_normalize_source_format_infers_2020_when_extra_fields():
    record = "|".join([""] * 55)
    assert normalize_source_format(None, record) == "EURING2020"


def test_normalize_source_format_accepts_aliases():
    record = "|".join([""] * 10)
    assert normalize_source_format("EURING2000", record) == "EURING2000"
    assert normalize_source_format("EURING2000PLUS", record) == "EURING2000+"
    assert normalize_source_format("EURING2000P", record) == "EURING2000+"
    assert normalize_source_format("EURING2020", record) == "EURING2020"


def test_normalize_source_format_rejects_unknown():
    with pytest.raises(ValueError, match="Unknown source format"):
        normalize_source_format("euring2000", "A")
