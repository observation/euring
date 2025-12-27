"""Tests for EURING record decoding."""

from euring import euring_decode_record


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
