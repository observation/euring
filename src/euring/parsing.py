from collections.abc import Callable, Mapping
from typing import Any

from .field_schema import coerce_field


def euring_decode_value(
    value: str,
    type: str,
    required: bool = True,
    length: int | None = None,
    variable_length: bool = False,
    value_type: str | None = None,
    parser: Callable[[str], Any] | None = None,
    lookup: Mapping[str, str] | Callable[[str], str] | None = None,
) -> dict[str, Any] | None:
    """Decode a single EURING field value with type checks, parsing, and lookup."""
    definition = {
        "name": "Value",
        "key": "value",
        "euring_type": type,
        "value_type": value_type,
        "required": required,
        "length": length,
        "variable_length": variable_length,
        "parser": parser,
        "lookup": lookup,
    }
    field = coerce_field(definition)
    parsed = field.parse(value)
    if parsed is None:
        return None
    results: dict[str, Any] = {"raw_value": value, "value": parsed}
    if parser:
        results["parsed_value"] = parsed
    description_value = parsed
    if lookup and not parser and value != "" and parsed is not None:
        description_value = value
    results["description"] = field.describe(description_value)
    return results
