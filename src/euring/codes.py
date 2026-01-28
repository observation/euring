import re
from collections.abc import Callable, Mapping
from datetime import date
from typing import Any

from .coordinates import _validate_euring_coordinates, euring_coordinates_to_lat_lng
from .data import (
    load_code_map,
    load_other_marks_data,
    load_place_details,
    load_place_map,
    load_scheme_details,
    load_scheme_map,
    load_species_details,
    load_species_map,
)
from .exceptions import EuringConstraintException, EuringLookupException
from .utils import is_all_hyphens

LOOKUP_EURING_CODE_IDENTIFIER = load_code_map("euring_code_identifier")
LOOKUP_CONDITION = load_code_map("condition")


def _catching_method_code_filter(code: str) -> bool:
    """Filter catching method codes to valid entries."""
    return code == "-" or len(code) == 1


LOOKUP_PRIMARY_IDENTIFICATION_METHOD = load_code_map("primary_identification_method")
LOOKUP_VERIFICATION_OF_THE_METAL_RING = load_code_map("verification_of_the_metal_ring")
LOOKUP_METAL_RING_INFORMATION = load_code_map("metal_ring_information")
_OTHER_MARKS_DATA = load_other_marks_data()
LOOKUP_OTHER_MARKS_INFORMATION_SPECIAL_CASES = _OTHER_MARKS_DATA["special_cases"] if _OTHER_MARKS_DATA else {}
LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1 = _OTHER_MARKS_DATA["first_character"] if _OTHER_MARKS_DATA else {}
LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2 = _OTHER_MARKS_DATA["second_character"] if _OTHER_MARKS_DATA else {}

LOOKUP_MANIPULATED = load_code_map("manipulated")
LOOKUP_MOVED_BEFORE_ENCOUNTER = load_code_map("moved_before_the_encounter")
LOOKUP_CATCHING_METHOD = load_code_map("catching_method", code_filter=_catching_method_code_filter)
LOOKUP_CATCHING_LURES = load_code_map("catching_lures")
LOOKUP_STATE_OF_WING_POINT = load_code_map("state_of_wing_point")
LOOKUP_MOULT = load_code_map("moult")
LOOKUP_PLUMAGE_CODE = load_code_map("plumage_code")
LOOKUP_BILL_METHOD = load_code_map("bill_method")
LOOKUP_TARSUS_METHOD = load_code_map("tarsus_method")
LOOKUP_FAT_SCORE_METHOD = load_code_map("fat_score_method")
LOOKUP_PECTORAL_MUSCLE_SCORE = load_code_map("pectoral_muscle_score")
LOOKUP_BROOD_PATCH = load_code_map("brood_patch")
LOOKUP_CARPAL_COVERT = load_code_map("carpal_covert")
LOOKUP_SEXING_METHOD = load_code_map("sexing_method")
LOOKUP_SEX = load_code_map("sex")
LOOKUP_AGE = load_code_map("age")
LOOKUP_STATUS = load_code_map("status")
LOOKUP_BROOD_SIZE = load_code_map("brood_size")
LOOKUP_PULLUS_AGE = load_code_map("pullus_age")
LOOKUP_ACCURACY_PULLUS_AGE = load_code_map("accuracy_of_pullus_age")
LOOKUP_CIRCUMSTANCES = load_code_map("circumstances")
LOOKUP_ACCURACY_OF_COORDINATES = load_code_map("accuracy_of_coordinates")
LOOKUP_ACCURACY_OF_DATE = load_code_map("accuracy_of_date")
LOOKUP_CIRCUMSTANCES_PRESUMED = load_code_map("circumstances_presumed")
_SPECIES_LOOKUP = load_species_map()
_SCHEME_LOOKUP = load_scheme_map()
_PLACE_LOOKUP = load_place_map()
_SPECIES_DETAILS = load_species_details()
_SCHEME_DETAILS = load_scheme_details()
_PLACE_DETAILS = load_place_details()
_RINGING_SCHEME_PATTERN = re.compile(r"^[A-Z]{3}$")
_PLACE_CODE_PATTERN = re.compile(r"^[A-Z]{2}([A-Z]{2}|[0-9]{2}|--)$")


def lookup_description(value: str, lookup: Mapping[str, str] | Callable[[str], str] | None) -> str | None:
    """Resolve a code value to its description using a mapping or callable."""
    if lookup is None:
        return None
    if callable(lookup):
        return lookup(value)
    try:
        return lookup[value]
    except KeyError:
        raise EuringLookupException(f'Value "{value}"is not a valid code.')


