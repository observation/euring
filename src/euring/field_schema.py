from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from euring.utils import euring_lat_to_dms, euring_lng_to_dms

from .codes import lookup_description
from .exceptions import EuringConstraintException, EuringTypeException
from .types import (
    TYPE_ALPHABETIC,
    TYPE_ALPHANUMERIC,
    TYPE_INTEGER,
    TYPE_NUMERIC,
    TYPE_NUMERIC_SIGNED,
    TYPE_TEXT,
    is_valid_type,
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
    type_name: str = ""
    required: bool = True
    length: int | None = None
    variable_length: bool = False
    empty_value: str | None = None

    def _mapping(self) -> dict[str, Any]:
        mapping: dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "type_name": self.type_name,
            "required": self.required,
        }
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

    def _validate_length(self, raw: str) -> None:
        value_length = len(raw)
        if self.length is not None:
            if self.variable_length:
                if value_length > self.length:
                    raise EuringConstraintException(
                        f'Value "{raw}" is length {value_length}, should be at most {self.length}.'
                    )
            elif value_length != self.length:
                raise EuringConstraintException(f'Value "{raw}" is length {value_length} instead of {self.length}.')
        if self.length is None and self.variable_length:
            raise EuringConstraintException("Variable-length fields require a length limit.")

    def _validate_raw(self, raw: str) -> str | None:
        if raw == "":
            if not self._is_required():
                return None
            raise EuringConstraintException('Required field, empty value "" is not permitted.')
        self._validate_length(raw)
        if self.type_name and not is_valid_type(raw, self.type_name):
            raise EuringTypeException(f'Value "{raw}" is not valid for type {self.type_name}.')
        return raw

    def _coerce_type(self, raw: str) -> Any:
        if self.type_name == TYPE_INTEGER:
            if set(raw) == {"-"}:
                return None
            return int(raw)
        if self.type_name == TYPE_NUMERIC:
            return float(raw)
        if self.type_name == TYPE_NUMERIC_SIGNED:
            return float(raw)
        if self.type_name in {TYPE_ALPHABETIC, TYPE_ALPHANUMERIC, TYPE_TEXT}:
            return raw
        return raw

    def parse(self, raw: str) -> Any | None:
        """Parse raw text into a Python value."""
        validated = self._validate_raw(raw)
        if validated is None:
            return None
        return self._coerce_type(validated)

    def encode(self, value: Any | None) -> str:
        """Encode a Python value to raw text."""
        if value in (None, ""):
            if self._is_required():
                raise EuringConstraintException('Required field, empty value "" is not permitted.')
            return ""

        if self.key == "geographical_coordinates" and isinstance(value, dict):
            if "lat" not in value or "lng" not in value:
                raise EuringConstraintException("Geographical coordinates require both lat and lng values.")
            return f"{euring_lat_to_dms(float(value['lat']))}{euring_lng_to_dms(float(value['lng']))}"

        str_value = f"{value}"
        if self.type_name in {TYPE_NUMERIC, TYPE_NUMERIC_SIGNED}:
            str_value = str_value.rstrip("0").rstrip(".")
        if (
            self.type_name in {TYPE_INTEGER, TYPE_NUMERIC, TYPE_NUMERIC_SIGNED}
            and self.length
            and not self.variable_length
        ):
            str_value = str_value.zfill(self.length)
        self._validate_length(str_value)
        if self.type_name and not is_valid_type(str_value, self.type_name):
            raise EuringTypeException(f'Value "{str_value}" is not valid for type {self.type_name}.')
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
            return self._coerce_type(validated)
        return self.parser(validated)

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
    if "type" in definition and "type_name" not in definition:
        raise ValueError('Field definitions must use "type_name" instead of legacy "type".')
    type_name = definition.get("type_name") or ""
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
            type_name=type_name,
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
            type_name=type_name,
            required=required,
            length=length,
            variable_length=variable_length,
            empty_value=empty_value,
            lookup=lookup,
        )
    return EuringField(
        key=key,
        name=name,
        type_name=type_name,
        required=required,
        length=length,
        variable_length=variable_length,
        empty_value=empty_value,
    )
