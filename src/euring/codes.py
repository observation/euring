from datetime import date

from .exceptions import EuringParseException
from .utils import euring_dms_to_float

LOOKUP_PRIMARY_IDENTIFICATION_METHOD = {
    "A0": "Metal ring.",
    "B0": "Coloured or numbered leg ring(s).",
    "C0": "Coloured or numbered neck ring(s).",
    "D0": "Wing tags.",
    "E0": "Radio tracking device.",
    "F0": "Satellite tracking device.",
    "G0": "Transponder.",
    "H0": "Nasal mark(s).",
    "K0": "GPS loggers",
    "L0": "Geolocator loggers (recording daylight).",
    "R0": "Flight feather(s) stamped with a number.",
    "T0": "Body or wing painting or bleaching.",
}

LOOKUP_VERIFICATION_OF_THE_METAL_RING = {
    "0": "Ring not verified by scheme.",
    "1": "Ring verified by scheme.",
    "9": "Unknown if ring verified by scheme",
}

LOOKUP_METAL_RING_INFORMATION = {
    "0": "Metal ring is not present.",
    "1": "Metal ring added (where no metal ring was present), position (on tarsus or above) unknown or unrecorded.",
    "2": "Metal ring added (where no metal ring was present), definitely on tarsus.",
    "3": "Metal ring added (where no metal ring was present), definitely above tarsus.",
    "4": "Metal ring is already present.",
    "5": "Metal ring changed.",
    "6": "Metal ring removed and bird released alive (use code 4 if bird was dead)",
    "7": "Metal ring added, where a metal ring was already present.",
}

LOOKUP_OTHER_MARKS_INFORMATION_POSITION_1 = {
    "B": "Coloured or numbered leg-ring(s) or flags.",
    "C": "Coloured or numbered neck-ring(s).",
    "D": "Coloured or numbered wingtag(s).",
    "E": "Radio-tracking device.",
    "F": "Satellite-tracking device.",
    "G": "Transponder.",
    "H": "Nasal mark(s).",
    "K": "GPS logger.",
    "L": "Geolocator (light) logger.",
    "R": "Flight feathers stamped with the ring number.",
    "S": "Tape on the ring.",
    "T": "Dye mark (some part of plumage dyed, painted or bleached).",
}

LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2 = {
    "B": "mark added.",
    "C": "mark already present.",
    "D": "mark removed.",
    "E": "mark changed.",
    "-": "unknown.",
}

LOOKUP_OTHER_MARKS_INFORMATION_SPECIAL_CASES = {
    "MM": "More than one mark present.",
    "OM": "Other mark(s) present.",
    "OP": "Other permanent mark(s) present.",
    "OT": "Other temporary mark(s) present.",
    "ZZ": "No other marks present or not known to be present.",
}

LOOKUP_MANIPULATED = {
    "H": "Hand reared.",
    "K": "Fledging provoked.",
    "C": "Captive for more than 24 hours (code date of release).",
    "F": "Transported (more than 10 km) from co-ordinates coded.",
    "T": "Transported (more than 10 km) to co-ordinates coded.",
    "M": "Manipulated (injection, biopsy, radio- or satellite telemetry etc.).",
    "R": "Ringing accident.",
    "E": "Euthanised; bird humanely destroyed (reasons will be explained in Circumstances)",
    "P": "Poor condition when caught.",
    "N": "Normal, not manipulated bird.",
    "U": "Uncoded or unknown if manipulated or not.",
}

LOOKUP_MOVED_BEFORE_ENCOUNTER = {
    "0": "Not moved (excluding short movements, usually on foot, from catching place to ringing station).",
    "2": "Moved unintentionally by man or other agency.",
    "4": "Moved intentionally by man.",
    "6": "Moved by water (e.g. found on shoreline).",
    "9": "Uncoded or unknown if moved or not.",
}

LOOKUP_EURING_CODE_IDENTIFIER = {
    "0": "EURING Code Manual (1966). Directly coded (no translation).",
    "1": "Code Manual New EURING (1979), but translated from EURING Code Manual (1966).",
    "2": "Code Manual New EURING (1979). Directly coded (no translation of older codes).",
    "3": "Translated from earlier code but exact route uncertain",
    "4": "EURING exchange-code 2000 or 2000+, Directly coded (no translation of older codes)",
}

LOOKUP_CATCHING_METHOD = {
    "-": "not applicable, because there was no catching at all (for example 'found' or 'found dead' or 'shot')",
    "A": "Actively triggered trap (by ringer)",
    "B": "trap automatically triggered by Bird",
    "C": "Cannon net or rocket net",
    "D": "Dazzling",
    "F": "caught in Flight by anything other than a static mist net (e.g. flicked)",
    "G": "Nets put just under the water's surface and lifed up as waterfowl (ducks, Grebes, divers) swim over it",
    "H": "by Hand (with or without hook, noose etc.)",
    "L": "cLap net",
    "M": "Mist net",
    "N": "on Nest (any method)",
    "O": "any Other system",
    "P": "Phut net",
    "R": "Round up whilst flightless",
    "S": "ball-chatri or other Snare device",
    "T": "Helgoland Trap or duck decoy",
    "U": "Dutch net for PlUvialis apricaria",
    "V": "roosting in caVity",
    "W": "passive Walk-in / maze trap",
    "Z": "unknown",
}

