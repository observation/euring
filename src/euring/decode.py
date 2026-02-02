from euring.exceptions import EuringConstraintException, EuringException
from euring.fields import (
    EURING2000_FIELDS,
    EURING2000_RECORD_LENGTH,
    EURING2000PLUS_FIELDS,
    EURING2020_FIELDS,
    euring_value_from_list,
)
from euring.formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
    normalize_format,
    unknown_format_error_message,
)
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


def _normalize_decode_format(format: str | None) -> str | None:
    """Normalize a user-provided format string or raise."""
    if not format:
        return None
    try:
        return normalize_format(format)
    except ValueError:
        raise EuringConstraintException(unknown_format_error_message(format))


def _decode_raw_record(record: object, format: str | None) -> tuple[str, dict[str, str], list[dict[str, str]]]:
    """Decode raw field values from an encoded EURING record string."""
    decode_format = ""
    record_errors: list[dict[str, str]] = []
    values_by_key: dict[str, str] = {}

    if not isinstance(record, str):
        record_errors.append({"message": f'Record "{record}" is not a string but {type(record)}.'})
    elif record == "":
        record_errors.append({"message": "Record is an empty string."})
    elif not format:
        decode_format = euring_detect_format(record)
        if not decode_format:
            record_errors.append({"message": f'Format could not be detected from record "{record}".'})

    if format:
        decode_format = _normalize_decode_format(format)
        if not decode_format:
            record_errors.append({"message": unknown_format_error_message(format=format)})

    if not decode_format:
        decode_format = FORMAT_EURING2020
        record_errors.append({"message": f'Switching to default format "{decode_format}".'})

    # Any record error before this point is a fatal error, we will not decode
    if bool(record_errors):
        return decode_format, values_by_key, record_errors

    pipe_character_in_record = "|" in record
    if decode_format == FORMAT_EURING2000:
        if pipe_character_in_record:
            record_errors.append({"message": f'Format "{decode_format}" should not contain pipe characters ("|").'})
        record_length = len(record)
        if record_length != EURING2000_RECORD_LENGTH:
            record_errors.append(
                {
                    "message": (
                        f'Format "{decode_format}" '
                        f"should be exactly {EURING2000_RECORD_LENGTH} characters, found {record_length}."
                    )
                }
            )
    else:
        if not pipe_character_in_record:
            record_errors.append(
                {"message": (f'Format "{decode_format}" should contain values separated by pipe characters ("|").')}
            )

    raw_values_by_key = euring_record_to_dict(record, format=decode_format)
    return decode_format, raw_values_by_key, record_errors
