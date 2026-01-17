FORMAT_EURING2000 = "euring2000"
FORMAT_EURING2000PLUS = "euring2000plus"
FORMAT_EURING2020 = "euring2020"
FORMAT_JSON = "json"

FORMAT_VALUES = {
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
}

FORMAT_NAMES = {
    FORMAT_EURING2000: "EURING2000",
    FORMAT_EURING2000PLUS: "EURING2000+",
    FORMAT_EURING2020: "EURING2020",
}


def normalize_format(format: str) -> str:
    """Normalize string to EURING format constant."""
    raw = format.strip()
    if raw in FORMAT_VALUES:
        return raw
    raise ValueError(
        f'Unknown format "{format}". Use {FORMAT_EURING2000}, {FORMAT_EURING2000PLUS}, or {FORMAT_EURING2020}.'
    )


def format_display_name(format: str) -> str:
    """Return the formal display name for an internal EURING format value."""
    try:
        return FORMAT_NAMES[format]
    except KeyError as exc:
        raise ValueError(f'Unknown format "{format}".') from exc


def format_hint(format: str) -> str | None:
    """Suggest the closest machine-friendly format name."""
    raw = format.strip()
    lower = raw.lower()
    if lower in FORMAT_VALUES:
        return lower
    if "2020" in lower:
        return FORMAT_EURING2020
    if "2000" in lower:
        if "plus" in lower or "+" in lower:
            return FORMAT_EURING2000PLUS
        return FORMAT_EURING2000
    return None


def unknown_format_error(format: str, name: str = "format") -> str:
    """Return an error message for an unknown EURING format."""
    hint = format_hint(format)
    message = f'Unknown {name} "{format}". Use {FORMAT_EURING2000}, {FORMAT_EURING2000PLUS}, or {FORMAT_EURING2020}."'
    if hint:
        message = f"{message}\nDid you mean {hint}?"
    return message
