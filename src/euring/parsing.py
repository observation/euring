from collections.abc import Callable, Mapping
from typing import Any

from .field_model import coerce_field


def euring_decode_value(
    value: str,
    type: str,
    required: bool = True,
    length: int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    parser: Callable[[str], Any] | None = None,
    lookup: Mapping[str, str] | Callable[[str], str] | None = None,
) -> dict[str, Any] | None:
    """Decode a single EURING field value with type checks, parsing, and lookup."""
    definition = {
        "name": "Value",
        "key": "value",
        "type": type,
        "required": required,
        "length": length,
        "min_length": min_length,
        "max_length": max_length,
        "parser": parser,
        "lookup": lookup,
    }
    field = coerce_field(definition)
    parsed = field.parse(value)
    if parsed is None:
        return None
    results: dict[str, Any] = {"value": value}
    if parser:
        results["parsed_value"] = parsed
    results["description"] = field.describe(parsed)
    return results
