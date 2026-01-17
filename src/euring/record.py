from __future__ import annotations

import json
import warnings

from .converters import convert_euring_record
from .decoders import EuringDecoder, euring_decode_value
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_JSON,
    format_display_name,
    normalize_format,
)
from .rules import record_rule_errors


class EuringRecord:
    """Build or decode EURING records."""

    def __init__(self, format: str, *, strict: bool = True) -> None:
        """Initialize a record with the given EURING format."""
        self.format = normalize_format(format)
        self.strict = strict
        self._fields: dict[str, dict[str, object]] = {}
        self.errors: dict[str, list] = {"record": [], "fields": []}
        self.fields = self._fields

    @classmethod
    def decode(cls, value: str, format: str | None = None) -> EuringRecord:
        """Decode a EURING record string into an EuringRecord."""
        decoder = EuringDecoder(value, format=format)
        result = decoder.get_results()
        if decoder.record_format:
            internal_format = decoder.record_format
        elif format:
            internal_format = normalize_format(format)
        else:
            internal_format = FORMAT_EURING2000PLUS
        record = cls(internal_format, strict=False)
        record._fields = result["fields"]
        record.fields = record._fields
        record.errors = result["errors"]
        return record

    def set(self, key: str, value: object) -> EuringRecord:
        """Set a field value by key."""
        field = _FIELD_MAP.get(key)
        if field is None:
            raise ValueError(f'Unknown field key "{key}".')
        self._fields[key] = {
            "name": field["name"],
            "value": "" if value is None else str(value),
            "order": field["order"],
        }
        return self

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
                return convert_euring_record(record, source_format=self.format, target_format=normalized, force=False)
            except ValueError as exc:
                warnings.warn(str(exc), UserWarning)
        return convert_euring_record(record, source_format=self.format, target_format=normalized, force=force)

    def has_errors(self, errors: object) -> bool:
        """Return True when a structured errors payload contains entries."""
        if not isinstance(errors, dict):
            return bool(errors)
        record_errors = errors.get("record", [])
        field_errors = errors.get("fields", [])
        return bool(record_errors) or bool(field_errors)

    def validate(self, record: str | None = None) -> dict[str, list]:
        """Validate all fields, then apply multi-field and record-level checks."""
        errors = {"record": [], "fields": []}
        field_errors = self._validate_fields()
        errors["fields"].extend(field_errors)
        errors["fields"].extend(self._validate_record_rules())
        self.errors = errors
        return self.errors

    def _validate_fields(self) -> list[dict[str, object]]:
        """Validate each field value against its definition."""
        errors: list[dict[str, object]] = []
        fields = _fields_for_format(self.format)
        positions = _field_positions(fields) if self.format == FORMAT_EURING2000 else {}
        for index, field in enumerate(fields):
            key = field["key"]
            value = self._fields.get(key, {}).get("value", "")
            value = "" if value is None else value
            try:
                euring_decode_value(
                    value,
                    field["type"],
                    required=field.get("required", True),
                    length=field.get("length"),
                    min_length=field.get("min_length"),
                    max_length=field.get("max_length"),
                    parser=field.get("parser"),
                    lookup=field.get("lookup"),
                )
            except EuringParseException as exc:
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
        values_by_key = {key: field.get("value", "") for key, field in self._fields.items()}
        errors: list[dict[str, object]] = []
        for error in record_rule_errors(self.format, values_by_key):
            errors.append(_record_error_for_key(error["key"], error["message"], value=error["value"]))
        return errors

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the record."""
        return {"record": {"format": format_display_name(self.format)}, "fields": self.fields, "errors": self.errors}

    @property
    def display_format(self) -> str:
        """Return the formal EURING format name."""
        return format_display_name(self.format)

    def _serialize(self) -> str:
        """Serialize current field values without strict completeness checks."""
        fields = _fields_for_format(self.format)
        values_by_key: dict[str, str] = {}
        for field in fields:
            key = field["key"]
            value = self._fields.get(key, {}).get("value", "")
            values_by_key[key] = "" if value is None else value
        if self.format == FORMAT_EURING2000:
            return _format_fixed_width(values_by_key, _fixed_width_fields())
        return "|".join(values_by_key.get(field["key"], "") for field in fields)


def _fields_for_format(format: str) -> list[dict[str, object]]:
    """Return the field list for the target format."""
    if format == FORMAT_EURING2000:
        return _fixed_width_fields()
    if format == FORMAT_EURING2000PLUS:
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == "reference":
                return EURING_FIELDS[: index + 1]
    return EURING_FIELDS


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
        fields.append({**field, "length": length})
        start += length
    return fields


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


_FIELD_MAP = {field["key"]: {**field, "order": index} for index, field in enumerate(EURING_FIELDS)}


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
    field = _FIELD_MAP.get(key, {})
    return {
        "field": field.get("name", key),
        "message": message,
        "value": "" if value is None else f"{value}",
        "key": key,
        "index": field.get("order"),
    }
