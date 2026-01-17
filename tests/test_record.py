"""Tests for building EURING records."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from euring import EuringRecord, euring_decode_record


def _values_from_record(record: str) -> dict[str, str]:
    decoded = euring_decode_record(record)
    values: dict[str, str] = {}
    for key, field in decoded.fields.items():
        value = field.get("value")
        if value is None:
            continue
        values[key] = value
    return values


def test_record_euring2000_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
    spec = spec_from_file_location("euring2000_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2000_EXAMPLES[0]
    values = _values_from_record(record_str)
    record = EuringRecord("euring2000")
    record.update(values)
    assert record.serialize() == record_str


def test_record_euring2000plus_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2000plus_examples.py"
    spec = spec_from_file_location("euring2000plus_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2000PLUS_EXAMPLES[0]
    values = _values_from_record(record_str)
    record = EuringRecord("euring2000plus")
    record.update(values)
    assert record.serialize() == record_str


def test_record_euring2020_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2020_EXAMPLES[0]
    values = _values_from_record(record_str)
    record = EuringRecord("euring2020")
    record.update(values)
    assert record.serialize() == record_str


def test_record_missing_required_field_raises():
    record = EuringRecord("euring2000plus")
    with pytest.raises(ValueError):
        record.serialize()


def test_record_unknown_field_key_raises():
    record = EuringRecord("euring2000plus", strict=False)
    with pytest.raises(ValueError):
        record.set("unknown_key", "value")


def test_record_non_strict_allows_missing_required():
    record = EuringRecord("euring2000plus", strict=False)
    record.set("ringing_scheme", "GBB")
    record = record.serialize()
    assert record.split("|")[0] == "GBB"


def test_record_invalid_format_raises():
    with pytest.raises(ValueError):
        EuringRecord("bad-format")


def test_record_missing_format_raises():
    with pytest.raises(TypeError):
        EuringRecord()  # type: ignore[call-arg]


def test_record_invalid_value_raises():
    record = EuringRecord("euring2000plus", strict=False)
    record.set("ringing_scheme", "1")
    with pytest.raises(ValueError):
        record.serialize()


def test_record_record_validation_error():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2020_EXAMPLES[0]
    values = _values_from_record(record)
    record = EuringRecord("euring2020")
    record.update(values)
    record.set("geographical_coordinates", "+0000000+0000000")
    with pytest.raises(ValueError):
        record.serialize()
