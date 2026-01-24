class EuringException(Exception):
    """Base exception for EURING errors."""


class EuringTypeException(EuringException):
    """Raised when a value does not satisfy its declared EURING type."""


class EuringConstraintException(EuringException):
    """Raised when a value violates field constraints beyond type."""


class EuringLookupException(EuringException):
    """Raised when a lookup value cannot be resolved."""
