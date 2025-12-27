import re

from .exceptions import EuringParseException


def euring_dms_to_float(value):
    """Convert EURING DMS coordinate text into decimal degrees."""
    try:
        seconds = value[-2:]
        minutes = value[-4:-2]
        degrees = value[:-4]
        result = float(degrees)
        negative = result < 0
        result = abs(result) + (float(minutes) / 60) + (float(seconds) / 3600)
        if negative:
            result = -result
    except (IndexError, ValueError):
        raise EuringParseException('Could not parse coordinate "{value}" to decimal.')
    return result


def euring_float_to_dms(value, round_seconds=False):
    """
    Convert a Decimal Degree Value into Degrees Minute Seconds Notation.

    Pass value as double
    type = {Latitude or Longitude} as string

    returns a dict with quadrant, degreees, minutes, seconds
    created by: anothergisblog.blogspot.com
    modified by: Dylan Verheul
    """
    degrees = int(value)
    submin = abs((value - int(value)) * 60)
    minutes = int(submin)
    seconds = abs((submin - int(submin)) * 60)
    if degrees < 0:
        quadrant = "-"
    else:
        quadrant = "+"  # includes 0
    if round_seconds:
        seconds = int(round(seconds))
    return {"quadrant": quadrant, "degrees": degrees, "minutes": minutes, "seconds": seconds}


def euring_coord_to_dms(value, degrees_pos):
    """Format a decimal coordinate into EURING DMS text with fixed degree width."""
    dms = euring_float_to_dms(value, round_seconds=True)
    return "{quadrant}{degrees}{minutes}{seconds}".format(
        quadrant=dms["quadrant"],
        degrees="{}".format(abs(dms["degrees"])).zfill(degrees_pos),
        minutes="{}".format(dms["minutes"]).zfill(2),
        seconds="{}".format(dms["seconds"]).zfill(2),
    )


def euring_lat_to_dms(value):
    """Convert a latitude in decimal degrees into EURING DMS text."""
    return euring_coord_to_dms(value, degrees_pos=2)


def euring_lng_to_dms(value):
    """Convert a longitude in decimal degrees into EURING DMS text."""
    return euring_coord_to_dms(value, degrees_pos=3)


def euring_identification_display_format(euring_number):
    """
    Return EURING number in upper case, with anything that is not a letter or digit removed.

    :param euring_number:
    :return:
    """
    # Convert to uppercase unicode
    result = f"{euring_number}".upper()
    # Remove everything that is not a digit (0-9) or letter (A-Z)
    return re.sub(r"[^A-Z0-9]", "", result)


def euring_identification_export_format(euring_number):
    """
    Return EURING code formatted for display and with added internal padding (dots) up to length 10.

    :param euring_number:
    :param length:
    :return:
    """
    # Set length
    length = 10
    # Remove any character that is not a letter or a digit, and convert to upper case
    text = euring_identification_display_format(euring_number)
    # If we are at at the requested length, we're done
    text_length = len(text)
    if text_length == length:
        return text
    if text_length > length:
        return text[:length]
        # TODO: Maybe raise ValueError('EURING number too long after euring_display_format '
        #       '({} {}).'.format(euring_number, text))
    # We need length - text_length dots to fill us up
    dots = "." * (length - text_length)
    # Insert dots before the rightmost series of digits
    result = ""
    digit_seen = False
    done = False
    for c in reversed(text):
        if not done:
            if c.isdigit():
                digit_seen = True
            elif digit_seen:
                result = dots + result
                done = True
        result = c + result
    if not done:
        result = dots + result
    return result


def euring_scheme_export_format(scheme_code):
    """
    Proper export format for a scheme code.

    :param scheme_code: Scheme code (string)
    :return: Formatted scheme code
    """
    result = f"{scheme_code}".upper()
    return result[0:3].rjust(3)


def euring_species_export_format(species_code):
    """
    Proper export format for EURING species code.

    :param species_code:
    :return:
    """
    if not species_code:
        return "00000"
    # Must be a valid integer
    try:
        result = int(species_code)
    except ValueError:
        raise ValueError("Invalid EURING species code.")
    # Now to unicode
    result = f"{species_code}"
    # Check the length
    if len(result) > 5:
        raise ValueError("EURING species code too long.")
    # Pad with zeroes and return result
    return result.zfill(5)
