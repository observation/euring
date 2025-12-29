from __future__ import annotations

from .fields import EURING_FIELDS
from .utils import euring_lat_to_dms, euring_lng_to_dms


def convert_euring2000_record(value: str, target_format: str = "EURING2000PLUS") -> str:
    """Convert a fixed-width EURING2000 record to EURING2000PLUS or EURING2020."""
    return convert_euring_record(value, source_format="EURING2000", target_format=target_format)


def convert_euring_record(
    value: str,
    source_format: str | None = None,
    target_format: str = "EURING2000PLUS",
    force: bool = False,
) -> str:
    """Convert EURING records between EURING2000, EURING2000PLUS, and EURING2020."""
    normalized_target = _normalize_target_format(target_format)
    normalized_source = _normalize_source_format(source_format, value)

    if normalized_source == "EURING2000":
        fields = _split_fixed_width(value)
        source_fields = _fixed_width_fields()
    else:
        fields = _split_pipe_delimited(value)
        source_fields = _target_fields(normalized_source)
        if len(fields) > len(source_fields) and any(part.strip() for part in fields[len(source_fields) :]):
            raise ValueError(
                "Input has more fields than expected for the declared format. "
                "Use EURING2020 when 2020-only fields are present."
            )

    values_by_key = _map_fields_to_values(source_fields, fields)
    _require_force_on_loss(values_by_key, normalized_source, normalized_target, force)
    _apply_coordinate_downgrade(values_by_key, normalized_source, normalized_target, force)

    if normalized_target == "EURING2000":
        target_fields = _fixed_width_fields()
        return _format_fixed_width(values_by_key, target_fields)

    target_fields = _target_fields(normalized_target)
    output_values = [values_by_key.get(field["key"], "") for field in target_fields]
    return "|".join(output_values)


def _split_fixed_width(value: str) -> list[str]:
    if "|" in value:
        raise ValueError("Input appears to be pipe-delimited, not fixed-width EURING2000.")
    if len(value) < 94:
        raise ValueError("EURING2000 record must be 94 characters long.")
    if len(value) > 94 and value[94:].strip():
        raise ValueError("EURING2000 record contains extra data beyond position 94.")
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
    return value.split("|")


def _map_fields_to_values(fields: list[dict[str, object]], values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for index, field in enumerate(fields):
        key = field["key"]
        mapping[key] = values[index] if index < len(values) else ""
    return mapping


def _require_force_on_loss(values_by_key: dict[str, str], source_format: str, target_format: str, force: bool) -> None:
    reasons: list[str] = []
    if target_format in {"EURING2000", "EURING2000+"}:
        for key in ("latitude", "longitude", "current_place_code", "more_other_marks"):
            if values_by_key.get(key):
                reasons.append(f"drop {key}")
        accuracy = values_by_key.get("accuracy_of_coordinates", "")
        if accuracy.isalpha():
            reasons.append("alphabetic coordinate accuracy")
    if target_format == "EURING2000":
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
    if target_format not in {"EURING2000", "EURING2000+"}:
        return
    accuracy = values_by_key.get("accuracy_of_coordinates", "")
    if accuracy.isalpha():
        if not force:
            raise ValueError(
                "Alphabetic accuracy codes are only valid in EURING2020. Use --force to apply lossy mapping."
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
    if target_format == "EURING2000+":
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == "reference":
                return EURING_FIELDS[: index + 1]
    return EURING_FIELDS


def _normalize_target_format(target_format: str) -> str:
    raw = target_format.strip()
    normalized = raw.upper()
    if normalized.startswith("EURING"):
        normalized = normalized.replace("EURING", "")
    else:
        raise ValueError(f'Unknown target format "{target_format}". Use euring2000, euring2000plus, or euring2020.')
    if normalized in {"2000", "2000+", "2000PLUS", "2000P"}:
        if normalized == "2000":
            return "EURING2000"
        return "EURING2000+"
    if normalized == "2020":
        return "EURING2020"
    raise ValueError(f'Unknown target format "{target_format}". Use euring2000, euring2000plus, or euring2020.')


def _normalize_source_format(source_format: str | None, value: str) -> str:
    if source_format is None:
        if "|" not in value:
            return "EURING2000"
        values = value.split("|")
        reference_index = _field_index("reference")
        accuracy_index = _field_index("accuracy_of_coordinates")
        accuracy_value = values[accuracy_index] if accuracy_index < len(values) else ""
        has_2020_fields = len(values) > reference_index + 1
        if (accuracy_value and accuracy_value.isalpha()) or has_2020_fields:
            return "EURING2020"
        return "EURING2000+"

    normalized = source_format.strip().upper()
    if not normalized.startswith("EURING"):
        raise ValueError(f'Unknown source format "{source_format}". Use euring2000, euring2000plus, or euring2020.')
    normalized = normalized.replace("EURING", "")
    if normalized in {"2000", "2000+", "2000PLUS", "2000P", "2020"}:
        if normalized == "2000":
            return "EURING2000"
        if normalized in {"2000PLUS", "2000P"}:
            normalized = "2000+"
        return f"EURING{normalized}"
    raise ValueError(f'Unknown source format "{source_format}". Use euring2000, euring2000plus, or euring2020.')


def _field_index(key: str) -> int:
    for index, field in enumerate(EURING_FIELDS):
        if field.get("key") == key:
            return index
    raise ValueError(f'Unknown field key "{key}".')


def _fixed_width_fields() -> list[dict[str, object]]:
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
