"""Shared validation helpers for record-level EURING rules."""

from __future__ import annotations

from .fields import EURING2020_ONLY_KEYS, EURING_KEY_NAME, NON_EURING2000_KEYS
from .formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, FORMAT_EURING2020


def field_name_for_key(key: str) -> str:
    """Return the field name for a key, falling back to the key."""
    return EURING_KEY_NAME.get(key, key)


def accuracy_of_coordinates_is_alpha(values_by_key: dict[str, str]) -> bool:
    """Return True when accuracy_of_coordinates is alphabetic."""
    accuracy_of_coordinates = values_by_key.get("accuracy_of_coordinates", "")
    return bool(accuracy_of_coordinates) and accuracy_of_coordinates.isalpha()


def matches_euring2000(values_by_key: dict[str, str]) -> bool:
    """Return True when values are present only for fields in EURING2000 format."""
    for key in NON_EURING2000_KEYS:
        if values_by_key.get(key):
            return False
    return True


def requires_euring2000plus(values_by_key: dict[str, str]) -> bool:
    """Return True when values are present for fields that are not in EURING2000 format."""
    return not matches_euring2000(values_by_key)


def requires_euring2020(values_by_key: dict[str, str]) -> bool:
    """Return True when values require EURING2020."""
    if accuracy_of_coordinates_is_alpha(values_by_key):
        return True
    for key in EURING2020_ONLY_KEYS:
        if values_by_key.get(key):
            return True
    return False


def record_rule_errors(format: str, values_by_key: dict[str, str]) -> list[dict[str, str]]:
    """Return record-level validation errors for the current values."""
    errors: list[dict[str, str]] = []

    def _error(key, message):
        return {
            "key": key,
            "message": message,
            "value": values_by_key.get(key, "") or "",
        }

    if format == FORMAT_EURING2020:
        geographical_coordinates = values_by_key.get("geographical_coordinates", "") or ""
        latitude = values_by_key.get("latitude", "") or ""
        longitude = values_by_key.get("longitude", "") or ""
        if latitude or longitude:
            if geographical_coordinates and geographical_coordinates != "." * 15:
                errors.append(
                    _error(
                        key="geographical_coordinates",
                        message="When Latitude/Longitude are provided, Geographical Co-ordinates must be 15 dots.",
                    )
                )
        if latitude and not longitude:
            errors.append(
                _error(key="longitude", message="Longitude is required when Latitude is provided."),
            )
        if longitude and not latitude:
            errors.append(
                _error(
                    key="latitude",
                    message="Latitude is required when Longitude is provided.",
                )
            )
    else:
        if accuracy_of_coordinates_is_alpha(values_by_key):
            errors.append(
                _error(
                    key="accuracy_of_coordinates",
                    message="Alphabetic accuracy codes are only valid in EURING2020.",
                )
            )
        if format == FORMAT_EURING2000:
            for key in NON_EURING2000_KEYS:
                value = values_by_key.get(key, "")
                if not value:
                    continue
                errors.append(
                    _error(
                        key=key,
                        message="Fields beyond the EURING2000 fixed-width layout are not allowed.",
                    )
                )
        if format == FORMAT_EURING2000PLUS:
            for key in EURING2020_ONLY_KEYS:
                value = values_by_key.get(key, "")
                if not value:
                    continue
                errors.append(
                    _error(
                        key=key,
                        message="EURING2020-only fields require EURING2020 format.",
                    )
                )
    return errors
