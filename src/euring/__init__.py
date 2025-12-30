"""
EURING data processing library.

This package provides functionality to decode and validate EURING (European Union for Bird Ringing) data records.
EURING is the standard format for bird ringing data exchange in Europe.

Main features:
- Decode EURING 2000 and 2000+ format records
- Validate field types and formats
- Parse geographical coordinates
- Look up code meanings
"""

from .__about__ import __version__
from .builder import EuringRecordBuilder
from .converters import convert_euring2000_record, convert_euring_record
from .decoders import EuringDecoder, euring_decode_record
from .exceptions import EuringException, EuringParseException
from .types import (
    TYPE_ALPHABETIC,
    TYPE_ALPHANUMERIC,
    TYPE_INTEGER,
    TYPE_NUMERIC,
    TYPE_NUMERIC_SIGNED,
    TYPE_TEXT,
    is_alphabetic,
    is_alphanumeric,
    is_integer,
    is_numeric,
    is_numeric_signed,
    is_text,
    is_valid_type,
)
from .utils import (
    euring_coord_to_dms,
    euring_dms_to_float,
    euring_float_to_dms,
    euring_identification_display_format,
    euring_identification_export_format,
    euring_lat_to_dms,
    euring_lng_to_dms,
    euring_scheme_export_format,
    euring_species_export_format,
)

__all__ = [
    "__version__",
    "EuringRecordBuilder",
    "euring_decode_record",
    "convert_euring2000_record",
    "convert_euring_record",
    "EuringDecoder",
    "EuringRecordBuilder",
    "TYPE_ALPHABETIC",
    "TYPE_ALPHANUMERIC",
    "TYPE_INTEGER",
    "TYPE_NUMERIC",
    "TYPE_NUMERIC_SIGNED",
    "TYPE_TEXT",
    "is_alphabetic",
    "is_alphanumeric",
    "is_integer",
    "is_numeric",
    "is_numeric_signed",
    "is_text",
    "is_valid_type",
    "EuringException",
    "EuringParseException",
    "euring_dms_to_float",
    "euring_float_to_dms",
    "euring_coord_to_dms",
    "euring_lat_to_dms",
    "euring_lng_to_dms",
    "euring_identification_display_format",
    "euring_identification_export_format",
    "euring_scheme_export_format",
    "euring_species_export_format",
]
