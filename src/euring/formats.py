FORMAT_EURING2000 = "euring2000"
FORMAT_EURING2000PLUS = "euring2000plus"
FORMAT_EURING2020 = "euring2020"

FORMAT_CANON_EURING2000 = "EURING2000"
FORMAT_CANON_EURING2000PLUS = "EURING2000+"
FORMAT_CANON_EURING2020 = "EURING2020"

FORMAT_CANON_NAMES = {
    FORMAT_EURING2000: FORMAT_CANON_EURING2000,
    FORMAT_EURING2000PLUS: FORMAT_CANON_EURING2000PLUS,
    FORMAT_EURING2020: FORMAT_CANON_EURING2020,
}

FORMAT_VALUES = {
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
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
        return FORMAT_CANON_NAMES[format]
    except KeyError as exc:
        raise ValueError(f'Unknown format "{format}".') from exc


def format_hint(format: str) -> str | None:
    """Suggest the closest machine-friendly format name."""
    raw = format.strip()
    lower = raw.lower()
    if lower in FORMAT_VALUES:
        return lower
    if lower in {"2000", "2000plus", "2020"}:
        return f"euring{lower}"
    if lower in {"2000+", "euring2000+"}:
        return FORMAT_EURING2000PLUS
    if lower in {"euring2000", "euring2000plus", "euring2020"}:
        return lower
    return None
