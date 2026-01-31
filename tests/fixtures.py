"""Shared test fixtures for EURING records."""

from euring.fields import EURING2000_FIELDS, EURING_FIELDS

default_test_record_dict = {
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


def _field_index(key: str) -> int:
    for index, field in enumerate(EURING_FIELDS):
        if field.key == key:
            return index
    raise ValueError(f"Unknown key: {key}")


def _set_value(values: list[str], key: str, value: str) -> None:
    values[_field_index(key)] = value


def _make_euring2000_plus_record(*, accuracy: str) -> str:
    values = [default_test_record_dict[field.key] for field in EURING2000_FIELDS]
    values[_field_index("accuracy_of_coordinates")] = accuracy
    return "|".join(values)


def _make_euring2000_plus_record_with_invalid_species(*, accuracy: str = "1") -> str:
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
    _set_value(values, "geographical_coordinates", geo_value)
    _set_value(values, "latitude", lat_value)
    _set_value(values, "longitude", lng_value)
    return "|".join(values)


def _make_euring2020_record_with_coords() -> str:
    values = [""] * len(EURING_FIELDS)
    _set_value(values, "ringing_scheme", "GBB")
    _set_value(values, "primary_identification_method", "A0")
    _set_value(values, "identification_number", "1234567890")
    _set_value(values, "place_code", "AB00")
    _set_value(values, "accuracy_of_coordinates", "A")
    _set_value(values, "latitude", "52.3760")
    _set_value(values, "longitude", "4.9000")
    return "|".join(values)