def lookup_ring_number(value: str) -> str:
    """Validate padding dots and return the unpadded identification number."""
    if not value:
        return value
    # Per the manual, dots are always inserted immediately to the left of the
    # rightmost contiguous run of digits.
    if "." not in value:
        return value

    matches = list(re.finditer(r"\d+", value))
    if matches:
        rightmost_digits = matches[-1]
        prefix = value[: rightmost_digits.start()]
        # Dots may appear in the prefix, but only as a single trailing block.
        if "." in prefix.rstrip("."):
            raise EuringConstraintException(
                "Identification number (ring) padding dots must be immediately before the rightmost digits."
            )
    else:
        # No digits: fall back to allowing only leading padding dots.
        trimmed = value.lstrip(".")
        if "." in trimmed:
            raise EuringConstraintException(
                "Identification number (ring) padding dots must be leading when no digits are present."
            )

    return value.replace(".", "")


def lookup_other_marks(value: str) -> str:
    """
    Lookup combined code for field "Other Marks Information" EURING2000+ Manual Page 8.

    :param value: Value to look up
    :return: Description found
    """
    if not LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1 or not LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2:
        raise EuringLookupException("Other marks reference data is not available.")
    # First see if it's a special case
    try:
        return LOOKUP_OTHER_MARKS_INFORMATION_SPECIAL_CASES[value]
    except KeyError:
        pass
    # Match first and second character
    try:
        char1 = value[0]
        pos1 = LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1[char1]
        char2 = value[1]
        if char2 == "-":
            pos2 = "unknown if it was already present, removed, added or changed at this encounter"
        else:
            pos2 = LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2[char2]
    except KeyError:
        raise EuringLookupException(f'Value "{value}"is not a valid code combination.')
    # Make the combined description a little prettier
    return "{pos1}, {pos2}.".format(pos1=pos1.strip("."), pos2=pos2.strip("."))


def lookup_species(value: str | int) -> str:
    """
    Species lookup - uses packaged reference data when available.

    :param value:
    :return:
    """
    value_str = f"{value}"
    result = _SPECIES_LOOKUP.get(value_str)
    if result:
        return result
    try:
        int(value_str)
    except ValueError:
        raise EuringConstraintException(f'Value "{value}" is not a valid EURING species code format.')
    if len(value_str) != 5:
        raise EuringConstraintException(f'Value "{value}" is not a valid EURING species code format.')
    raise EuringLookupException(f'Value "{value}" is a valid EURING species code format but was not found.')


def lookup_species_details(value: str | int) -> dict[str, Any]:
    """Return the full species record for a EURING species code."""
    value_str = f"{value}"
    result = _SPECIES_DETAILS.get(value_str)
    if result:
        return result
    try:
        int(value_str)
    except ValueError:
        raise EuringConstraintException(f'Value "{value}" is not a valid EURING species code format.')
    if len(value_str) != 5:
        raise EuringConstraintException(f'Value "{value}" is not a valid EURING species code format.')
    raise EuringLookupException(f'Value "{value}" is a valid EURING species code format but was not found.')


def parse_geographical_coordinates(value: str | None) -> dict[str, float] | None:
    """Parse EURING coordinate text into latitude/longitude decimal values."""
    # +420500-0044500
    if value is None:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    if value == "." * 15:
        return None
    _validate_euring_coordinates(value)
    try:
        return euring_coordinates_to_lat_lng(value)
    except (TypeError, IndexError):
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')


def lookup_geographical_coordinates(value: dict[str, float] | None) -> str | None:
    """Format parsed coordinates into a human-readable string."""
    if value is None:
        return None
    return "lat: {lat} lng: {lng}".format(**value)


def parse_latitude(value: str) -> float:
    """Parse a decimal latitude with manual range/precision limits."""
    return _parse_decimal_coordinate(value, max_abs=90, max_decimals=4, field_name="Latitude")


def parse_longitude(value: str) -> float:
    """Parse a decimal longitude with manual range/precision limits."""
    return _parse_decimal_coordinate(value, max_abs=180, max_decimals=4, field_name="Longitude")


