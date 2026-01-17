"""Tests for record_rules helpers."""

from euring.rules import (
    EURING2000_KEYS,
    EURING2000PLUS_KEYS,
    EURING2020_KEYS,
    EURING2020_ONLY_KEYS,
    NON_EURING2000_KEYS,
    matches_euring2000,
    record_rule_errors,
    requires_euring2000plus,
    requires_euring2020,
)


def test_fields_per_format():
    # EURING2020 Code Manual Page4-5
    assert len(EURING2000_KEYS) == 33
    assert len(EURING2000PLUS_KEYS) == 60
    assert len(EURING2020_KEYS) == 64
    assert len(NON_EURING2000_KEYS) == 64 - 33


def test_matches_euring2000_true_without_extra_values():
    values = {key: "" for key in EURING2020_ONLY_KEYS}
    assert matches_euring2000(values)


def test_matches_euring2000_false_with_2020_value():
    values = {"latitude": "52.3760"}
    assert not matches_euring2000(values)


def test_requires_euring2000plus_when_non_2000_value():
    values = {"latitude": "52.3760"}
    assert requires_euring2000plus(values)


def test_requires_euring2020_for_alpha_accuracy():
    values = {"accuracy_of_coordinates": "A"}
    assert requires_euring2020(values)


def test_record_rule_errors_for_euring2000plus_with_2020_only():
    values = {"latitude": "52.3760"}
    errors = record_rule_errors("euring2000plus", values)
    assert any(error["key"] == "latitude" for error in errors)


def test_record_rule_errors_for_euring2000_extra_fields():
    values = {"latitude": "52.3760"}
    errors = record_rule_errors("euring2000", values)
    assert any("fixed-width" in error["message"] for error in errors)


def test_record_rule_errors_for_euring2020_missing_latitude():
    values = {"geographical_coordinates": "...............", "latitude": "", "longitude": "2.0000"}
    errors = record_rule_errors("euring2020", values)
    assert any(error["key"] == "latitude" for error in errors)
