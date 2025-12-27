"""Tests for EURING exceptions."""

from euring.exceptions import EuringException, EuringParseException


def test_exception_inheritance():
    error = EuringParseException("bad input")
    assert isinstance(error, EuringParseException)
    assert isinstance(error, EuringException)
