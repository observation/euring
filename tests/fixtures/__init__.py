"""Shared test fixtures for EURING records."""

from euring.fields import (
    EURING2000_KEYS,
    EURING2000PLUS_KEYS,
    EURING2020_KEYS,
)
from euring.formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, FORMAT_EURING2020

DEFAULT_TEST_VALUES = {
    # Default test data for a EURING record in key-value format
    "ringing_scheme": "GBB",
    "primary_identification_method": "A0",
    "identification_number": "1234567890",
    "verification_of_the_metal_ring": "0",
    "metal_ring_information": "1",
    "other_marks_information": "ZZ",
    "species_mentioned": "00010",
    "species_concluded": "00010",
    "manipulated": "N",
    "moved_before_recovery": "0",
    "catching_method": "M",
    "catching_lures": "U",
    "sex_mentioned": "U",
    "sex_concluded": "U",
    "age_mentioned": "2",
    "age_concluded": "2",
    "status": "U",
    "brood_size": "99",
    "pullus_age": "99",
    "accuracy_of_pullus_age": "0",
    "date": "01012024",
    "accuracy_of_date": "0",
    "time": "0000",
    "place_code": "AB00",
    "geographical_coordinates": "+0000000+0000000",
    "accuracy_of_coordinates": "1",
    "condition": "9",
    "circumstances": "99",
    "circumstances_presumed": "0",
    "euring_code_identifier": "4",
    "distance": "00000",
    "direction": "000",
    "elapsed_time": "00000",
    # EURING2000 fields stop here.
    "wing_length": "",
    "third_primary": "",
    "state_of_wing_point": "",
    "mass": "",
    "moult": "",
    "plumage_code": "",
    "hind_claw": "",
    "bill_length": "",
    "bill_method": "",
    "total_head_length": "",
    "tarsus": "",
    "tarsus_method": "",
    "tail_length": "",
    "tail_difference": "",
    "fat_score": "",
    "fat_score_method": "",
    "pectoral_muscle": "",
    "brood_patch": "",
    "primary_score": "",
    "primary_moult": "",
    "old_greater_coverts": "",
    "alula": "",
    "carpal_covert": "",
    "sexing_method": "",
    "place_name": "",
    "remarks": "",
    "reference": "",
    # EURING2000+ fields stop here.
    "latitude": "",
    "longitude": "",
    "current_place_code": "",
    "more_other_marks": "",
}


def _make_euring_record(data: dict, format: str) -> str:
    if format == FORMAT_EURING2000:
        keys = EURING2000_KEYS
        separator = ""
    elif format == FORMAT_EURING2000PLUS:
        keys = EURING2000PLUS_KEYS
        separator = "|"
    elif format == FORMAT_EURING2020:
        keys = EURING2020_KEYS
        separator = "|"
    else:
        raise ValueError(f"Unknown format: {format}")
    record_dict = {key: value for key, value in DEFAULT_TEST_VALUES.items() if key in keys}
    for key, value in data.items():
        assert key in keys, f"Invalid key: {key}"
        record_dict[key] = value
    return separator.join(record_dict.values())


def _make_euring2000_record(**kwargs) -> str:
    return _make_euring_record(kwargs, format=FORMAT_EURING2000)


def _make_euring2000plus_record(**kwargs) -> str:
    return _make_euring_record(kwargs, format=FORMAT_EURING2000PLUS)


def _make_euring2020_record(**kwargs) -> str:
    return _make_euring_record(kwargs, format=FORMAT_EURING2020)


def _make_euring2000plus_record_with_invalid_species(*, accuracy_of_coordinates: str = "1") -> str:
    return _make_euring2000plus_record(
        accuracy_of_coordinates=accuracy_of_coordinates,
        species_mentioned="12ABC",
        species_concluded="12ABC",
    )


def _make_euring2020_record_for_coords(**kwargs) -> str:
    return _make_euring2020_record(**kwargs)


def _make_euring2020_record_with_coords() -> str:
    return _make_euring2020_record(
        geographical_coordinates="." * 15,
        accuracy_of_coordinates="A",
        latitude="52.3760",
        longitude="4.9000",
    )
