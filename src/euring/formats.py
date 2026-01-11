FORMAT_EURING2000 = "euring2000"
FORMAT_EURING2000PLUS = "euring2000plus"
FORMAT_EURING2020 = "euring2020"

FORMAT_CANON_EURING2000 = "EURING2000"
FORMAT_CANON_EURING2000PLUS = "EURING2000+"
FORMAT_CANON_EURING2020 = "EURING2020"


def normalize_format(format: str) -> str:
    """Normalize string to EURING format constant."""
    raw = format.strip().lower()
    if raw in {FORMAT_EURING2000, FORMAT_EURING2000PLUS, FORMAT_EURING2020}:
        return raw
    raise ValueError(
        f'Unknown format "{format}". Use {FORMAT_EURING2000}, {FORMAT_EURING2000PLUS}, or {FORMAT_EURING2020}.'
    )
