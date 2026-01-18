from .codes import lookup_description
from .exceptions import EuringParseException
from .types import is_valid_type


def euring_decode_value(
    value, type, required=True, length=None, min_length=None, max_length=None, parser=None, lookup=None
):
    """Decode a single EURING field value with type checks, parsing, and lookup."""
    # A minimum length of 0 is the same as not required
    if min_length == 0:
        required = False
    # What to do with an empty value
    if value == "":
        if required is False:
            # If not required, an empty value will result in None, regardless of the type check
            return None
        else:
            raise EuringParseException('Required field, empty value "" is not permitted.')
    # Check the type
    if not is_valid_type(value, type):
        raise EuringParseException(f'Value "{value}" is not valid for type {type}.')
    # Length checks
    value_length = len(value)
    # Check length
    if length is not None:
        if value_length != length:
            raise EuringParseException(f'Value "{value}" is length {value_length} instead of {length}.')
    # Check min_length
    if min_length is not None:
        if value_length < min_length:
            raise EuringParseException(f'Value "{value}" is length {value_length}, should be at least {min_length}.')
    # Check max_length
    if max_length is not None:
        if value_length > max_length:
            raise EuringParseException(f'Value "{value}" is length {value_length}, should be at most {max_length}.')
    # Results
    results = {"value": value}
    # Extra parser if needed
    if parser:
        value = parser(value)
        results["parsed_value"] = value
    # Look up description
    results["description"] = lookup_description(value, lookup)
    # Return results
    return results
