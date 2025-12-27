from datetime import date

from .data import (
    load_code_map,
    load_named_code_map,
    load_other_marks_data,
    load_place_map,
    load_scheme_map,
    load_species_map,
)
from .exceptions import EuringParseException
from .utils import euring_dms_to_float


LOOKUP_EURING_CODE_IDENTIFIER = {
    "0": "EURING Code Manual (1966). Directly coded (no translation).",
    "1": "Code Manual New EURING (1979), but translated from EURING Code Manual (1966).",
    "2": "Code Manual New EURING (1979). Directly coded (no translation of older codes).",
    "3": "Translated from earlier code but exact route uncertain",
    "4": "EURING exchange-code 2000 or 2000+, Directly coded (no translation of older codes)",
}


LOOKUP_CONDITION = {
    "0": "Condition completely unknown.",
    "1": "Dead but no information on how recently the bird had died (or been killed).",
    "2": "Freshly dead - within about a week.",
    "3": "Not freshly dead - information available that it had been dead for more than about a week.",
    "4": "Found sick, wounded, unhealthy etc. and known to have been released.",
    "5": "Found sick, wounded, unhealthy etc. and not released or not known if released.",
    "6": "Alive and probably healthy but taken into captivity.",
    "7": "Alive and probably healthy and certainly released.",
    "8": "Alive and probably healthy and released by a ringer.",
    "9": "Alive and probably healthy but ultimate fate of bird is not known.",
}


def _catching_method_code_filter(code: str) -> bool:
    return code == "-" or len(code) == 1


LOOKUP_PRIMARY_IDENTIFICATION_METHOD = load_code_map("primary_identification_method.json")
LOOKUP_VERIFICATION_OF_THE_METAL_RING = load_code_map("verification_of_the_metal_ring.json")
LOOKUP_METAL_RING_INFORMATION = load_code_map("metal_ring_information.json")
_OTHER_MARKS_DATA = load_other_marks_data()
LOOKUP_OTHER_MARKS_INFORMATION_SPECIAL_CASES = (
    _OTHER_MARKS_DATA["special_cases"] if _OTHER_MARKS_DATA else {}
)
LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1 = (
    _OTHER_MARKS_DATA["first_character"] if _OTHER_MARKS_DATA else {}
)
LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2 = (
    _OTHER_MARKS_DATA["second_character"] if _OTHER_MARKS_DATA else {}
)

LOOKUP_MANIPULATED = load_code_map("manipulated.json")
LOOKUP_MOVED_BEFORE_ENCOUNTER = load_code_map("moved_before_the_encounter.json")
LOOKUP_CATCHING_METHOD = load_code_map("catching_method.json", code_filter=_catching_method_code_filter)
LOOKUP_CATCHING_LURES = load_code_map("catching_lures.json")
LOOKUP_SEX = load_code_map("sex.json")
LOOKUP_AGE = load_code_map("age.json")
LOOKUP_STATUS = load_code_map("status.json")
LOOKUP_BROOD_SIZE = load_code_map("brood_size.json")
LOOKUP_PULLUS_AGE = load_code_map("pullus_age.json")
LOOKUP_ACCURACY_PULLUS_AGE = load_code_map("accuracy_of_pullus_age.json")
LOOKUP_CIRCUMSTANCES = load_code_map("circumstances.json")
_SPECIES_LOOKUP = load_species_map()
_SCHEME_LOOKUP = load_scheme_map()
_PLACE_LOOKUP = load_place_map()


def lookup_description(value, lookup):
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
        raise EuringParseException(f'Value "{value}" is not a valid EURING species code.')
    raise EuringParseException(f'Value "{value}" is not a valid EURING species code.')


def parse_geographical_coordinates(value):
    # +420500-0044500
    try:
        lat = value[:7]
        lng = value[7:]
    except (TypeError, IndexError):
        raise EuringParseException(f'Value "{value}" is not a valid set of coordinates.')
    result = dict(lat=euring_dms_to_float(lat), lng=euring_dms_to_float(lng))
    return result


def lookup_geographical_coordinates(value):
    return "lat: {lat} lng: {lng}".format(**value)


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


def lookup_date(value):
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


def lookup_age(value):
    v = f"{value}"
    return lookup_description(v, LOOKUP_AGE)


def lookup_brood_size(value):
    v = f"{value}"
    return lookup_description(v, LOOKUP_BROOD_SIZE)


def lookup_pullus_age(value):
    v = f"{value}"
    return lookup_description(v, LOOKUP_PULLUS_AGE)
