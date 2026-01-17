"""Tests for format inputs and hints."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from euring import EuringRecord
from euring.converters import convert_euring_record
from euring.exceptions import EuringParseException
from euring.formats import format_hint


def _load_fixture(module_name: str, filename: str) -> list[str]:
    fixture_path = Path(__file__).parent / "fixtures" / filename
    spec = spec_from_file_location(module_name, fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__[module_name.upper()]


def test_decode_format_accepts_lowercase():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    decoded = EuringRecord.decode(record, format="euring2000plus")
    assert decoded.display_format == "EURING2000+"


def test_decode_format_rejects_uppercase_formal():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(EuringParseException, match="Unknown format"):
        EuringRecord.decode(record, format="EURING2000PLUS")


def test_decode_format_rejects_plus_alias():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(EuringParseException, match="Unknown format"):
        EuringRecord.decode(record, format="euring2000+")


def test_decode_format_rejects_short_alias():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(EuringParseException, match="Unknown format"):
        EuringRecord.decode(record, format="euring2000p")


def test_decode_format_rejects_missing_prefix():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(EuringParseException, match="Unknown format"):
        EuringRecord.decode(record, format="2000plus")


def test_convert_target_format_accepts_lowercase():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    converted = convert_euring_record(record, target_format="euring2000plus")
    assert "|" in converted


def test_convert_target_format_rejects_uppercase_formal():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown target format"):
        convert_euring_record(record, target_format="EURING2000PLUS")


def test_convert_target_format_rejects_plus_alias():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown target format"):
        convert_euring_record(record, target_format="euring2000+")


def test_convert_target_format_rejects_short_alias():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown target format"):
        convert_euring_record(record, target_format="euring2000p")


def test_convert_target_format_rejects_missing_prefix():
    records = _load_fixture("euring2000_examples", "euring2000_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown target format"):
        convert_euring_record(record, target_format="2000plus")


def test_convert_source_format_accepts_lowercase():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    converted = convert_euring_record(record, source_format="euring2000plus", target_format="euring2020")
    assert "|" in converted


def test_convert_source_format_rejects_uppercase_formal():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown source format"):
        convert_euring_record(record, source_format="EURING2000PLUS", target_format="euring2020")


def test_convert_source_format_rejects_plus_alias():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown source format"):
        convert_euring_record(record, source_format="euring2000+", target_format="euring2020")


def test_convert_source_format_rejects_short_alias():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown source format"):
        convert_euring_record(record, source_format="euring2000p", target_format="euring2020")


def test_convert_source_format_rejects_missing_prefix():
    records = _load_fixture("euring2000plus_examples", "euring2000plus_examples.py")
    record = records[0]
    with pytest.raises(ValueError, match="Unknown source format"):
        convert_euring_record(record, source_format="2000plus", target_format="euring2020")


def test_format_hint_for_2020():
    assert format_hint("2020") == "euring2020"


def test_format_hint_for_2000plus():
    assert format_hint("2000plus") == "euring2000plus"


def test_format_hint_for_2000_plus_symbol():
    assert format_hint("2000+") == "euring2000plus"


def test_format_hint_for_2000():
    assert format_hint("2000") == "euring2000"


def test_format_hint_unknown_returns_none():
    assert format_hint("unknown") is None
