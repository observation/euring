"""Tests for EURING exceptions."""

from euring.exceptions import (
    EuringConstraintException,
    EuringException,
    EuringLookupException,
    EuringTypeException,
)


def test_exception_inheritance():
    error = EuringException("bad input")
    assert isinstance(error, EuringException)


def test_specific_exceptions_inherit_from_base():
    for exc_type in (EuringTypeException, EuringConstraintException, EuringLookupException):
        error = exc_type("bad input")
        assert isinstance(error, exc_type)
        assert isinstance(error, EuringException)
