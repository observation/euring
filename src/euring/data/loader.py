from __future__ import annotations

import importlib
from collections.abc import Callable
from functools import cache
from typing import Any


@cache
def load_data(name: str) -> Any | None:
    return _load_code_table_module(name)


def _load_code_table_module(name: str) -> Any | None:
    module_name = f"euring.data.code_table_{name}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None
    return getattr(module, "TABLE", None)


def load_table(name: str) -> list[dict[str, Any]] | None:
    data = load_data(name)
    if not data:
        return None
    return data if isinstance(data, list) else None


def normalize_code(code: Any) -> str | None:
    if code is None:
        return None
    if isinstance(code, bool):
        return str(int(code))
    if isinstance(code, (int, float)):
        return str(int(code))
    code_str = str(code).strip()
    if code_str in {"—", "–"}:
        return "--"
    return code_str


def load_code_map(
    filename: str,
    *,
    code_key: str = "code",
    value_key: str = "description",
    code_filter: Callable[[str], bool] | None = None,
) -> dict[str, str]:
    data = load_data(filename)
    if not data:
        return {}
    result: dict[str, str] = {}
    for item in data:
        code = normalize_code(item.get(code_key))
        if not code:
            continue
        if code_filter and not code_filter(code):
            continue
        value = item.get(value_key)
        if value is None:
            continue
        result[code] = value
    return result


def load_other_marks_data() -> dict[str, dict[str, str]] | None:
    data = load_data("other_marks_information")
    if not data:
        return None
    special_cases = {normalize_code(item["code"]): item["description"] for item in data.get("special_cases", [])}
    first_character = {normalize_code(item["code"]): item["description"] for item in data.get("first_character", [])}
    second_character = {normalize_code(item["code"]): item["description"] for item in data.get("second_character", [])}
    return {
        "special_cases": {k: v for k, v in special_cases.items() if k},
        "first_character": {k: v for k, v in first_character.items() if k},
        "second_character": {k: v for k, v in second_character.items() if k},
    }


def load_named_code_map(
    filename: str,
    *,
    name_key: str = "name",
) -> dict[str, str]:
    data = load_data(filename)
    if not data:
        return {}
    result: dict[str, str] = {}
    for item in data:
        code = normalize_code(item.get("code"))
        if not code:
            continue
        name = item.get(name_key) or item.get("description")
        if not name:
            continue
        result[code] = name
    return result


def load_place_map() -> dict[str, str]:
    data = load_table("places")
    if not data:
        return {}
    result: dict[str, str] = {}
    for row in data:
        place_code = normalize_code(row.get("place_code"))
        if not place_code:
            continue
        name = (row.get("country") or row.get("code") or "").strip()
        region = (row.get("region") or "").strip()
        if name and region:
            value = f"{name} ({region})"
        else:
            value = name or region
        if value:
            result[place_code] = value
    return result


def load_place_details() -> dict[str, dict[str, Any]]:
    """Load place code details keyed by place code."""
    data = load_table("places")
    if not data:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in data:
        place_code = normalize_code(item.get("place_code"))
        if not place_code:
            continue
        result[place_code] = {**item, "place_code": place_code}
    return result


def load_species_details() -> dict[str, dict[str, Any]]:
    """Load species details keyed by species code."""
    data = load_table("species")
    if not data:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in data:
        code = normalize_code(item.get("code"))
        if not code:
            continue
        result[code] = {**item, "code": code}
    return result


def load_scheme_details() -> dict[str, dict[str, Any]]:
    """Load ringing scheme details keyed by scheme code."""
    data = load_table("schemes")
    if not data:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in data:
        code = normalize_code(item.get("code"))
        if not code:
            continue
        result[code] = {**item, "code": code}
    return result


def load_species_map() -> dict[str, str]:
    return load_named_code_map("species", name_key="name")


def load_scheme_map() -> dict[str, str]:
    data = load_table("schemes")
    if not data:
        return {}
    result: dict[str, str] = {}
    for item in data:
        code = normalize_code(item.get("code"))
        if not code:
            continue
        country = item.get("country") or ""
        centre = item.get("ringing_centre") or ""
        if centre and country:
            value = f"{centre}, {country}"
        else:
            value = centre or country
        if value:
            result[code] = value
    return result
