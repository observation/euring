from datetime import date

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
from .exceptions import EuringParseException
from .utils import euring_dms_to_float

LOOKUP_EURING_CODE_IDENTIFIER = load_code_map("euring_code_identifier")
LOOKUP_CONDITION = load_code_map("condition")


def _catching_method_code_filter(code: str) -> bool:
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
LOOKUP_SEX = load_code_map("sex")
LOOKUP_AGE = load_code_map("age")
LOOKUP_STATUS = load_code_map("status")
LOOKUP_BROOD_SIZE = load_code_map("brood_size")
LOOKUP_PULLUS_AGE = load_code_map("pullus_age")
LOOKUP_ACCURACY_PULLUS_AGE = load_code_map("accuracy_of_pullus_age")
LOOKUP_CIRCUMSTANCES = load_code_map("circumstances")
_SPECIES_LOOKUP = load_species_map()
_SCHEME_LOOKUP = load_scheme_map()
_PLACE_LOOKUP = load_place_map()
_SPECIES_DETAILS = load_species_details()
_SCHEME_DETAILS = load_scheme_details()
_PLACE_DETAILS = load_place_details()


def lookup_description(value, lookup):
    """Resolve a code value to its description using a mapping or callable."""
    if lookup is None:
        return None
    if callable(lookup):
        return lookup(value)
    try:
        return lookup[value]
    except KeyError:
        raise EuringParseException(f'Value "{value}"is not a valid code.')


def lookup_ring_number(value):
    """Lookup a ring number Just strip the dots from the EURING codes."""
    if value and value.endswith("."):
        raise EuringParseException("Identification number (ring) cannot end with a dot.")
    return value.replace(".", "")


def lookup_other_marks(value):
    """
    Lookup combined code for field "Other Marks Information" EURING2000+ Manual Page 8.

    :param value: Value to look up
    :return: Description found
    """
    if not LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1 or not LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2:
        raise EuringParseException("Other marks reference data is not available.")
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
        raise EuringParseException(f'Value "{value}"is not a valid code combination.')
    # Make the combined description a little prettier
    return "{pos1}, {pos2}.".format(pos1=pos1.strip("."), pos2=pos2.strip("."))


def lookup_species(value):
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
        raise EuringParseException(f'Value "{value}" is not a valid EURING species code format.')
    if len(value_str) != 5:
        raise EuringParseException(f'Value "{value}" is not a valid EURING species code format.')
    raise EuringParseException(f'Value "{value}" is a valid EURING species code format but was not found.')


def lookup_species_details(value):
    """Return the full species record for a EURING species code."""
    value_str = f"{value}"
    result = _SPECIES_DETAILS.get(value_str)
    if result:
        return result
    try:
        int(value_str)
    except ValueError:
        raise EuringParseException(f'Value "{value}" is not a valid EURING species code format.')
    if len(value_str) != 5:
        raise EuringParseException(f'Value "{value}" is not a valid EURING species code format.')
    raise EuringParseException(f'Value "{value}" is a valid EURING species code format but was not found.')


def parse_geographical_coordinates(value):
    """Parse EURING coordinate text into latitude/longitude decimal values."""
    # +420500-0044500
    if value is None:
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    if value == "." * 15:
        return None
    _validate_dms_component(value[:7], degrees_digits=2, max_degrees=90)
    _validate_dms_component(value[7:], degrees_digits=3, max_degrees=180)
    try:
        lat = value[:7]
        lng = value[7:]
    except (TypeError, IndexError):
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    result = dict(lat=euring_dms_to_float(lat), lng=euring_dms_to_float(lng))
    return result


def lookup_geographical_coordinates(value):
    """Format parsed coordinates into a human-readable string."""
    if value is None:
        return None
    return "lat: {lat} lng: {lng}".format(**value)


def parse_latitude(value):
    """Parse a decimal latitude with manual range/precision limits."""
    return _parse_decimal_coordinate(value, max_abs=90, max_decimals=4, field_name="Latitude")


def parse_longitude(value):
    """Parse a decimal longitude with manual range/precision limits."""
    return _parse_decimal_coordinate(value, max_abs=180, max_decimals=4, field_name="Longitude")


def _parse_decimal_coordinate(value, *, max_abs, max_decimals, field_name):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise EuringParseException(f'Value "{value}" is not a valid {field_name}.')
    if abs(parsed) > max_abs:
        raise EuringParseException(f"{field_name} must be between -{max_abs} and {max_abs}.")
    if "." in value:
        decimal_part = value.split(".", 1)[1]
        if len(decimal_part) > max_decimals:
            raise EuringParseException(f"{field_name} must have at most {max_decimals} decimal places.")
    return parsed


def _validate_dms_component(value, *, degrees_digits, max_degrees):
    if value is None:
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    expected_length = 1 + degrees_digits + 2 + 2
    if len(value) != expected_length:
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    sign = value[0]
    if sign not in {"+", "-"}:
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    degrees = value[1 : 1 + degrees_digits]
    minutes = value[1 + degrees_digits : 1 + degrees_digits + 2]
    seconds = value[1 + degrees_digits + 2 :]
    if not (degrees.isdigit() and minutes.isdigit() and seconds.isdigit()):
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    if int(degrees) > max_degrees or int(minutes) > 59 or int(seconds) > 59:
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')


def lookup_place_code(value):
    """
    Place code lookup - uses packaged reference data when available.

    :param value:
    :return:
    """
    value_str = f"{value}"
    result = _PLACE_LOOKUP.get(value_str)
    if result:
        return result
    raise EuringParseException(f'Value "{value}" is not a valid EURING place code.')


def lookup_place_details(value):
    """Return the full place record for a EURING place code."""
    value_str = f"{value}"
    result = _PLACE_DETAILS.get(value_str)
    if result:
        return result
    raise EuringParseException(f'Value "{value}" is not a valid EURING place code.')


def lookup_date(value):
    """Parse a EURING date string into a datetime.date."""
    try:
        day = int(value[0:2])
        month = int(value[2:4])
        year = int(value[4:8])
        return date(year, month, day)
    except (IndexError, ValueError):
        raise EuringParseException(f'Value "{value}" is not a valid EURING date.')


def lookup_ringing_scheme(value):
    """
    Ringing scheme lookup - uses packaged reference data when available.

    :param value:
    :return:
    """
    value_str = f"{value}"
    result = _SCHEME_LOOKUP.get(value_str)
    if result:
        return result
    raise EuringParseException(f'Value "{value}" is not a valid EURING ringing scheme code.')


def lookup_ringing_scheme_details(value):
    """Return the full scheme record for a EURING ringing scheme code."""
    value_str = f"{value}"
    result = _SCHEME_DETAILS.get(value_str)
    if result:
        return result
    raise EuringParseException(f'Value "{value}" is not a valid EURING ringing scheme code.')


def lookup_age(value):
    """Look up the EURING age description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_AGE)


def lookup_brood_size(value):
    """Look up the EURING brood size description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_BROOD_SIZE)


def lookup_pullus_age(value):
    """Look up the EURING pullus age description for a code."""
    v = f"{value}"
    return lookup_description(v, LOOKUP_PULLUS_AGE)
