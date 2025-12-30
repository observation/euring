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
