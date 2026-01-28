"""Tests for EURING coordinate utilities."""

import pytest

from euring import EuringConstraintException
from euring.coordinates import (
    _decimal_to_euring_coordinate_components,
    _euring_coordinate_to_decimal,
    _lat_to_euring_coordinate,
    _lng_to_euring_coordinate,
    euring_coordinates_to_lat_lng,
    lat_lng_to_euring_coordinates,
)


def test_coordinate_conversion():
    lat_decimal = _euring_coordinate_to_decimal("+420500")
    lng_decimal = _euring_coordinate_to_decimal("-0100203")
    assert abs(lat_decimal - 42.083333) < 1e-5
    assert abs(lng_decimal - (-10.034167)) < 1e-5

    assert _lat_to_euring_coordinate(lat_decimal) == "+420500"
    assert _lng_to_euring_coordinate(lng_decimal) == "-0100203"

    dms = _decimal_to_euring_coordinate_components(12.25)
    assert dms["quadrant"] == "+"
    assert dms["degrees"] == 12
    assert dms["minutes"] == 15
    assert dms["seconds"] == 0.0


def test_coordinates_round_trip():
    value = "+420500-0100203"
    parsed = euring_coordinates_to_lat_lng(value)
    assert parsed["lat"] == pytest.approx(42.083333333333336)
    assert parsed["lng"] == pytest.approx(-10.034166666666666)
    assert lat_lng_to_euring_coordinates(parsed["lat"], parsed["lng"]) == value


def test_coordinate_conversion_invalid():
    with pytest.raises(EuringConstraintException):
        _euring_coordinate_to_decimal("bogus")
