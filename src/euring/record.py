from __future__ import annotations

import json
import warnings
from dataclasses import replace

from euring.decode import _decode_raw_record

from .coordinates import _lat_to_euring_coordinate, _lng_to_euring_coordinate
from .exceptions import EuringException
from .field_schema import EuringField, coerce_field
from .fields import (
    EURING2000_FIELDS,
    EURING2000PLUS_FIELDS,
    EURING2020_FIELDS,
    EURING_FIELD_MAP,
)
from .formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
    FORMAT_JSON,
    format_display_name,
    normalize_format,
    unknown_format_error_message,
)
from .rules import record_rule_errors
from .utils import is_all_hyphens, is_empty


class EuringRecord:
    """Build or decode EURING records."""

    def __init__(self, format: str, *, strict: bool = True) -> None:
        """Initialize a record with the given EURING format."""
        self.format = normalize_format(format)
        self.strict = strict
        self.clear_errors()
        self._fields: dict[str, dict[str, object]] = {}
        for key, field in EURING_FIELD_MAP.items():
            self._fields[key] = {
                "name": field["name"],
                "raw_value": None,
                "value": None,
                "order": field["order"],
            }
        self.clear_errors()

    def clear_errors(self):
        """Clear all errors and reinitialize."""
        self.errors: dict[str, object] = {"record": [], "fields": dict[str, list[str]]}

    @classmethod
    def decode(cls, value: str, format: str | None = None) -> EuringRecord:
        """Decode a EURING record string into an EuringRecord."""
        record_format, raw_values_by_key, record_errors = _decode_raw_record(value, format)
        record = cls(record_format, strict=False)
        for key, raw_value in raw_values_by_key.items():
            record._set_raw_value(key, raw_value)
        record._validate(record_errors=record_errors)
        return record

    @property
    def fields(self) -> dict[str, dict[str, object]]:
        """Return the decoded field data."""
        return self._fields

    def set(self, key: str, value: object) -> EuringRecord:
        """Set a field value by key."""
        field = EURING_FIELD_MAP.get(key)
        if field is None:
            raise ValueError(f'Unknown field key "{key}".')
        # Setting a typed value should clear any previously captured raw EURING text.
        self._fields[key] = {"name": field["name"], "value": value, "order": field["order"]}
        return self

    def _set_raw_value(self, key: str, value: object) -> None:
        """Set a field from decoded input without normalization."""
        field = EURING_FIELD_MAP.get(key)
        if field is None:
            return
        self._fields[key] = {
            "name": field["name"],
            "raw_value": "" if value is None else f"{value}",
            "value": "" if value is None else f"{value}",
            "order": field["order"],
        }

    def update(self, values: dict[str, object]) -> EuringRecord:
        """Update multiple field values."""
        for key, value in values.items():
            self.set(key, value)
        return self

    def serialize(self, output_format: str | None = None) -> str:
        """Serialize and validate a EURING record string or JSON payload."""
        if output_format is not None and output_format != FORMAT_JSON:
            normalized = normalize_format(output_format)
            if normalized != self.format:
                raise ValueError(f'Record format is "{self.format}". Use that format or "{FORMAT_JSON}".')
        errors = self.validate()
        if self.has_errors(errors):
            if self.strict or self._has_non_optional_errors(errors):
                raise ValueError(f"Record validation failed: {errors}")
        if output_format == FORMAT_JSON:
            return json.dumps(self.to_dict())
        return self._serialize()

    def export(self, output_format: str, *, force: bool = False, warn_on_loss: bool = True) -> str:
        """Export the record to another EURING string format."""
        if output_format == FORMAT_JSON:
            raise ValueError("Use serialize(output_format='json') for JSON output.")
        normalized = normalize_format(output_format)
        if normalized == self.format:
            return self.serialize()
        record = self.serialize()
        if force and warn_on_loss:
            try:
                return _convert_record_string(
                    record,
                    source_format=self.format,
                    target_format=normalized,
                    force=False,
                )
            except ValueError as exc:
                warnings.warn(str(exc), UserWarning)
        return _convert_record_string(record, source_format=self.format, target_format=normalized, force=force)

    def has_errors(self, errors: object) -> bool:
        """Return True when a structured errors payload contains entries."""
        if not isinstance(errors, dict):
            return bool(errors)
        record_errors = errors.get("record", [])
        field_errors = errors.get("fields", [])
        return bool(record_errors) or bool(field_errors)

    def validate(self) -> dict[str, list]:
        """Validate all fields, then apply multi-field and record-level checks."""
        return self._validate()

    def _validate(
        self,
        record_errors: list[dict[str, object]] | None = None,
        field_errors: list[dict[str, object]] | None = None,
    ) -> dict[str, list]:
        """Validate all fields, then apply multi-field and record-level checks."""
        self.errors = {"record": record_errors or [], "fields": field_errors or []}
        self.errors["fields"].extend(self._validate_fields())
        self.errors["fields"].extend(self._validate_record_rules())
        return self.errors


    def record_errors(self) -> list[dict[str, object]]:
        """Return all record errors."""
        return self.errors.get("record", [])

    def field_errors(self, key: str) -> list[dict[str, object]]:
        """Return all field errors for a given field key."""
        return [error for error in self.errors.get("fields", []) if error.get("key") == key]

    def _add_record_error(self, error_message: str):
        """Add a record level error."""
        self.errors["record"].append({"message": error_message})

    def _add_field_error(self, key: str, error_message: str):
        """Add a field level error."""
        self.errors["fields"].append({"key": key, "message": error_message})

    def _validate_fields(self) -> list[dict[str, object]]:
        """Validate each field value against its definition."""
        errors: list[dict[str, object]] = []
        fields = _fields_for_format(self.format)
        positions = _field_positions(fields) if self.format == FORMAT_EURING2000 else {}
        needs_geo_dots = False
        if self.format == FORMAT_EURING2020:
            lat_value = self._fields.get("latitude", {}).get("value")
            lng_value = self._fields.get("longitude", {}).get("value")
            needs_geo_dots = not is_empty(lat_value) or not is_empty(lng_value)
        for index, field in enumerate(fields):
            key = field["key"]
            field_state = self._fields.get(key, {})
            value = field_state.get("value", "")
            had_empty_value = is_empty(value)
            try:
                field_obj = field if isinstance(field, EuringField) else coerce_field(field)
                if self.format == FORMAT_EURING2000 and field_obj.get("variable_length"):
                    # EURING2000 does not support variable-length encoding.
                    field_obj = replace(field_obj, variable_length=False)
                encoded_value = _serialize_field_value(field, value, self.format)
                raw_value = encoded_value
                if key == "date" and had_empty_value and is_all_hyphens(raw_value):
                    # Treat placeholder dashes for missing required dates as empty so
                    # non-strict mode only reports a missing-required-field error.
                    raw_value = ""
                if key == "geographical_coordinates" and had_empty_value and needs_geo_dots:
                    raw_value = "." * 15
                    encoded_value = raw_value
                parsed_value = field_obj.parse(raw_value)
                if had_empty_value and raw_value:
                    parsed_value = None
                description_value = parsed_value
                if field_obj.get("lookup") is not None and raw_value != "" and parsed_value is not None:
                    if field_obj.get("parser") is None:
                        description_value = raw_value
                    elif field_obj.get("value_type") == "date":
                        # Date lookups operate on the encoded ddmmyyyy string.
                        description_value = raw_value
                description = field_obj.describe(description_value)
                if key in self._fields:
                    self._fields[key]["value"] = parsed_value
                    self._fields[key]["encoded_value"] = encoded_value
                    if field_obj.get("parser") is not None:
                        self._fields[key]["parsed_value"] = parsed_value
                    if description is not None:
                        self._fields[key]["description"] = description
            except EuringException as exc:
                payload = {
                    "field": field["name"],
                    "message": f"{exc}",
                    "value": "" if value is None else f"{value}",
                    "key": key,
                    "index": index,
                }
                position = positions.get(key)
                if position:
                    payload["position"] = position["position"]
                    payload["length"] = position["length"]
                errors.append(payload)
        return errors

    def _has_non_optional_errors(self, errors: dict[str, list]) -> bool:
        """Return True if errors include anything beyond missing required fields."""
        if errors.get("record"):
            return True
        for error in errors.get("fields", []):
            message = error.get("message", "")
            if message != 'Required field, empty value "" is not permitted.':
                return True
        return False

    def _validate_record_rules(self) -> list[dict[str, object]]:
        """Validate multi-field and record-level rules."""
        values_by_key: dict[str, str] = {}
        for field in _fields_for_format(self.format):
            key = field["key"]
            field_state = self._fields.get(key, {})
            source_raw = field_state.get("raw_value")
            if source_raw is not None:
                values_by_key[key] = source_raw
                continue
            value = field_state.get("value", "")
            try:
                values_by_key[key] = _serialize_field_value(field, value, self.format)
            except EuringException:
                values_by_key[key] = ""
        if self.format == FORMAT_EURING2020:
            lat_value = values_by_key.get("latitude", "")
            lng_value = values_by_key.get("longitude", "")
            if (lat_value or lng_value) and not values_by_key.get("geographical_coordinates"):
                values_by_key["geographical_coordinates"] = "." * 15
        errors: list[dict[str, object]] = []
        for error in record_rule_errors(self.format, values_by_key):
            errors.append(_record_error_for_key(error["key"], error["message"], value=error["value"]))
        return errors

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the record."""
        return {"record": {"format": format_display_name(self.format)}, "fields": self._fields, "errors": self.errors}

    @property
    def display_format(self) -> str:
        """Return the formal EURING format name."""
        return format_display_name(self.format)

    def _serialize(self) -> str:
        """Serialize current field values without strict completeness checks."""
        fields = _fields_for_format(self.format)
        values_by_key: dict[str, str] = {}
        geo_placeholder = None
        if self.format == FORMAT_EURING2020:
            lat_value = self._fields.get("latitude", {}).get("value")
            lng_value = self._fields.get("longitude", {}).get("value")
            if not is_empty(lat_value) or not is_empty(lng_value):
                geo_placeholder = "." * 15
        for field in fields:
            key = field["key"]
            value = self._fields.get(key, {}).get("value")
            if key == "geographical_coordinates":
                if is_empty(value) and geo_placeholder:
                    values_by_key[key] = geo_placeholder
                    continue
            values_by_key[key] = _serialize_field_value(field, value, self.format)
        if self.format == FORMAT_EURING2000:
            return _format_fixed_width(values_by_key, EURING2000_FIELDS)
        return "|".join(values_by_key.get(field["key"], "") for field in fields)


def _fields_for_format(format: str) -> list[dict[str, object]]:
    """Return the field list for the target format."""
    if format == FORMAT_EURING2000:
        return EURING2000_FIELDS
    if format == FORMAT_EURING2000PLUS:
        return EURING2000PLUS_FIELDS
    if format == FORMAT_EURING2020:
        return EURING2020_FIELDS
    raise EuringException(f"Unknown EuringRecord format: {format}.")


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


def _serialize_field_value(field: dict[str, object], value: object, format: str) -> str:
    """Encode a typed field value into a EURING raw string."""
    field_obj = coerce_field(field)
    return field_obj.encode_for_format(value, format=format)


def _convert_record_string(
    value: str,
    *,
    source_format: str | None = None,
    target_format: str,
    force: bool = False,
) -> str:
    """Convert EURING records between euring2000, euring2000plus, and euring2020."""
    normalized_target, values_by_key, target_fields = _convert_record_data(
        value, source_format=source_format, target_format=target_format, force=force
    )
    if normalized_target == FORMAT_EURING2000:
        return _format_fixed_width(values_by_key, target_fields)
    output_values = [values_by_key.get(field["key"], "") for field in target_fields]
    return "|".join(output_values)


def _convert_record_data(
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
        source_fields = EURING2000_FIELDS
    else:
        fields = _split_pipe_delimited(value)
        source_fields = _fields_for_format(normalized_source)
        if len(fields) > len(source_fields) and any(part.strip() for part in fields[len(source_fields) :]):
            raise ValueError(
                "Input has more fields than expected for the declared format. "
                f"Use {FORMAT_EURING2020} when 2020-only fields are present."
            )

    values_by_key = _map_fields_to_values(source_fields, fields)
    _require_force_on_loss(values_by_key, normalized_source, normalized_target, force)
    _apply_coordinate_downgrade(values_by_key, normalized_source, normalized_target, force)

    target_fields = _fields_for_format(normalized_target)

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
    for field in EURING2000_FIELDS:
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
        fixed_keys = {field["key"] for field in EURING2000_FIELDS}
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
    if coords.strip() and set(coords) != {"."}:
        return
    latitude = values_by_key.get("latitude", "")
    longitude = values_by_key.get("longitude", "")
    if not latitude or not longitude:
        return
    lat = _lat_to_euring_coordinate(float(latitude))
    lng = _lng_to_euring_coordinate(float(longitude))
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


def _normalize_target_format(target_format: str) -> str:
    """Normalize a target format string to an internal constant."""
    try:
        return normalize_format(target_format)
    except ValueError:
        raise ValueError(unknown_format_error_message(target_format, "target format"))


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
        raise ValueError(unknown_format_error_message(source_format, "source format"))


def _field_index(key: str) -> int:
    """Return the field index for a given key."""
    for index, field in enumerate(EURING2020_FIELDS):
        if field.get("key") == key:
            return index
    raise ValueError(f'Unknown field key "{key}".')


def _field_positions(fields: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    """Return position metadata for fixed-width fields."""
    positions: dict[str, dict[str, int]] = {}
    start = 1
    for field in fields:
        length = field.get("length")
        if not length:
            continue
        positions[field["key"]] = {"position": start, "length": length}
        start += length
    return positions


def _record_error_for_key(key: str, message: str, *, value: str) -> dict[str, object]:
    """Build a field error payload for a record-level rule."""
    field = EURING_FIELD_MAP.get(key, {})
    return {
        "field": field.get("name", key),
        "message": message,
        "value": "" if value is None else f"{value}",
        "key": key,
        "index": field.get("order"),
    }
