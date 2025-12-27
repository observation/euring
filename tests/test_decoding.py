"""Tests for EURING record decoding."""

import pytest

from euring import EuringDecoder, euring_decode_record
from euring.decoders import euring_decode_value
from euring.exceptions import EuringParseException
from euring.types import TYPE_INTEGER
from euring.codes import lookup_date


class TestDecoding:
    def test_decode_minimal_record(self):
        # Very minimal EURING record for testing
        record = euring_decode_record(
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|+0000000+0000000|1|9|99|0|4"
        )
        assert record["format"] == "EURING2000+"
        assert record["scheme"] == "GBB"
        assert "data" in record
        assert "Ringing Scheme" in record["data"]

    def test_decode_value_with_lookup(self):
        result = euring_decode_value("01012024", TYPE_INTEGER, length=8, lookup=lookup_date)
        assert result["value"] == "01012024"
        assert result["description"].isoformat() == "2024-01-01"

    def test_decode_value_invalid_type(self):
        with pytest.raises(EuringParseException):
            euring_decode_value("ABC", TYPE_INTEGER, length=3)

    def test_decoder_handles_non_string(self):
        decoder = EuringDecoder(None)
        results = decoder.get_results()
        assert results["errors"]
