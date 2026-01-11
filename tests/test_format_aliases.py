"""Tests for format aliases and hints."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from euring import EuringRecordBuilder, euring_decode_record
from euring.converters import convert_euring_record
from euring.exceptions import EuringParseException


def _load_fixture(module_name: str, filename: str) -> list[str]:
    fixture_path = Path(__file__).parent / "fixtures" / filename
    spec = spec_from_file_location(module_name, fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__[module_name.upper()]


def test_builder_normalizes_aliases():
    assert EuringRecordBuilder("2000").format == "euring2000"
    assert EuringRecordBuilder("2000+", strict=False).format == "euring2000plus"
    assert EuringRecordBuilder("2000p", strict=False).format == "euring2000plus"
    assert EuringRecordBuilder("2020", strict=False).format == "euring2020"


def test_decode_format_hint_accepts_aliases():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    decoded = euring_decode_record(record, format_hint="EURING2000P")
    assert decoded["format"] == "EURING2000+"


def test_decode_format_hint_rejects_missing_prefix():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(EuringParseException, match="Unknown format hint"):
        euring_decode_record(record, format_hint="2000plus")


def test_convert_target_format_accepts_aliases():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    converted = convert_euring_record(record, target_format="EURING2000P")
    assert "|" in converted


def test_convert_target_format_rejects_missing_prefix():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown target format"):
        convert_euring_record(record, target_format="2000plus")


def test_convert_source_format_accepts_aliases():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    converted = convert_euring_record(record, source_format="EURING2000PLUS", target_format="EURING2020")
    assert "|" in converted


def test_convert_source_format_rejects_missing_prefix():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown source format"):
        convert_euring_record(record, source_format="2000plus", target_format="EURING2020")
