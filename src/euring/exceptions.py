class EuringException(Exception):
    """Base exception for EURING errors."""

    pass


class EuringParseException(EuringException):
    """Raised when EURING parsing or validation fails."""

    pass
