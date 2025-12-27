"""Tests for data-backed lookup helpers."""

import pytest

from euring.codes import (
    lookup_description,
    lookup_place_code,
    lookup_place_details,
    lookup_ringing_scheme,
    lookup_ringing_scheme_details,
    lookup_species,
    lookup_species_details,
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
