from __future__ import annotations

from .formats import FORMAT_EURING2020
from .record import _convert_record_string


def convert_euring_record(
    value: str,
    source_format: str | None = None,
    target_format: str = FORMAT_EURING2020,
    force: bool = False,
) -> str:
    """Convert EURING records between euring2000, euring2000plus, and euring2020."""
    return _convert_record_string(
        value,
        source_format=source_format,
        target_format=target_format,
        force=force,
    )
