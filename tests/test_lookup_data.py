"""Tests for data-backed lookup helpers."""

import pytest

from euring.codes import (
    lookup_date,
    lookup_description,
    lookup_geographical_coordinates,
    lookup_other_marks,
    lookup_place_code,
    lookup_place_details,
    lookup_ring_number,
    lookup_ringing_scheme,
    lookup_ringing_scheme_details,
    lookup_species,
    lookup_species_details,
    parse_geographical_coordinates,
    parse_latitude,
    parse_longitude,
)
from euring.exceptions import EuringParseException


def test_lookup_species_uses_packaged_data():
    assert lookup_species("00010") == "Struthio camelus"


def test_lookup_ringing_scheme_uses_packaged_data():
    assert lookup_ringing_scheme("AAC") == "Canberra, Australia"


def test_lookup_place_code_uses_packaged_data():
    assert lookup_place_code("AB00") == "Albania"


def test_lookup_place_details_uses_packaged_data():
    details = lookup_place_details("GR83")
    assert details["code"] == "Greece"
    assert details["region"] == "Makedonia"


def test_lookup_place_details_invalid():
    with pytest.raises(EuringParseException):
        lookup_place_details("XXXX")


def test_lookup_ringing_scheme_details_uses_packaged_data():
    details = lookup_ringing_scheme_details("AAC")
    assert details["ringing_centre"] == "Canberra"
    assert details["country"] == "Australia"


def test_lookup_species_details_uses_packaged_data():
    details = lookup_species_details("00010")
    assert details["name"] == "Struthio camelus"


def test_lookup_description_callable():
    assert lookup_description("x", lambda value: f"ok:{value}") == "ok:x"


def test_lookup_description_invalid():
    with pytest.raises(EuringParseException):
        lookup_description("bad", {"good": "value"})


def test_lookup_place_code_invalid():
    with pytest.raises(EuringParseException):
        lookup_place_code("ZZZZ")


def test_lookup_ringing_scheme_invalid():
    with pytest.raises(EuringParseException):
        lookup_ringing_scheme("ZZZ")


def test_lookup_species_invalid():
    with pytest.raises(EuringParseException):
        lookup_species("not-a-code")


def test_lookup_species_invalid_length():
    with pytest.raises(EuringParseException):
        lookup_species("1234")


def test_lookup_species_not_found():
    with pytest.raises(EuringParseException):
        lookup_species("12345")


def test_lookup_species_details_invalid_format():
    with pytest.raises(EuringParseException):
        lookup_species_details("not-a-code")


def test_lookup_date_invalid():
    with pytest.raises(EuringParseException):
        lookup_date("32132024")


def test_lookup_other_marks_invalid():
    with pytest.raises(EuringParseException):
        lookup_other_marks("$$")


def test_lookup_other_marks_missing_reference_data(monkeypatch):
    import euring.codes as codes

    monkeypatch.setattr(codes, "LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1", {})
    monkeypatch.setattr(codes, "LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2", {})
    with pytest.raises(EuringParseException):
        codes.lookup_other_marks("BB")


def test_lookup_other_marks_special_case():
    assert lookup_other_marks("MM") == "More than one mark present."


def test_lookup_other_marks_hyphen_second_char():
    description = lookup_other_marks("B-")
    assert "unknown if it was already present" in description


def test_lookup_ring_number_strips_dots():
    assert lookup_ring_number("AB.12.3") == "AB123"


def test_lookup_ring_number_rejects_trailing_dot():
    with pytest.raises(EuringParseException):
        lookup_ring_number("AB1234567.")


def test_lookup_geographical_coordinates_round_trip():
    coords = parse_geographical_coordinates("+420500-0044500")
    assert lookup_geographical_coordinates(coords) == "lat: 42.083333333333336 lng: -4.75"


def test_parse_geographical_coordinates_invalid():
    with pytest.raises(EuringParseException):
        parse_geographical_coordinates(None)


def test_parse_geographical_coordinates_invalid_range():
    with pytest.raises(EuringParseException):
        parse_geographical_coordinates("+420560-0044500")


def test_parse_latitude_invalid_value():
    with pytest.raises(EuringParseException):
        parse_latitude("bad")


def test_parse_latitude_too_many_decimals():
    with pytest.raises(EuringParseException):
        parse_latitude("1.00000")


def test_parse_longitude_out_of_range():
    with pytest.raises(EuringParseException):
        parse_longitude("181")