def parse_direction(value: str) -> int | None:
    """Parse and validate a direction in degrees (000-359) or hyphen placeholder."""
    if value is None:
        raise EuringConstraintException(f'Value "{value}" is not a valid direction.')
    value_str = f"{value}"
    if is_all_hyphens(value_str):
        return None
    if value_str.startswith("-"):
        raise EuringConstraintException(f'Value "{value}" is not a valid direction.')
    try:
        parsed = int(value_str)
    except (TypeError, ValueError):
        raise EuringConstraintException(f'Value "{value}" is not a valid direction.')
    if parsed < 0 or parsed > 359:
        raise EuringConstraintException("Direction must be between 0 and 359 degrees.")
    return parsed


def parse_place_code(value: str) -> str:
    """Validate the place code pattern (AA##, AAAA, or AA--)."""
    value_str = f"{value}"
    if not _PLACE_CODE_PATTERN.match(value_str):
        raise EuringConstraintException(f'Value "{value}" is not a valid place code format.')
    return value_str


def _parse_decimal_coordinate(value: str, *, max_abs: int, max_decimals: int, field_name: str) -> float:
    """Parse and validate a decimal latitude/longitude string."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise EuringConstraintException(f'Value "{value}" is not a valid {field_name}.')
    if abs(parsed) > max_abs:
        raise EuringConstraintException(f"{field_name} must be between -{max_abs} and {max_abs}.")
    if "." in value:
        decimal_part = value.split(".", 1)[1]
        if len(decimal_part) > max_decimals:
            raise EuringConstraintException(f"{field_name} must have at most {max_decimals} decimal places.")
    return parsed


def parse_old_greater_coverts(value: str) -> str:
    """Validate Old Greater Coverts codes (0-9 or A)."""
    if value not in {str(num) for num in range(10)} | {"A"}:
        raise EuringConstraintException(f'Value "{value}" is not a valid Old Greater Coverts code.')
    return value


def lookup_place_code(value: str | int) -> str:
    """
    Place code lookup - uses packaged reference data when available.

    :param value:
    :return:
    """
    value_str = f"{value}"
    result = _PLACE_LOOKUP.get(value_str)
    if result:
        return result
    raise EuringLookupException(f'Value "{value}" is not a valid EURING place code.')


def lookup_place_details(value: str | int) -> dict[str, Any]:
    """Return the full place record for a EURING place code."""
    value_str = f"{value}"
    result = _PLACE_DETAILS.get(value_str)
    if result:
        return result
    raise EuringLookupException(f'Value "{value}" is not a valid EURING place code.')


def lookup_date(value: str | int) -> date:
    """Parse a EURING date string into a datetime.date."""
    value_str = f"{value}"
    if value_str.isdigit() and len(value_str) < 8:
        value_str = value_str.zfill(8)
    try:
        day = int(value_str[0:2])
        month = int(value_str[2:4])
        year = int(value_str[4:8])
        return date(year, month, day)
    except (IndexError, ValueError):
        raise EuringConstraintException(f'Value "{value}" is not a valid EURING date.')


def parse_date(value: str) -> str:
    """Validate that date placeholders are not used, then return the raw value."""
    if is_all_hyphens(value):
        raise EuringConstraintException("Date cannot be all dashes; provide an estimated real date instead.")
    return value


def lookup_ringing_scheme(value: str | int) -> str:
    """
    Ringing scheme lookup - uses packaged reference data when available.

    Per the EURING manual, ringing schemes are alphabetic, three-character codes.
    The packaged table may not include every valid scheme, so we accept unknown
    codes that match the documented pattern instead of raising a hard error.

    :param value:
    :return:
    """
    value_str = f"{value}".upper()
    result = _SCHEME_LOOKUP.get(value_str)
    if result:
        return result
    if _RINGING_SCHEME_PATTERN.match(value_str):
        return f"Unknown ringing scheme ({value_str})."
    raise EuringLookupException(f'Value "{value}" is not a valid EURING ringing scheme code.')


def lookup_ringing_scheme_details(value: str | int) -> dict[str, Any]:
    """Return the full scheme record for a EURING ringing scheme code."""
    value_str = f"{value}"
    result = _SCHEME_DETAILS.get(value_str)
    if result:
        return result
    raise EuringLookupException(f'Value "{value}" is not a valid EURING ringing scheme code.')


def lookup_age(value: str | int) -> str | None:
    """Look up the EURING age description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_AGE)


def lookup_brood_size(value: str | int) -> str | None:
    """Look up the EURING brood size description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_BROOD_SIZE)


def lookup_pullus_age(value: str | int) -> str | None:
    """Look up the EURING pullus age description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_PULLUS_AGE)
