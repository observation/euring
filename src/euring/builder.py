from __future__ import annotations

from .decoders import euring_decode_record, euring_decode_value
from .exceptions import EuringParseException
from .fields import EURING_FIELDS


class EuringRecordBuilder:
    """Build EURING record strings from field values."""

    def __init__(self, format: str = "euring2000plus", *, strict: bool = True) -> None:
        self.format = _normalize_format(format)
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

        if self.format == "euring2000":
            record = _format_fixed_width(values_by_key, _fixed_width_fields())
        else:
            record = "|".join(values_by_key.get(field["key"], "") for field in fields)

        if self.strict:
            hint = _format_hint(self.format)
            result = euring_decode_record(record, format_hint=hint)
            if result.get("errors"):
                raise ValueError(f"Record validation failed: {result['errors']}")

        return record


def _normalize_format(format: str) -> str:
    raw = format.strip().lower()
    if raw.startswith("euring"):
        raw = raw.replace("euring", "", 1)
    if raw in {"2000", "2000+", "2000plus", "2000p"}:
        return "euring2000" if raw == "2000" else "euring2000plus"
    if raw == "2020":
        return "euring2020"
    if raw in {"euring2000", "euring2000plus", "euring2020"}:
        return raw
    raise ValueError(f'Unknown format "{format}". Use euring2000, euring2000plus, or euring2020.')


def _format_hint(format: str) -> str:
    if format == "euring2000":
        return "EURING2000"
    if format == "euring2000plus":
        return "EURING2000+"
    return "EURING2020"


def _fields_for_format(format: str) -> list[dict[str, object]]:
    if format == "euring2000":
        return _fixed_width_fields()
    if format == "euring2000plus":
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
