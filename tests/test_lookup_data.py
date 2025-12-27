"""Tests for data-backed lookup helpers."""

from euring.codes import lookup_place_code, lookup_ringing_scheme, lookup_species


def test_lookup_species_uses_packaged_data():
    assert lookup_species("00010") == "Struthio camelus"


def test_lookup_ringing_scheme_uses_packaged_data():
    assert lookup_ringing_scheme("AAC") == "Canberra, Australia"


def test_lookup_place_code_uses_packaged_data():
    assert lookup_place_code("AB00") == "Albania"
