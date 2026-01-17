from __future__ import annotations

from .decoders import EuringDecoder, euring_decode_value
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, format_display_name, normalize_format


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

    def serialize(self) -> str:
        """Serialize and validate a EURING record string."""
        fields = _fields_for_format(self.format)
        values_by_key: dict[str, str] = {}

        for field in fields:
            key = field["key"]
            value = self._fields.get(key, {}).get("value", "")
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

        errors = self.validate(record)
        if self.strict and self.has_errors(errors):
            raise ValueError(f"Record validation failed: {errors}")

        return record

    def has_errors(self, errors: object) -> bool:
        """Return True when a structured errors payload contains entries."""
        if not isinstance(errors, dict):
            return bool(errors)
        record_errors = errors.get("record", [])
        field_errors = errors.get("fields", [])
        return bool(record_errors) or bool(field_errors)

    def validate(self, record: str | None = None) -> dict[str, list]:
        """Validate the record and store errors on the record."""
        if record is None:
            record = self._serialize()
        decoder = EuringDecoder(record, format=self.format)
        result = decoder.get_results()
        self.errors = result.get("errors", {"record": [], "fields": []})
        self._fields = result.get("fields", {})
        self.fields = self._fields
        return self.errors

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
            values_by_key[key] = self._fields.get(key, {}).get("value", "")
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
