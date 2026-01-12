from __future__ import annotations

from .decoders import euring_decode_record, euring_decode_value
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, normalize_format


class EuringRecordBuilder:
    """Build EURING record strings from field values."""

    def __init__(self, format: str, *, strict: bool = True) -> None:
        self.format = normalize_format(format)
        self.strict = strict
        self._values: dict[str, str] = {}

    def set(self, key: str, value: object) -> EuringRecordBuilder:
        if key not in _FIELD_KEYS:
            raise ValueError(f'Unknown field key "{key}".')
        self._values[key] = "" if value is None else str(value)
        return self

    def update(self, values: dict[str, object]) -> EuringRecordBuilder:
        for key, value in values.items():
            self.set(key, value)
        return self

    def build(self) -> str:
        fields = _fields_for_format(self.format)
        values_by_key: dict[str, str] = {}

        for field in fields:
            key = field["key"]
            value = self._values.get(key, "")
            if value == "":
                if self.strict and field.get("required", True):
                    raise ValueError(f'Missing required field "{key}".')
                continue
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
                raise ValueError(f'Invalid value for "{key}": {exc}') from exc
            values_by_key[key] = value

        if self.format == FORMAT_EURING2000:
            record = _format_fixed_width(values_by_key, _fixed_width_fields())
        else:
            record = "|".join(values_by_key.get(field["key"], "") for field in fields)

        if self.strict:
            format = normalize_format(self.format)
            result = euring_decode_record(record, format=format)
            errors = result.get("errors", {})
            if self.has_errors(errors):
                raise ValueError(f"Record validation failed: {result['errors']}")

        return record

    def has_errors(self, errors: object) -> bool:
        if not isinstance(errors, dict):
            return bool(errors)
        record_errors = errors.get("record", [])
        field_errors = errors.get("fields", [])
        return bool(record_errors) or bool(field_errors)


def _fields_for_format(format: str) -> list[dict[str, object]]:
    if format == FORMAT_EURING2000:
        return _fixed_width_fields()
    if format == FORMAT_EURING2000PLUS:
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == "reference":
                return EURING_FIELDS[: index + 1]
    return EURING_FIELDS


def _fixed_width_fields() -> list[dict[str, object]]:
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


_FIELD_KEYS = {field["key"] for field in EURING_FIELDS}
