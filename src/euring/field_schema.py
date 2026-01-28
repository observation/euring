from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import date as dt_date
from typing import Any

from euring.coordinates import lat_lng_to_euring_coordinates
from euring.utils import is_all_hyphens, is_empty

from .codes import lookup_description
from .exceptions import EuringConstraintException, EuringTypeException
from .formats import FORMAT_EURING2000
from .types import (
    TYPE_ALPHABETIC,
    TYPE_ALPHANUMERIC,
    TYPE_INTEGER,
    TYPE_NUMERIC,
    TYPE_NUMERIC_SIGNED,
    TYPE_TEXT,
    is_valid_euring_type,
)

__all__ = [
    "EuringField",
    "EuringLookupField",
    "EuringFormattedField",
    "coerce_field",
]


@dataclass(frozen=True)
class EuringField(Mapping[str, Any]):
    """Schema definition for a EURING field (no per-record values)."""

    key: str
    name: str
    euring_type: str = ""
    value_type: str | None = None
    required: bool = True
    length: int | None = None
    variable_length: bool = False
    empty_value: str | None = None

    def _mapping(self) -> dict[str, Any]:
        mapping: dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "euring_type": self.euring_type,
            "required": self.required,
        }
        if self.value_type is not None:
            mapping["value_type"] = self.value_type
        if self.length is not None:
            mapping["length"] = self.length
        if self.variable_length:
            mapping["variable_length"] = True
        if self.empty_value is not None:
            mapping["empty_value"] = self.empty_value
        return mapping

    def __getitem__(self, key: str) -> Any:
        return self._mapping()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())

    def _is_required(self) -> bool:
        return self.required

    def _validate_length(self, raw: str, ignore_variable_length: bool = False) -> None:
        if self.length is not None:
            value_length = len(raw)
            if self.variable_length and not ignore_variable_length:
                if value_length > self.length:
                    raise EuringConstraintException(
                        f'Value "{raw}" is length {value_length}, should be at most {self.length}.'
                    )
            elif value_length != self.length:
                raise EuringConstraintException(f'Value "{raw}" is length {value_length} instead of {self.length}.')

    def _validate_raw(self, raw: str) -> str | None:
        if raw == "":
            if not self._is_required():
                return None
            raise EuringConstraintException('Required field, empty value "" is not permitted.')
        self._validate_length(raw)
        if self.euring_type and not is_valid_euring_type(raw, self.euring_type):
            raise EuringTypeException(f'Value "{raw}" is not valid for type {self.euring_type}.')
        return raw

    def _coerce_type(self, raw: str) -> Any:
        if self.euring_type == TYPE_INTEGER:
            if is_all_hyphens(raw):
                return None
            return int(raw)
        if self.euring_type == TYPE_NUMERIC:
            return float(raw)
        if self.euring_type == TYPE_NUMERIC_SIGNED:
            return float(raw)
        if self.euring_type in {TYPE_ALPHABETIC, TYPE_ALPHANUMERIC, TYPE_TEXT}:
            return raw
        return raw

    def _coerce_value_type(self, raw: str) -> Any:
        """Coerce a validated raw value to the configured value type."""
        if self.value_type in {None, ""}:
            return self._coerce_type(raw)
        if self.value_type == "code_str":
            return raw
        if self.value_type == "int":
            if is_all_hyphens(raw):
                return None
            return int(raw)
        if self.value_type == "float":
            return float(raw)
        if self.value_type == "date":
            if len(raw) != 8 or not raw.isdigit():
                raise EuringConstraintException(f'Value "{raw}" is not a valid ddmmyyyy date.')
            day = int(raw[0:2])
            month = int(raw[2:4])
            year = int(raw[4:8])
            try:
                return dt_date(year, month, day)
            except ValueError:
                raise EuringConstraintException(f'Value "{raw}" is not a valid ddmmyyyy date.')
        raise ValueError(f'Unsupported value_type "{self.value_type}" for field "{self.key}".')

    def parse(self, raw: str) -> Any | None:
        """Parse raw text into a Python value."""
        validated = self._validate_raw(raw)
        if validated is None:
            return None
        return self._coerce_value_type(validated)

    def encode(self, value: Any | None) -> str:
        """Encode a Python value to raw text."""
        if is_empty(value):
            if self._is_required():
                raise EuringConstraintException('Required field, empty value "" is not permitted.')
            return ""

        if self.key == "geographical_coordinates":
            coords: dict[str, object] | None = None
            if isinstance(value, dict):
                coords = value
            elif isinstance(value, (tuple, list)) and len(value) == 2:
                coords = {"lat": value[0], "lng": value[1]}
            if coords is not None:
                if "lat" not in coords or "lng" not in coords:
                    raise EuringConstraintException("Geographical coordinates require both lat and lng values.")
                return lat_lng_to_euring_coordinates(float(coords["lat"]), float(coords["lng"]))

        if self.key == "date" and isinstance(value, dt_date):
            return value.strftime("%d%m%Y")

        str_value = f"{value}"
        if self.euring_type in {TYPE_NUMERIC, TYPE_NUMERIC_SIGNED}:
            str_value = str_value.rstrip("0").rstrip(".")
        if (
            self.euring_type in {TYPE_INTEGER, TYPE_NUMERIC, TYPE_NUMERIC_SIGNED}
            and self.length
            and not self.variable_length
        ):
            str_value = str_value.zfill(self.length)
        self._validate_length(str_value)
        if self.euring_type and not is_valid_euring_type(str_value, self.euring_type):
            raise EuringTypeException(f'Value "{str_value}" is not valid for type {self.euring_type}.')
        return str_value

    def encode_for_format(self, value: Any | None, *, format: str) -> str:
        """Encode a Python value to raw text for a specific EURING format."""
        if is_empty(value):
            if self.empty_value:
                return self.empty_value
            if self.length and format == FORMAT_EURING2000:
                return "-" * self.length
            if self.length and self.required and self.euring_type == TYPE_INTEGER:
                return "-" * self.length
            return ""

        if self.key == "geographical_coordinates":
            coords: dict[str, object] | None = None
            if isinstance(value, dict):
                coords = value
            elif isinstance(value, (tuple, list)) and len(value) == 2:
                coords = {"lat": value[0], "lng": value[1]}
            if coords is not None:
                if "lat" not in coords or "lng" not in coords:
                    raise EuringConstraintException("Geographical coordinates require both lat and lng values.")
                return lat_lng_to_euring_coordinates(float(coords["lat"]), float(coords["lng"]))

        if self.key == "date" and isinstance(value, dt_date):
            str_value = value.strftime("%d%m%Y")
            self._validate_length(str_value)
            if self.euring_type and not is_valid_euring_type(str_value, self.euring_type):
                raise EuringTypeException(f'Value "{str_value}" is not valid for type {self.euring_type}.')
            return str_value

        if self.euring_type == TYPE_INTEGER and isinstance(value, str) and is_all_hyphens(value):
            return self.encode_for_format(None, format=format)

        str_value = f"{value}"
        if self.euring_type in {TYPE_NUMERIC, TYPE_NUMERIC_SIGNED}:
            str_value = str_value.rstrip("0").rstrip(".")

        ignore_variable_length = format == FORMAT_EURING2000

        if self.euring_type in {TYPE_INTEGER, TYPE_NUMERIC, TYPE_NUMERIC_SIGNED} and self.length:
            str_value = str_value.zfill(self.length)

        if self.variable_length and not ignore_variable_length:
            str_value = str_value.lstrip("0") or "0"

        self._validate_length(str_value, ignore_variable_length=ignore_variable_length)
        if self.euring_type and not is_valid_euring_type(str_value, self.euring_type):
            raise EuringTypeException(f'Value "{str_value}" is not valid for type {self.euring_type}.')
        return str_value

    def describe(self, value: Any | None) -> Any | None:
        """Return a display description for a parsed value."""
        return None


