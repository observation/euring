"""Tests for building EURING records."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from euring import EuringRecordBuilder, euring_decode_record


def _values_from_record(record: str) -> dict[str, str]:
    decoded = euring_decode_record(record)
    values: dict[str, str] = {}
    for key, field in decoded["data_by_key"].items():
        if field is None:
            continue
        values[key] = field["value"]
    return values


def test_build_euring2000_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
    spec = spec_from_file_location("euring2000_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2000_EXAMPLES[0]
    values = _values_from_record(record)
    builder = EuringRecordBuilder("euring2000")
    builder.update(values)
    assert builder.build() == record


def test_build_euring2000plus_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2000plus_examples.py"
    spec = spec_from_file_location("euring2000plus_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2000PLUS_EXAMPLES[0]
    values = _values_from_record(record)
    builder = EuringRecordBuilder("euring2000plus")
    builder.update(values)
    assert builder.build() == record


def test_build_euring2020_round_trip():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2020_EXAMPLES[0]
    values = _values_from_record(record)
    builder = EuringRecordBuilder("euring2020")
    builder.update(values)
    assert builder.build() == record


def test_build_missing_required_field_raises():
    builder = EuringRecordBuilder("euring2000plus")
    with pytest.raises(ValueError):
        builder.build()


def test_build_unknown_field_key_raises():
    builder = EuringRecordBuilder("euring2000plus", strict=False)
    with pytest.raises(ValueError):
        builder.set("unknown_key", "value")


def test_build_non_strict_allows_missing_required():
    builder = EuringRecordBuilder("euring2000plus", strict=False)
    builder.set("ringing_scheme", "GBB")
    record = builder.build()
    assert record.split("|")[0] == "GBB"


def test_build_invalid_format_raises():
    with pytest.raises(ValueError):
        EuringRecordBuilder("bad-format")


def test_build_invalid_value_raises():
    builder = EuringRecordBuilder("euring2000plus", strict=False)
    builder.set("ringing_scheme", "1")
    with pytest.raises(ValueError):
        builder.build()


def test_build_record_validation_error():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2020_EXAMPLES[0]
    values = _values_from_record(record)
    builder = EuringRecordBuilder("euring2020")
    builder.update(values)
    builder.set("geographical_coordinates", "+0000000+0000000")
    with pytest.raises(ValueError):
        builder.build()
