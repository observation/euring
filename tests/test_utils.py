"""Tests for EURING utility functions."""

import pytest

from euring import (
    EuringParseException,
    euring_dms_to_float,
    euring_float_to_dms,
    euring_identification_display_format,
    euring_identification_export_format,
    euring_lat_to_dms,
    euring_lng_to_dms,
    euring_scheme_export_format,
    euring_species_export_format,
)


class TestUtils:
    def test_dms_conversion(self):
        # Test DMS to float
        lat_decimal = euring_dms_to_float("+420500")
        lng_decimal = euring_dms_to_float("-0100203")
        assert abs(lat_decimal - 42.083333) < 1e-5
        assert abs(lng_decimal - (-10.034167)) < 1e-5

        # Test float to DMS (round trip)
        assert euring_lat_to_dms(lat_decimal) == "+420500"
        assert euring_lng_to_dms(lng_decimal) == "-0100203"
        dms = euring_float_to_dms(12.25)
        assert dms["quadrant"] == "+"
        assert dms["degrees"] == 12
        assert dms["minutes"] == 15
        assert dms["seconds"] == 0.0

    def test_dms_conversion_invalid(self):
        with pytest.raises(EuringParseException):
            euring_dms_to_float("bogus")

    def test_identification_format(self):
        assert euring_identification_display_format("ab.12-3") == "AB123"
        assert euring_identification_export_format("AB123") == "AB.....123"

    def test_scheme_format(self):
        assert euring_scheme_export_format("GB") == " GB"
        assert euring_scheme_export_format("ABCDE") == "ABC"

    def test_species_format(self):
        assert euring_species_export_format("123") == "00123"
        assert euring_species_export_format("12345") == "12345"
        with pytest.raises(ValueError):
            euring_species_export_format("123456")
        with pytest.raises(ValueError):
            euring_species_export_format("not-a-number")
