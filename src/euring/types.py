import re

TYPE_ALPHABETIC = "Alphabetic"
TYPE_ALPHANUMERIC = "Alphanumeric"
TYPE_INTEGER = "Integer"
TYPE_NUMERIC = "Numeric"
TYPE_NUMERIC_SIGNED = "NumericSigned"
TYPE_TEXT = "Text"

# Only capital letters
# Allow an empty string
# Allow dash (-) because it is allowed in Other Marks Information
RE_ALPHABETIC = r"^[A-Z\-]*$"

# All capital letters, all digits, and allow +-/*
# Also allow an empty string
# Allow a dash (-) because Alphabetic allows dashes
# Allow a dot (.) because it is allowed in Identification number (ring)
RE_ALPHANUMERIC = r"^[A-Z0-9\+\-\/\*\.]*$"

# Allow all digits OR all dashes (=None), do not allow empty string
RE_INTEGER = r"^[0-9]+$|^\-+$"

# Allow anything that consists of digits
# Allow one period somewhere in the string, but not at the beginning or at the end
RE_NUMERIC = r"^[0-9]+(\.[0-9]+)?$"
RE_NUMERIC_SIGNED = r"^(?!-0(?:$|\.))\-?[0-9]+(\.[0-9]+)?$"

# RE_TEXT = r'^[a-zA-Z0-9\+\-\/\*]*$'
# A text field consisting of any combination of characters except the following:
# - the pipe (|),
# - vertical whitespace (such as Newline or Carriage Return),
# - control characters (ASCII codes 0-32 and 127).
RE_TEXT = r"^[^\x00-\x1F\x7C\7F]*$"


def _matches(value, regex):
    return re.match(regex, value) is not None


def is_alphabetic(value):
    """
    Alphabetic.

    Upper case letters drawn from the 26-letter Roman alphabet, some punctuation marks
    (but never commas) may be included.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_ALPHABETIC)


def is_alphanumeric(value):
    """
    Alphanumeric.

    Combinations of upper case letters, digits 0 to 9 and arithmetic signs.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_ALPHANUMERIC)


def is_integer(value):
    """
    Integer.

    Whole numbers, one or more digits. Note that some fields require leading zeroes.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_INTEGER)


def is_numeric(value):
    """
    Numeric.

    Any numbers, with decimal points allowed.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_NUMERIC)


def is_numeric_signed(value):
    """
    Numeric signed.

    Like Numeric, but allows a leading minus sign. The value -0 is not permitted.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_NUMERIC_SIGNED)


def is_text(value):
    """
    Text.

    Any combination of letters, numbers and punctuation marks.
    :param value: Value to test
    :return: Result
    """
    return _matches(value, RE_TEXT)


def is_valid_type(value, type):
    """Return True if a value matches the specified EURING field type."""
    if type == TYPE_ALPHABETIC:
        return is_alphabetic(value)
    if type == TYPE_ALPHANUMERIC:
        return is_alphanumeric(value)
    if type == TYPE_INTEGER:
        return is_integer(value)
    if type == TYPE_NUMERIC:
        return is_numeric(value)
    if type == TYPE_NUMERIC_SIGNED:
        return is_numeric_signed(value)
    if type == TYPE_TEXT:
        return is_text(value)
    return False
