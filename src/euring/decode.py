from euring.exceptions import EuringException
from euring.fields import (
    EURING2000_FIELDS,
    EURING2000PLUS_FIELDS,
    EURING2020_FIELDS,
    euring_value_from_list,
)
from euring.formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, FORMAT_EURING2020, unknown_format_error_message
from euring.utils import is_alpha


def euring_detect_format(record: str) -> str:
    """Detect EURING format of encoded record."""
    if "|" in record:
        values = record.split("|")
        num_fields = len(values)
        if num_fields > len(EURING2000PLUS_FIELDS):
            return FORMAT_EURING2020
        accuracy_of_coordinates = euring_value_from_list(values, "accuracy_of_coordinates")
        if is_alpha(accuracy_of_coordinates):
            return FORMAT_EURING2020
        return FORMAT_EURING2000PLUS
    return FORMAT_EURING2000


def euring_record_to_dict(record: str, format: str) -> dict[str, str]:
    """Convert EURING record to a key based dictionary."""
    values = euring_record_to_values(record, format)
    return euring_values_to_dict(values)


def euring_values_to_dict(values: list[str]) -> dict[str, str]:
    """Convert EURING list of values to a key based dictionary."""
    fields = {}
    for index, value in enumerate(values):
        fields[EURING2020_FIELDS[index].key] = value
    return fields


def euring_record_to_values(record: str, format: str) -> list[str]:
    """Convert EURING record to a list of values."""
    if format in (FORMAT_EURING2000PLUS, FORMAT_EURING2020):
        return record.split("|")
    if format == FORMAT_EURING2000:
        return _euring2000_record_to_values(record)
    raise EuringException(unknown_format_error_message(format=format))


def _euring2000_record_to_values(record: str) -> list[str]:
    """Convert fixed length EURING record to a list of values."""
    values = []
    start = 0
    record_length = len(record)
    for field in EURING2000_FIELDS:
        if start >= record_length:
            break
        end = start + field.length
        values.append(record[start:end])
        start = end
    return values