LOOKUP_CATCHING_LURES = {
    "-": "not applicable, because there was no catching lure at all (for example 'found' or 'found dead' or 'shot')",
    "U": "unknown or not coded",
    "A": "food",
    "B": "water",
    "C": "light",
    "D": "decoy birds (alive)",
    "E": "decoy birds (stufed specimens or artificial decoy)",
    "F": "sound from tape recorder (same species)",
    "G": "sound from tape recorder (other species)",
    "H": "sound from mechanical whistle",
    "M": "more than one lure used",
    "N": "definitely no lure used",
}

LOOKUP_SEX = {"U": "Unknown", "M": "Male", "F": "Female"}

LOOKUP_AGE = {
    "0": "Age unknown, i.e. not recorded.",
    "1": "Pullus: nestling or chick, unable to fly freely, still able to be caught by hand.",
    "2": "Full-grown: able to fly freely but age otherwise unknown.",
    "3": "First-year: full-grown bird hatched in the breeding season of this calendar year.",
    "4": "Afer first-year: full-grown bird hatched before this calendar year; year of hatching otherwise unknown.",
    "5": "2nd year: a bird hatched last calendar year and now in its second calendar year.",
    "6": "Afer 2nd year: full-grown bird hatched before last calendar year; year of hatching otherwise unknown.",
    "7": "3rd year: a bird hatched two calendar years before, and now in its third calendar year.",
    "8": "After 3rd year: full-grown bird hatched >3 years ago (including present); year unknown otherwise.",
    "9": "4th year: a bird hatched three calendar years before, and now in its fourth calendar year.",
    "A": "After 4th year: a bird older than category 9 - age otherwise unknown.",
}

# Letters used to determine age past age code 9 and A, see lookup_age function below
LOOKUP_AGE_LETTERS = "BCDEFGHIJKLMNOPQRSTUVWXYZ"

LOOKUP_STATUS = {
    "-": "bird a pullus",
    "U": "Unknown or unrecorded.",
    "N": "Nesting or Breeding.",
    "R": "Roosting assemblage.",
    "K": "In Colony (not necessarily breeding but not pullus).",
    "M": "Moulting assemblage (whether bird moulting or not).",
    "T": "MoulTing.",
    "L": "Apparently a Local bird, but not breeding.",
    "W": "Apparently a bird Wintering in the locality.",
    "P": "On Passage - certainly not a local breeding nor wintering bird (includes birds atracted to lighthouses).",
    "S": "At Sea - birds on boats, lightships or oil rigs.",
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
        pos2 = LOOKUP_OTHER_MARKS_INFORMATION_POSITION_2[char2]
    except KeyError:
        raise EuringParseException(f'Value "{value}"is not a valid code combination.')
    # Description 'unknown' is quite unclear, so make the text better (as in example in manual)
    if char2 == "-":
        pos2 = "unknown if it was already present, removed, added or changed at this encounter"
    # Make the combined description a little prettier
    return "{pos1}, {pos2}.".format(pos1=pos1.strip("."), pos2=pos2.strip("."))


def lookup_species(value):
    """
    Species lookup - returns the code as is since we don't have database access.

    In a real application, this would look up the species name from a database.
    :param value:
    :return:
    """
    try:
        int(value)
        return f"Species code {value}"
    except ValueError:
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
    Place code lookup - returns the code as is since we don't have database access.

    In a real application, this would look up place information from a database.
    :param value:
    :return:
    """
    return f"Place code {value}"


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
    Ringing scheme lookup - returns the code as is since we don't have database access.

    In a real application, this would look up scheme information from a database.
    :param value:
    :return:
    """
    return f"Scheme {value}"


def lookup_age(value):
    v = f"{value}"
    try:
        return LOOKUP_AGE[v]
    except KeyError:
        pass
    try:
        index = LOOKUP_AGE_LETTERS.index(v)
    except ValueError:
        raise EuringParseException(f'Value "{value}" is not a valid EURING age code.')
    # 'B': '5th year: one year older than category 9 - age known exactly to the year.'
    age = index + 5
    older = index + 1
    return f"{age}th year: {older} year older than category 9 - age known exactly to the year."


def lookup_brood_size(value):
    if value == "--":
        return "bird is not a nestling"
    try:
        num = int(value)
    except ValueError:
        pass
    else:
        if num == 0:
            return "unknown or not coded."
        if num == 1:
            return "1 chick in the nest."
        if num <= 50:
            return f"{num} chicks in the nest."
        if num < 99:
            count = num - 50
            return f"{count} chicks in the nest from definitely more than one female, ({num} = {count} + 50)."
        if num == 99:
            return "chicks present but exact number in brood unknown/not recorded."
    raise EuringParseException(f'Value "{value}" is not a valid EURING brood size code.')


def lookup_pullus_age(value):
    if value == "--":
        return "bird is not a pullus"
    try:
        num = int(value)
    except ValueError:
        pass
    else:
        if num == 1:
            return "pullus age 1 day."
        if num < 99:
            return f"pullus age {num} days."
        if num == 99:
            return "pullus age not recorded"
    raise EuringParseException(f'Value "{value}" is not a valid EURING brood size code.')
