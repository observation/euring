"""Tests for EURING record decoding."""

import pytest

from euring import EuringRecord
from euring.codes import (
    lookup_date,
    lookup_geographical_coordinates,
    parse_direction,
    parse_geographical_coordinates,
    parse_old_greater_coverts,
    parse_place_code,
)
from euring.exceptions import EuringConstraintException, EuringTypeException
from euring.fields import EURING_FIELDS
from euring.parsing import euring_decode_value
from euring.types import TYPE_ALPHANUMERIC, TYPE_INTEGER


def _make_euring2000_plus_record(*, accuracy: str) -> str:
    values = [
        "GBB",
        "A0",
        "1234567890",
        "0",
        "1",
        "ZZ",
        "00010",
        "00010",
        "N",
        "0",
        "M",
        "U",
        "U",
        "U",
        "2",
        "2",
        "U",
        "99",
        "99",
        "0",
        "01012024",
        "0",
        "0000",
        "AB00",
        "+0000000+0000000",
        accuracy,
        "9",
        "99",
        "0",
        "4",
        "00000",
        "000",
        "00000",
    ]
    return "|".join(values)


def _make_euring2000_plus_record_with_invalid_species(*, accuracy: str) -> str:
    values = _make_euring2000_plus_record(accuracy=accuracy).split("|")
    values[6] = "12ABC"
    values[7] = "12ABC"
    return "|".join(values)


def _make_euring2020_record_for_coords(
    *,
    geo_value: str,
    lat_value: str,
    lng_value: str,
    accuracy: str = "1",
) -> str:
    base = _make_euring2000_plus_record(accuracy=accuracy).split("|")
    values = base + [""] * (len(EURING_FIELDS) - len(base))

    def set_value(key: str, value: str) -> None:
        for index, field in enumerate(EURING_FIELDS):
            if field["key"] == key:
                values[index] = value
                return
        raise ValueError(f"Unknown key: {key}")

    set_value("geographical_coordinates", geo_value)
    set_value("latitude", lat_value)
    set_value("longitude", lng_value)
    return "|".join(values)


