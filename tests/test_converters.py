"""Tests for EURING record conversion."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from euring.converters import _field_index, convert_euring2000_record, convert_euring_record
from euring.fields import EURING_FIELDS
from euring.utils import euring_lat_to_dms, euring_lng_to_dms


def _load_fixture(module_name: str, attr: str) -> str:
    fixture_path = Path(__file__).parent / "fixtures" / f"{module_name}.py"
    spec = spec_from_file_location(module_name, fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, attr)[0]


def _make_euring2020_record_with_coords() -> str:
    values = [""] * len(EURING_FIELDS)
    for index, field in enumerate(EURING_FIELDS):
        if field["key"] == "ringing_scheme":
            values[index] = "GBB"
        if field["key"] == "primary_identification_method":
            values[index] = "A0"
        if field["key"] == "identification_number":
            values[index] = "1234567890"
        if field["key"] == "place_code":
            values[index] = "AB00"
        if field["key"] == "accuracy_of_coordinates":
            values[index] = "A"
        if field["key"] == "latitude":
            values[index] = "52.3760"
        if field["key"] == "longitude":
            values[index] = "4.9000"
    return "|".join(values)


def test_convert_unknown_target_format():
    with pytest.raises(ValueError):
        convert_euring_record("value", target_format="bad")


def test_convert_unknown_source_format():
    with pytest.raises(ValueError):
        convert_euring_record("value", source_format="bad", target_format="euring2000plus")


def test_convert_fixed_width_rejects_pipe():
    with pytest.raises(ValueError):
        convert_euring_record("A|B", source_format="EURING2000", target_format="euring2000plus")


def test_convert_fixed_width_too_short():
    with pytest.raises(ValueError):
        convert_euring_record("A" * 10, source_format="EURING2000", target_format="euring2000plus")


def test_convert_fixed_width_extra_data():
    with pytest.raises(ValueError):
        convert_euring_record("A" * 94 + "X", source_format="EURING2000", target_format="euring2000plus")


def test_convert_euring2000_record_helper():
    record = _load_fixture("euring2000_examples", "EURING2000_EXAMPLES")
    converted = convert_euring2000_record(record)
    assert "|" in converted


def test_convert_extra_fields_rejected():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    with pytest.raises(ValueError):
        convert_euring_record(record + "|EXTRA", source_format="EURING2000+", target_format="euring2020")


def test_convert_requires_force_for_2020_fields():
    record = _load_fixture("euring2020_examples", "EURING2020_EXAMPLES")
    with pytest.raises(ValueError):
        convert_euring_record(record, target_format="euring2000plus")


def test_convert_requires_force_for_dropped_fields():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    fields = record.split("|")
    remarks_index = next(i for i, f in enumerate(EURING_FIELDS) if f["key"] == "remarks")
    fields[remarks_index] = "note"
    with pytest.raises(ValueError):
        convert_euring_record("|".join(fields), target_format="euring2000")


def test_convert_alpha_accuracy_mapping():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    fields = record.split("|")
    accuracy_index = next(i for i, f in enumerate(EURING_FIELDS) if f["key"] == "accuracy_of_coordinates")
    fields[accuracy_index] = "A"
    converted = convert_euring_record("|".join(fields), target_format="euring2000plus", force=True)
    out_fields = converted.split("|")
    assert out_fields[accuracy_index] == "0"


def test_convert_alpha_accuracy_invalid():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    fields = record.split("|")
    accuracy_index = next(i for i, f in enumerate(EURING_FIELDS) if f["key"] == "accuracy_of_coordinates")
    fields[accuracy_index] = "Q"
    with pytest.raises(ValueError):
        convert_euring_record("|".join(fields), target_format="euring2000plus", force=True)


def test_convert_coordinate_downgrade_fills():
    record = _make_euring2020_record_with_coords()
    lat = euring_lat_to_dms(52.3760)
    lng = euring_lng_to_dms(4.9000)
    converted = convert_euring_record(record, target_format="euring2000plus", force=True)
    fields = converted.split("|")
    geo_index = next(i for i, f in enumerate(EURING_FIELDS) if f["key"] == "geographical_coordinates")
    assert fields[geo_index] == f"{lat}{lng}"


def test_convert_to_fixed_width():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    converted = convert_euring_record(record, target_format="euring2000", force=True)
    assert "|" not in converted
    assert len(converted) == 94


def test_convert_auto_detects_fixed_width():
    record = _load_fixture("euring2000_examples", "EURING2000_EXAMPLES")
    converted = convert_euring_record(record, target_format="euring2000plus")
    assert "|" in converted


def test_convert_source_format_alias():
    record = _load_fixture("euring2000plus_examples", "EURING2000PLUS_EXAMPLES")
    converted = convert_euring_record(record, source_format="EURING2000P", target_format="euring2020")
    assert converted.count("|") >= record.count("|")


def test_field_index_unknown_key():
    with pytest.raises(ValueError):
        _field_index("unknown_key")