@dataclass(frozen=True)
class EuringLookupField(EuringField):
    """Field that describes values using a lookup map or callable."""

    lookup: Any | None = None

    def _mapping(self) -> dict[str, Any]:
        mapping = super()._mapping()
        if self.lookup is not None:
            mapping["lookup"] = self.lookup
        return mapping

    def describe(self, value: Any | None) -> Any | None:
        if self.lookup is None or value is None:
            return None
        if callable(self.lookup):
            return lookup_description(value, self.lookup)
        return lookup_description(str(value), self.lookup)


@dataclass(frozen=True)
class EuringFormattedField(EuringField):
    """Field that validates type, then parses raw text into a Python value."""

    parser: Any | None = None
    lookup: Any | None = None

    def _mapping(self) -> dict[str, Any]:
        mapping = super()._mapping()
        if self.parser is not None:
            mapping["parser"] = self.parser
        if self.lookup is not None:
            mapping["lookup"] = self.lookup
        return mapping

    def parse(self, raw: str) -> Any | None:
        validated = self._validate_raw(raw)
        if validated is None:
            return None
        if self.parser is None:
            return self._coerce_value_type(validated)
        parsed = self.parser(validated)
        # Allow a parser to validate and pass through a raw string, while still
        # applying the configured value_type coercion.
        if isinstance(parsed, str) and self.value_type not in {None, ""}:
            return self._coerce_value_type(parsed)
        return parsed

    def describe(self, value: Any | None) -> Any | None:
        if self.lookup is None or value is None:
            return None
        if callable(self.lookup):
            return lookup_description(value, self.lookup)
        return lookup_description(str(value), self.lookup)


def coerce_field(definition: Mapping[str, Any]) -> EuringField:
    """Return a field instance from a definition mapping or field object."""
    if isinstance(definition, EuringField):
        return definition
    key = definition.get("key", "")
    name = definition.get("name", key)
    euring_type = definition.get("euring_type") or ""
    value_type = definition.get("value_type")
    required = definition.get("required", True)
    length = definition.get("length")
    variable_length = bool(definition.get("variable_length", False))
    empty_value = definition.get("empty_value")
    parser = definition.get("parser")
    lookup = definition.get("lookup")
    if parser is not None:
        return EuringFormattedField(
            key=key,
            name=name,
            euring_type=euring_type,
            value_type=value_type,
            required=required,
            length=length,
            variable_length=variable_length,
            empty_value=empty_value,
            parser=parser,
            lookup=lookup,
        )
    if lookup is not None:
        return EuringLookupField(
            key=key,
            name=name,
            euring_type=euring_type,
            value_type=value_type,
            required=required,
            length=length,
            variable_length=variable_length,
            empty_value=empty_value,
            lookup=lookup,
        )
    return EuringField(
        key=key,
        name=name,
        euring_type=euring_type,
        value_type=value_type,
        required=required,
        length=length,
        variable_length=variable_length,
        empty_value=empty_value,
    )
