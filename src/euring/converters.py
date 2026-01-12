from __future__ import annotations

from .fields import EURING_FIELDS
from .formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
    normalize_format,
    unknown_format_error,
)
from .utils import euring_lat_to_dms, euring_lng_to_dms


def convert_euring2000_record(value: str, target_format: str = FORMAT_EURING2020) -> str:
    """Convert a fixed-width euring2000 record to euring2000plus or euring2020."""
    return convert_euring_record(value, source_format=FORMAT_EURING2000, target_format=target_format)


def convert_euring_record(
    value: str,
    source_format: str | None = None,
    target_format: str = FORMAT_EURING2020,
    force: bool = False,
) -> str:
    """Convert EURING records between euring2000, euring2000plus, and euring2020."""
    normalized_target, values_by_key, target_fields = convert_euring_record_data(
        value, source_format=source_format, target_format=target_format, force=force
    )
    if normalized_target == FORMAT_EURING2000:
        return _format_fixed_width(values_by_key, target_fields)
    output_values = [values_by_key.get(field["key"], "") for field in target_fields]
    return "|".join(output_values)


def convert_euring_record_data(
    value: str,
    *,
    source_format: str | None = None,
    target_format: str,
    force: bool = False,
) -> tuple[str, dict[str, str], list[dict[str, object]]]:
    """Convert and return the normalized target format plus field values by key."""
    normalized_target = _normalize_target_format(target_format)
    normalized_source = _normalize_source_format(source_format, value)

    if normalized_source == FORMAT_EURING2000:
        fields = _split_fixed_width(value)
        source_fields = _fixed_width_fields()
    else:
        fields = _split_pipe_delimited(value)
        source_fields = _target_fields(normalized_source)
        if len(fields) > len(source_fields) and any(part.strip() for part in fields[len(source_fields) :]):
            raise ValueError(
                "Input has more fields than expected for the declared format. "
                f"Use {FORMAT_EURING2020} when 2020-only fields are present."
            )

    values_by_key = _map_fields_to_values(source_fields, fields)
    _require_force_on_loss(values_by_key, normalized_source, normalized_target, force)
    _apply_coordinate_downgrade(values_by_key, normalized_source, normalized_target, force)

    if normalized_target == FORMAT_EURING2000:
        target_fields = _fixed_width_fields()
    else:
        target_fields = _target_fields(normalized_target)

    return normalized_target, values_by_key, target_fields


def _split_fixed_width(value: str) -> list[str]:
    """Split a fixed-width EURING2000 record into field values."""
    if "|" in value:
        raise ValueError(f"Input appears to be pipe-delimited, not fixed-width {FORMAT_EURING2000}.")
    if len(value) < 94:
        raise ValueError(f"{FORMAT_EURING2000} record must be 94 characters long.")
    if len(value) > 94 and value[94:].strip():
        raise ValueError(f"{FORMAT_EURING2000} record contains extra data beyond position 94.")
    fields: list[str] = []
    start = 0
    for field in _fixed_width_fields():
        length = field["length"]
        end = start + length
        chunk = value[start:end]
        if len(chunk) < length:
            chunk = chunk.ljust(length)
        fields.append(chunk)
        start = end
    return fields


def _split_pipe_delimited(value: str) -> list[str]:
    """Split a pipe-delimited record into field values."""
    return value.split("|")


def _map_fields_to_values(fields: list[dict[str, object]], values: list[str]) -> dict[str, str]:
    """Map field definitions to values by key."""
    mapping: dict[str, str] = {}
    for index, field in enumerate(fields):
        key = field["key"]
        mapping[key] = values[index] if index < len(values) else ""
    return mapping


def _require_force_on_loss(values_by_key: dict[str, str], source_format: str, target_format: str, force: bool) -> None:
    """Raise when conversion would lose data without force."""
    reasons: list[str] = []
    if target_format in {FORMAT_EURING2000, FORMAT_EURING2000PLUS}:
        for key in ("latitude", "longitude", "current_place_code", "more_other_marks"):
            if values_by_key.get(key):
                reasons.append(f"drop {key}")
        accuracy = values_by_key.get("accuracy_of_coordinates", "")
        if accuracy.isalpha():
            reasons.append("alphabetic coordinate accuracy")
    if target_format == FORMAT_EURING2000:
        fixed_keys = {field["key"] for field in _fixed_width_fields()}
        for key, value in values_by_key.items():
            if key not in fixed_keys and value:
                reasons.append(f"drop {key}")
    if reasons and not force:
        summary = ", ".join(sorted(set(reasons)))
        raise ValueError(f"Conversion would lose data. Use --force to proceed. Potential losses: {summary}.")


