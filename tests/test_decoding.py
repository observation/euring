"""Tests for EURING record decoding."""

from collections import OrderedDict

import pytest

from euring import EuringDecoder, euring_decode_record
from euring.codes import lookup_date, lookup_geographical_coordinates, parse_geographical_coordinates
from euring.decoders import euring_decode_value
from euring.exceptions import EuringParseException
from euring.fields import EURING_FIELDS
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
        record = euring_decode_record(_make_euring2000_plus_record(accuracy="1"))
        assert record["format"] == "EURING2000+"
        assert record["scheme"] == "GBB"
        assert "data" in record
        assert "data_by_key" in record
        assert "Ringing Scheme" in record["data"]
        assert record["data_by_key"]["ringing_scheme"]["value"] == "GBB"

    def test_decode_euring2020_format(self):
        record = euring_decode_record(_make_euring2000_plus_record(accuracy="A"))
        assert record["format"] == "EURING2020"

    def test_decode_euring2020_format_hint_rejects_2000_plus(self):
        record = euring_decode_record(
            _make_euring2000_plus_record(accuracy="A"),
            format_hint="EURING2000+",
        )
        assert record["errors"]

    def test_decode_value_with_lookup(self):
        result = euring_decode_value("01012024", TYPE_INTEGER, length=8, lookup=lookup_date)
        assert result["value"] == "01012024"
        assert result["description"].isoformat() == "2024-01-01"

    def test_decode_value_invalid_type(self):
        with pytest.raises(EuringParseException):
            euring_decode_value("ABC", TYPE_INTEGER, length=3)

    def test_decode_value_optional_empty(self):
        result = euring_decode_value("", TYPE_INTEGER, min_length=0)
        assert result is None

    def test_decode_value_length_mismatch(self):
        with pytest.raises(EuringParseException):
            euring_decode_value("123", TYPE_INTEGER, length=2)

    def test_decode_value_min_length_error(self):
        with pytest.raises(EuringParseException):
            euring_decode_value("1", TYPE_INTEGER, min_length=2)

    def test_decode_value_max_length_error(self):
        with pytest.raises(EuringParseException):
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

    def test_decoder_handles_non_string(self):
        decoder = EuringDecoder(None)
        results = decoder.get_results()
        assert results["errors"]

    def test_parse_field_missing_optional_does_not_error(self):
        decoder = EuringDecoder("GBB")
        decoder.results = {"data": OrderedDict(), "data_by_key": OrderedDict()}
        decoder.errors = OrderedDict()
        decoder.parse_field([], 1, "Optional", key="optional", type=TYPE_INTEGER, required=False)
        assert decoder.errors == OrderedDict()

    def test_parse_field_sets_none_for_optional_empty(self):
        decoder = EuringDecoder("GBB")
        decoder.results = {"data": OrderedDict(), "data_by_key": OrderedDict()}
        decoder.errors = OrderedDict()
        decoder.parse_field([""], 0, "Optional", key="optional", type=TYPE_INTEGER, required=False)
        assert decoder.results["data_by_key"]["optional"] is None

    def test_decode_euring2000_format(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        record = euring_decode_record(module.EURING2000_EXAMPLES[1])
        assert record["format"] == "EURING2000"
        assert record["data"]["Ringing Scheme"]["value"] == "DER"

    def test_decode_euring2000_invalid_extra_data(self):
        record = euring_decode_record("AAB1234567890" + "9" * 90)
        assert record["errors"]

    def test_decode_missing_required_field(self):
        record = euring_decode_record(
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|+0000000+0000000|1|9|99|0"
        )
        assert record["errors"]

    def test_decode_invalid_coordinates(self):
        record = euring_decode_record(
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|invalidcoords|1|9|99|0|4"
        )
        assert "Geographical Co-ordinates" in record["errors"]

    def test_decode_format_hint_unknown(self):
        with pytest.raises(EuringParseException):
            EuringDecoder("GBB", format_hint="2000")

    def test_decode_format_hint_conflict_pipe(self):
        record = euring_decode_record(_make_euring2000_plus_record(accuracy="1"), format_hint="EURING2000")
        assert record["errors"]

    def test_decode_format_hint_conflict_fixed_width(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        record = euring_decode_record(module.EURING2000_EXAMPLES[0], format_hint="EURING2000+")
        assert record["errors"]

    def test_decode_invalid_species_format(self):
        record = euring_decode_record(_make_euring2000_plus_record_with_invalid_species(accuracy="1"))
        assert "Species Mentioned" in record["errors"]
        assert "Species Concluded" in record["errors"]

    def test_decode_euring2020_rejects_geo_with_lat_long(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="+0000000+0000000",
                lat_value="1.0000",
                lng_value="2.0000",
            )
        )
        assert "Geographical Co-ordinates" in record["errors"]

    def test_decode_euring2020_requires_longitude_with_latitude(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="1.0000",
                lng_value="",
            )
        )
        assert "Longitude" in record["errors"]

    def test_decode_euring2020_requires_latitude_with_longitude(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="",
                lng_value="2.0000",
            )
        )
        assert "Latitude" in record["errors"]

    def test_decode_euring2020_latitude_out_of_range(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="90.0001",
                lng_value="2.0000",
            )
        )
        assert "Latitude" in record["errors"]

    def test_decode_euring2020_longitude_out_of_range(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="10.0000",
                lng_value="180.0001",
            )
        )
        assert "Longitude" in record["errors"]

    def test_decode_euring2020_latitude_too_many_decimals(self):
        record = euring_decode_record(
            _make_euring2020_record_for_coords(
                geo_value="...............",
                lat_value="10.00001",
                lng_value="2.0000",
            )
        )
        assert "Latitude" in record["errors"]

    def test_decode_duplicate_field_name(self):
        decoder = EuringDecoder("GBB")
        decoder.results = {"data": {"Ringing Scheme": {"value": "GBB"}}}
        decoder.errors = {}
        decoder.parse_field(["GBB"], 0, "Ringing Scheme", type=TYPE_INTEGER, length=3)
        assert "Ringing Scheme" in decoder.errors

    def test_decode_euring2000_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000_examples.py"
        spec = spec_from_file_location("euring2000_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2000_EXAMPLES:
            record = euring_decode_record(line)
            assert record["format"] == "EURING2000"
            assert not record["errors"]

    def test_decode_euring2000plus_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2000plus_examples.py"
        spec = spec_from_file_location("euring2000plus_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2000PLUS_EXAMPLES:
            record = euring_decode_record(line)
            assert record["format"] == "EURING2000+"
            assert not record["errors"]

    def test_decode_euring2020_fixture_records(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "euring2020_examples.py"
        spec = spec_from_file_location("euring2020_examples", fixture_path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        for line in module.EURING2020_EXAMPLES:
            record = euring_decode_record(line)
            assert record["format"] == "EURING2020"
            assert not record["errors"]