class TestDecoding:
    def test_decode_minimal_record(self):
        # Very minimal EURING record for testing
        record = EuringRecord.decode(_make_euring2000_plus_record(accuracy="1"))
        assert record.display_format == "EURING2000+"
        assert record.fields["ringing_scheme"]["value"] == "GBB"
        assert record.fields

    def test_decode_euring2020_format(self):
        record = EuringRecord.decode(_make_euring2000_plus_record(accuracy="A"))
        assert record.display_format == "EURING2020"

    def test_decode_euring2020_format_rejects_2000_plus(self):
        record = EuringRecord.decode(
            _make_euring2000_plus_record(accuracy="A"),
            format="euring2000plus",
        )
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_value_with_lookup(self):
        result = euring_decode_value("01012024", TYPE_INTEGER, length=8, lookup=lookup_date)
        assert result["raw_value"] == "01012024"
        assert result["value"] == 1012024
        assert result["description"].isoformat() == "2024-01-01"

    def test_decode_value_invalid_type(self):
        with pytest.raises(EuringTypeException):
            euring_decode_value("ABC", TYPE_INTEGER, length=3)

    def test_decode_value_optional_empty(self):
        result = euring_decode_value("", TYPE_INTEGER, min_length=0)
        assert result is None

    def test_decode_value_length_mismatch(self):
        with pytest.raises(EuringConstraintException):
            euring_decode_value("123", TYPE_INTEGER, length=2)

    def test_decode_value_min_length_error(self):
        with pytest.raises(EuringConstraintException):
            euring_decode_value("1", TYPE_INTEGER, min_length=2)

    def test_decode_value_max_length_error(self):
        with pytest.raises(EuringConstraintException):
            euring_decode_value("123", TYPE_INTEGER, max_length=2)

    def test_decode_value_with_parser(self):
        result = euring_decode_value(
            "+420500-0044500",
            TYPE_ALPHANUMERIC,
            length=15,
            parser=parse_geographical_coordinates,
            lookup=lookup_geographical_coordinates,
        )
        assert "parsed_value" in result

    def test_decode_euring2000plus_allows_short_elapsed_time(self):
        record = _make_euring2000_plus_record(accuracy="1").split("|")
        for index, field in enumerate(EURING_FIELDS):
            if field["key"] == "elapsed_time":
                record[index] = "1"
                break
        encoded = "|".join(record)
        decoded = EuringRecord.decode(encoded, format="euring2000plus")
        assert decoded.errors["record"] == []
        assert decoded.fields["elapsed_time"]["value"] == 1

    def test_decode_euring2020_allows_short_distance(self):
        record = _make_euring2000_plus_record(accuracy="A").split("|")
        record += [""] * (len(EURING_FIELDS) - len(record))
        for index, field in enumerate(EURING_FIELDS):
            if field["key"] == "distance":
                record[index] = "18"
                break
        encoded = "|".join(record)
        decoded = EuringRecord.decode(encoded, format="euring2020")
        assert decoded.errors["record"] == []
        assert decoded.fields["distance"]["value"] == 18

    def test_parse_old_greater_coverts_valid(self):
        assert parse_old_greater_coverts("0") == "0"
        assert parse_old_greater_coverts("9") == "9"
        assert parse_old_greater_coverts("A") == "A"

    def test_parse_old_greater_coverts_invalid(self):
        with pytest.raises(EuringConstraintException):
            parse_old_greater_coverts("B")

    def test_parse_direction_allows_degrees(self):
        assert parse_direction("0") == 0
        assert parse_direction("359") == 359

    def test_parse_direction_allows_hyphens(self):
        assert parse_direction("---") is None
        assert parse_direction("-") is None

    def test_parse_place_code_allows_country_unknown_subdivision(self):
        assert parse_place_code("NL--") == "NL--"

    def test_parse_place_code_allows_numeric_subdivision(self):
        assert parse_place_code("ES00") == "ES00"

    def test_parse_place_code_rejects_invalid_pattern(self):
        with pytest.raises(EuringConstraintException):
            parse_place_code("N1--")

    def test_parse_direction_rejects_out_of_range(self):
        with pytest.raises(EuringConstraintException):
            parse_direction("360")

    def test_parse_direction_rejects_negative(self):
        with pytest.raises(EuringConstraintException):
            parse_direction("-1")

    def test_decode_fields_handles_non_string(self):
        record = EuringRecord.decode(None)
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_euring2000_format(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        record = EuringRecord.decode(module.EURING2000_EXAMPLES[1])
        assert record.display_format == "EURING2000"
        assert record.fields["ringing_scheme"]["value"] == "DER"

    def test_decode_euring2000_invalid_extra_data(self):
        record = EuringRecord.decode("AAB1234567890" + "9" * 90)
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_missing_required_field(self):
        record = EuringRecord.decode(
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|+0000000+0000000|1|9|99|0"
        )
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_invalid_coordinates(self):
        record = EuringRecord.decode(
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|invalidcoords|1|9|99|0|4"
        )
        assert any(error["field"] == "Geographical Co-ordinates" for error in record.errors["fields"])

    def test_decode_format_unknown(self):
        with pytest.raises(EuringConstraintException, match="Unknown format"):
            EuringRecord.decode("GBB", format="2000")

    def test_decode_format_conflict_pipe(self):
        record = EuringRecord.decode(_make_euring2000_plus_record(accuracy="1"), format="euring2000")
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_format_conflict_fixed_width(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        record = EuringRecord.decode(module.EURING2000_EXAMPLES[0], format="euring2000plus")
        assert record.errors["record"] or record.errors["fields"]

    def test_decode_invalid_species_format(self):
        record = EuringRecord.decode(_make_euring2000_plus_record_with_invalid_species(accuracy="1"))
        fields = [error["field"] for error in record.errors["fields"]]
        assert "Species Mentioned" in fields
        assert "Species Concluded" in fields

    def test_decode_euring2020_rejects_geo_with_lat_long(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="+0000000+0000000",
                lat_value="1.0000",
                lng_value="2.0000",
            )
        )
        assert any(error["field"] == "Geographical Co-ordinates" for error in record.errors["fields"])

    def test_decode_euring2020_requires_longitude_with_latitude(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="1.0000",
                lng_value="",
            )
        )
        assert any(error["field"] == "Longitude" for error in record.errors["fields"])

    def test_decode_euring2020_requires_latitude_with_longitude(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="",
                lng_value="2.0000",
            )
        )
        assert any(error["field"] == "Latitude" for error in record.errors["fields"])

    def test_decode_euring2020_latitude_out_of_range(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="90.0001",
                lng_value="2.0000",
            )
        )
        assert any(error["field"] == "Latitude" for error in record.errors["fields"])

    def test_decode_euring2020_longitude_out_of_range(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="10.0000",
                lng_value="180.0001",
            )
        )
        assert any(error["field"] == "Longitude" for error in record.errors["fields"])

    def test_decode_euring2020_latitude_too_many_decimals(self):
        record = EuringRecord.decode(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="10.00001",
                lng_value="2.0000",
            )
        )
        assert any(error["field"] == "Latitude" for error in record.errors["fields"])

    def test_decode_fields_returns_format(self):
        record = EuringRecord.decode(_make_euring2000_plus_record(accuracy="1"))
        assert record.format == "euring2000plus"

    def test_decode_euring2000_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2000_EXAMPLES:
            record = EuringRecord.decode(line)
            assert record.display_format == "EURING2000"
            assert not record.errors["record"]
            assert not record.errors["fields"]

    def test_decode_euring2000plus_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000plus_examples.py"
        spec = spec_from_file_location("euring2000plus_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2000PLUS_EXAMPLES:
            record = EuringRecord.decode(line)
            assert record.display_format == "EURING2000+"
            assert not record.errors["record"]
            assert not record.errors["fields"]

    def test_decode_euring2020_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
        spec = spec_from_file_location("euring2020_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2020_EXAMPLES:
            record = EuringRecord.decode(line)
            assert record.display_format == "EURING2020"
            assert not record.errors["record"]
            assert not record.errors["fields"]