def _apply_coordinate_downgrade(
    values_by_key: dict[str, str], source_format: str, target_format: str, force: bool
) -> None:
    """Apply lossy coordinate downgrade rules when needed."""
    if target_format not in {FORMAT_EURING2000, FORMAT_EURING2000PLUS}:
        return
    accuracy = values_by_key.get("accuracy_of_coordinates", "")
    if accuracy.isalpha():
        if not force:
            raise ValueError(
                f"Alphabetic accuracy codes are only valid in {FORMAT_EURING2020}. Use --force to apply lossy mapping."
            )
        mapped = _map_alpha_accuracy_to_numeric(accuracy)
        if mapped is None:
            raise ValueError(f'Unsupported alphabetic accuracy code "{accuracy}".')
        values_by_key["accuracy_of_coordinates"] = mapped
    coords = values_by_key.get("geographical_coordinates", "")
    if coords.strip():
        return
    latitude = values_by_key.get("latitude", "")
    longitude = values_by_key.get("longitude", "")
    if not latitude or not longitude:
        return
    lat = euring_lat_to_dms(float(latitude))
    lng = euring_lng_to_dms(float(longitude))
    values_by_key["geographical_coordinates"] = f"{lat}{lng}"


def _map_alpha_accuracy_to_numeric(code: str) -> str | None:
    """Map alphabetic accuracy codes to numeric values."""
    mapping = {
        "A": "0",
        "B": "0",
        "C": "0",
        "D": "0",
        "E": "0",
        "F": "0",
        "G": "0",
        "H": "1",
        "I": "2",
        "J": "4",
        "K": "5",
        "L": "6",
        "M": "7",
        "Z": "9",
    }
    return mapping.get(code.upper())


def _format_fixed_width(values_by_key: dict[str, str], fields: list[dict[str, object]]) -> str:
    """Serialize values into a fixed-width record."""
    parts: list[str] = []
    for field in fields:
        key = field["key"]
        length = field["length"]
        value = values_by_key.get(key, "")
        if not value:
            parts.append("-" * length)
            continue
        if len(value) < length:
            value = value.ljust(length, "-")
        parts.append(value[:length])
    return "".join(parts)


def _target_fields(target_format: str) -> list[dict[str, object]]:
    """Return the field definitions for a target format."""
    if target_format == FORMAT_EURING2000PLUS:
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == "reference":
                return EURING_FIELDS[: index + 1]
    return EURING_FIELDS


def _normalize_target_format(target_format: str) -> str:
    """Normalize a target format string to an internal constant."""
    try:
        return normalize_format(target_format)
    except ValueError:
        raise ValueError(unknown_format_error(target_format, "target format"))


def _normalize_source_format(source_format: str | None, value: str) -> str:
    """Normalize a source format string or auto-detect from the value."""
    if source_format is None:
        if "|" not in value:
            return FORMAT_EURING2000
        values = value.split("|")
        reference_index = _field_index("reference")
        accuracy_index = _field_index("accuracy_of_coordinates")
        accuracy_value = values[accuracy_index] if accuracy_index < len(values) else ""
        has_2020_fields = len(values) > reference_index + 1
        if (accuracy_value and accuracy_value.isalpha()) or has_2020_fields:
            return FORMAT_EURING2020
        return FORMAT_EURING2000PLUS

    try:
        return normalize_format(source_format)
    except ValueError:
        raise ValueError(unknown_format_error(source_format, "source format"))


def _field_index(key: str) -> int:
    """Return the field index for a given key."""
    for index, field in enumerate(EURING_FIELDS):
        if field.get("key") == key:
            return index
    raise ValueError(f'Unknown field key "{key}".')


def _fixed_width_fields() -> list[dict[str, object]]:
    """Return field definitions for the EURING2000 fixed-width layout."""
    fields: list[dict[str, object]] = []
    start = 0
    for field in EURING_FIELDS:
        if start >= 94:
            break
        length = field.get("length", field.get("max_length"))
        if not length:
            break
        fields.append({"key": field["key"], "length": length})
        start += length
    return fields
