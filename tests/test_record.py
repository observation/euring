"""Tests for building EURING records."""

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

import euring.record as record_module
from euring import EuringRecord
from euring.formats import FORMAT_JSON
from euring.record import _fields_for_format, _fixed_width_fields, _format_fixed_width


def _values_from_record(record: str) -> dict[str, str]:
    decoded = EuringRecord.decode(record)
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


def test_record_serialize_json():
    record = EuringRecord("euring2000plus", strict=False)
    record.set("ringing_scheme", "GBB")
    payload = json.loads(record.serialize(output_format=FORMAT_JSON))
    assert payload["record"]["format"] == "EURING2000+"
    assert payload["fields"]["ringing_scheme"]["value"] == "GBB"


def test_record_serialize_rejects_mismatched_format():
    record = EuringRecord("euring2000plus", strict=False)
    with pytest.raises(ValueError):
        record.serialize(output_format="euring2020")


def test_record_export_same_format():
    record = EuringRecord("euring2000plus", strict=False)
    record.set("ringing_scheme", "GBB")
    assert record.export("euring2000plus") == record.serialize()


def test_record_export_requires_force_for_loss():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2020_EXAMPLES[0]
    record = EuringRecord.decode(record_str)
    with pytest.raises(ValueError):
        record.export("euring2000plus")


def test_record_export_warns_on_loss_with_force():
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2020_EXAMPLES[0]
    record = EuringRecord.decode(record_str)
    with pytest.warns(UserWarning):
        record.export("euring2000plus", force=True)


def test_record_euring2000_rejects_extra_fields():
    record = EuringRecord("euring2000", strict=False)
    record.set("ringing_scheme", "GBB")
    record.set("latitude", "52.3760")
    with pytest.raises(ValueError):
        record.serialize()


def test_record_record_validation_error():
    """Raise when record-level validation fails under strict mode."""
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record = module.EURING2020_EXAMPLES[0]
    values = _values_from_record(record)
    record = EuringRecord("euring2020")
    record.update(values)
    record.set("geographical_coordinates", "+000000+0000000")
    with pytest.raises(ValueError):
        record.serialize()


def test_record_decode_sets_format_and_fields():
    """Decode should set format and populate fields."""
    fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
    spec = spec_from_file_location("euring2020_examples", fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    record_str = module.EURING2020_EXAMPLES[0]
    record = EuringRecord.decode(record_str)
    assert record.format == "euring2020"
    assert "ringing_scheme" in record.fields


def test_record_has_errors_non_dict():
    """Non-dict errors should fall back to truthiness checks."""
    record = EuringRecord("euring2000")
    assert record.has_errors(["oops"])
    assert not record.has_errors([])


def test_record_validate_without_record_uses_current_fields():
    """Validate without an explicit record should serialize current fields."""
    record = EuringRecord("euring2000plus", strict=False)
    record.set("ringing_scheme", "GBB")
    errors = record.validate()
    assert isinstance(errors, dict)
    assert record.fields


def test_fields_for_format_euring2000plus_truncates():
    """EURING2000PLUS should stop at the reference field."""
    fields = _fields_for_format("euring2000plus")
    assert fields[-1]["key"] == "reference"


def test_fixed_width_fields_respects_max_length():
    """Fixed-width fields should not exceed the 94-character cutoff."""
    fields = _fixed_width_fields()
    total_length = sum(field["length"] for field in fields)
    assert total_length <= 94


def test_format_fixed_width_handles_empty_and_padding():
    """Fixed-width formatting should pad and fill empty fields."""
    fields = [{"key": "alpha", "length": 2}, {"key": "beta", "length": 3}]
    record = _format_fixed_width({"alpha": "A"}, fields)
    assert record == "A-" + "---"


def test_record_validate_without_record_uses_fixed_width():
    """Validation should serialize fixed-width records when needed."""
    record = EuringRecord("euring2000", strict=False)
    record.set("ringing_scheme", "GBB")
    errors = record.validate()
    assert isinstance(errors, dict)


def test_fields_for_format_euring2000plus_without_reference(monkeypatch):
    """EURING2000PLUS should return all fields when reference is missing."""
    fields = [{"key": "alpha", "length": 1}, {"key": "beta", "length": 1}]
    monkeypatch.setattr(record_module, "EURING_FIELDS", fields)
    assert _fields_for_format("euring2000plus") == fields


def test_fixed_width_fields_breaks_on_missing_length(monkeypatch):
    """Fixed-width fields should stop when length metadata is missing."""
    fields = [{"key": "alpha", "length": 1}, {"key": "beta"}]
    monkeypatch.setattr(record_module, "EURING_FIELDS", fields)
    result = _fixed_width_fields()
    assert result == [{"key": "alpha", "length": 1}]


def test_fixed_width_fields_breaks_at_cutoff(monkeypatch):
    """Fixed-width fields should stop once reaching 94 characters."""
    fields = [{"key": "alpha", "length": 94}, {"key": "beta", "length": 1}]
    monkeypatch.setattr(record_module, "EURING_FIELDS", fields)
    result = _fixed_width_fields()
    assert result == [{"key": "alpha", "length": 94}]


def test_fixed_width_fields_complete_without_break(monkeypatch):
    """Fixed-width fields should include all fields when under the cutoff."""
    fields = [{"key": "alpha", "length": 1}, {"key": "beta", "length": 2}]
    monkeypatch.setattr(record_module, "EURING_FIELDS", fields)
    result = _fixed_width_fields()
    assert result == [{"key": "alpha", "length": 1}, {"key": "beta", "length": 2}]
