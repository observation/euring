import re
from typing import Any

__all__ = [
    "euring_identification_display_format",
    "euring_identification_export_format",
    "euring_scheme_export_format",
    "euring_species_export_format",
]


def is_empty(value: Any) -> bool:
    """Return True when a field value should be treated as empty."""
    return value in (None, "")


def is_all_hyphens(value: str) -> bool:
    """Return True when a non-empty string consists of only hyphens."""
    return bool(value) and set(value) == {"-"}


def euring_identification_display_format(euring_number: Any) -> str:
    """
    Return EURING number in upper case, with anything that is not a letter or digit removed.

    :param euring_number:
    :return:
    """
    # Convert to uppercase unicode
    result = f"{euring_number}".upper()
    # Remove everything that is not a digit (0-9) or letter (A-Z)
    return re.sub(r"[^A-Z0-9]", "", result)


def euring_identification_export_format(euring_number: Any) -> str:
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


def euring_scheme_export_format(scheme_code: Any) -> str:
    """
    Proper export format for a scheme code.

    :param scheme_code: Scheme code (string)
    :return: Formatted scheme code
    """
    result = f"{scheme_code}".upper()
    return result[0:3].rjust(3)


def euring_species_export_format(species_code: str | int | None) -> str:
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
