#!/usr/bin/env python3
"""Example usage of the EURING library."""

from euring import (
    TYPE_ALPHABETIC,
    TYPE_INTEGER,
    EuringParseException,
    euring_decode_record,
    euring_dms_to_float,
    euring_lat_to_dms,
    is_valid_type,
)


def main():
    print("EURING Library Demo")
    print("=" * 20)

    # Test type validation
    print("\n1. Type Validation:")
    print(f"is_alphabetic('ABC'): {is_valid_type('ABC', TYPE_ALPHABETIC)}")
    print(f"is_alphabetic('abc'): {is_valid_type('abc', TYPE_ALPHABETIC)}")
    print(f"is_integer('123'): {is_valid_type('123', TYPE_INTEGER)}")
    print(f"is_integer('12.3'): {is_valid_type('12.3', TYPE_INTEGER)}")

    # Test coordinate conversion
    print("\n2. Coordinate Conversion:")
    dms = "+420500"
    decimal = euring_dms_to_float(dms)
    back_to_dms = euring_lat_to_dms(decimal)
    print(f"DMS: {dms} -> Decimal: {decimal} -> Back to DMS: {back_to_dms}")

    # Test decoding (using a minimal example)
    print("\n3. Record Decoding:")
    # This is a simplified example - real EURING records are much longer
    try:
        # This will fail because it's incomplete, but shows the structure
        record = euring_decode_record(
            "GBB|A0|1234567890|0|1|ZZ|00001|00001|N|0|M|U|U|U|2|2|U|01012024|0|0000|----|+0000000+0000000|1|9|99|0|4"
        )
        print("Decoded successfully!")
        print(f"Format: {record.get('format')}")
        print(f"Animal: {record.get('animal')}")
    except EuringParseException as e:
        print(f"Parse error (expected for incomplete record): {e}")

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
