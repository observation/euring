from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from .codes import lookup_description
from .exceptions import EuringParseException
from .types import is_valid_type

__all__ = [
    "EuringField",
    "EuringLookupField",
    "EuringFormattedField",
    "coerce_field",
]


@dataclass(frozen=True)
class EuringField(Mapping[str, Any]):
    """Base field definition with parse/encode/validate hooks."""

    key: str
    name: str
    type_name: str = ""
    required: bool = True
    length: int | None = None
    min_length: int | None = None
    max_length: int | None = None

    def _mapping(self) -> dict[str, Any]:
        mapping: dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "type": self.type_name,
            "required": self.required,
        }
        if self.length is not None:
            mapping["length"] = self.length
        if self.min_length is not None:
            mapping["min_length"] = self.min_length
        if self.max_length is not None:
            mapping["max_length"] = self.max_length
        return mapping

    def __getitem__(self, key: str) -> Any:
        return self._mapping()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())

    def _is_required(self) -> bool:
        if self.min_length == 0:
            return False
        return self.required

    def _validate_length(self, raw: str) -> None:
        value_length = len(raw)
        if self.length is not None and value_length != self.length:
            raise EuringParseException(f'Value "{raw}" is length {value_length} instead of {self.length}.')
        if self.min_length is not None and value_length < self.min_length:
            raise EuringParseException(f'Value "{raw}" is length {value_length}, should be at least {self.min_length}.')
        if self.max_length is not None and value_length > self.max_length:
            raise EuringParseException(f'Value "{raw}" is length {value_length}, should be at most {self.max_length}.')

    def parse(self, raw: str) -> Any | None:
        """Parse raw text into a Python value."""
        if raw == "":
            if not self._is_required():
                return None
            raise EuringParseException('Required field, empty value "" is not permitted.')
        self._validate_length(raw)
        if self.type_name and not is_valid_type(raw, self.type_name):
            raise EuringParseException(f'Value "{raw}" is not valid for type {self.type_name}.')
        return raw

    def encode(self, value: Any | None) -> str:
        """Encode a Python value to raw text."""
        if value is None or value == "":
            if self._is_required():
                raise EuringParseException('Required field, empty value "" is not permitted.')
            return ""
        raw = str(value)
        self._validate_length(raw)
        if self.type_name and not is_valid_type(raw, self.type_name):
            raise EuringParseException(f'Value "{raw}" is not valid for type {self.type_name}.')
        return raw

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
        value = super().parse(raw)
        if value is None:
            return None
        if self.parser is None:
            return value
        return self.parser(value)

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
    type_name = definition.get("type") or definition.get("type_name") or ""
    required = definition.get("required", True)
    length = definition.get("length")
    min_length = definition.get("min_length")
    max_length = definition.get("max_length")
    parser = definition.get("parser")
    lookup = definition.get("lookup")
    if parser is not None:
        return EuringFormattedField(
            key=key,
            name=name,
            type_name=type_name,
            required=required,
            length=length,
            min_length=min_length,
            max_length=max_length,
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
            min_length=min_length,
            max_length=max_length,
            lookup=lookup,
        )
    return EuringField(
        key=key,
        name=name,
        type_name=type_name,
        required=required,
        length=length,
        min_length=min_length,
        max_length=max_length,
    )
