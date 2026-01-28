#!/usr/bin/env python3
"""Example usage of the EURING library."""

from euring import (
    TYPE_ALPHABETIC,
    TYPE_INTEGER,
    EuringException,
    EuringRecord,
    is_valid_euring_type,
)
from euring.coordinates import euring_coordinates_to_lat_lng, lat_lng_to_euring_coordinates


def main():
    print("EURING Library Demo")
    print("=" * 20)

    # Test type validation
    print("\n1. Type Validation:")
    print(f"is_alphabetic('ABC'): {is_valid_euring_type('ABC', TYPE_ALPHABETIC)}")
    print(f"is_alphabetic('abc'): {is_valid_euring_type('abc', TYPE_ALPHABETIC)}")
    print(f"is_integer('123'): {is_valid_euring_type('123', TYPE_INTEGER)}")
    print(f"is_integer('12.3'): {is_valid_euring_type('12.3', TYPE_INTEGER)}")

    # Test coordinate conversion
    print("\n2. Coordinate Conversion:")
    euring_geographical_coordinates = "+420500+0000000"
    wgs84 = euring_coordinates_to_lat_lng(euring_geographical_coordinates)
    lat = wgs84["lat"]
    lng = wgs84["lng"]
    encoded_lat_lng = lat_lng_to_euring_coordinates(lat, lng)
    print(
        f"Encoded coordinates: {euring_geographical_coordinates}"
        f" -> Lat: {lat}, Lng: {lng}"
        f" -> Back to encoded coordinates: {encoded_lat_lng}"
    )

    # Test decoding (using a minimal example)
    print("\n3. Record Decoding:")
    # This is a simplified example - real EURING records are much longer
    try:
        # This will fail because it's incomplete, but shows the structure
        record = EuringRecord.decode(
            "GBB|A0|1234567890|0|1|ZZ|00001|00001|N|0|M|U|U|U|2|2|U|01012024|0|0000|----|+0000000+0000000|1|9|99|0|4"
        )
        print("Decoded successfully!")
        print(f"Format: {record.display_format}")
        print(f"Fields decoded: {len(record.fields)}")
    except EuringException as e:
        print(f"Parse error (expected for incomplete record): {e}")

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
