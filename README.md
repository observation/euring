# euring

[![CI](https://github.com/observation/euring/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/observation/euring/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/observation/euring/badge.svg?branch=main)](https://coveralls.io/github/observation/euring?branch=main)
[![Latest PyPI version](https://img.shields.io/pypi/v/euring.svg)](https://pypi.org/project/euring/)

A Python library and CLI for decoding, validating, and converting EURING ringing and recovery records (EURING2000, EURING2000+, EURING2020).

The full documentation is at <https://euring.readthedocs.org>.

Issues can be reported at <https://github.com/observation/euring/issues>.

## What are EURING Codes?

[EURING](https://www.euring.org) is the European Union for Bird Ringing.

[EURING Codes](https://www.euring.org/data-and-codes) are standards for recording and exchanging bird ringing and recovery data. The EURING Codes are written, published and maintained by EURING.

## Requirements

- A [supported Python version](https://devguide.python.org/versions/)
- [Typer](https://typer.tiangolo.com/) for CLI functionality

## Installation

```bash
pip install euring
```

## Usage

### Command Line

```bash
# Decode a EURING record
euring decode "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

# Decode a EURING record as JSON (includes a _meta.generator block)
euring decode --json --pretty "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

# Decode with an explicit format
euring decode --format euring2020 "DER|A0|CD...52065|0|1|ZZ|18770|18770|N|0|Z|U|F|F|2|2|U|--|--|-|08101971|0|----|DECK|...............|G|8|20|0|3|00000|000|00000||||||||||||||||||||||||||||50.4000|7.7000||"
euring decode --format euring2000plus "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"

# Validate a EURING record (errors only)
euring validate "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"

# Validate a file of EURING records
euring validate --file euring_records.psv
euring validate --file euring_records.psv --json --output validation.json

# Look up codes
euring lookup ringing_scheme GBB
euring lookup species 00010

# Look up a code and ouput result as JSON (includes a _meta.generator block)
euring lookup --json --pretty ringing_scheme GBB

# Dump code tables as JSON (includes a _meta.generator block)
euring dump --pretty age

# Dump all code tables to a directory
euring dump --all --output-dir ./code_tables

# Convert records between EURING2000, EURING2000+, and EURING2020
euring convert --to euring2020 "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000"
euring convert --to euring2000 --force "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"
euring convert --from euring2020 --to euring2000plus --force "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00||A|9|99|0|4|00000|000|00000|||||52.3760|4.9000||"
euring convert --file euring_records.txt --to euring2020 --output converted_records.txt

# Decode a file of EURING records to JSON (enriched output)
euring decode --file euring_records.txt --json --output decoded_records.json

```

Decoded JSON structure (single record):

```json
{
  "record": {
    "format": "EURING2000+"
  },
  "fields": {
    "ringing_scheme": {"name": "Ringing Scheme", "value": "ESA", "order": 0},
    "primary_identification_method": {"name": "Primary Identification Method", "value": "A0", "order": 1}
    // ...
  },
  "errors": {
    "record": [],
    "fields": []
  },
  "_meta": {
    "generator": {"name": "euring", "version": "X.Y.Z", "url": "https://github.com/observation/euring"}
  }
}
```

### Python Library

```python
from euring import EuringRecord, is_valid_type, TYPE_ALPHABETIC

# Decode a record
record = EuringRecord.decode(
    "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"
)

# Build a record (EURING2000+ example)
record = EuringRecord("euring2000plus")
record.set("ringing_scheme", "GBB")
record.set("primary_identification_method", "A0")
record.set("identification_number", "1234567890")
record.set("place_code", "AB00")
record.set("geographical_coordinates", "+0000000+0000000")
record.set("accuracy_of_coordinates", "1")
record_str = record.serialize()
record_json = record.serialize(output_format="json")
record_2020 = record.export("euring2020")

# Validate a value
is_valid = is_valid_type("ABC", TYPE_ALPHABETIC)
```

Decoded records expose a single `fields` mapping keyed by the stable ASCII
snake_case field `key`. Each field entry includes the official `name`, the raw
`value`, and an `order` index for stable sorting.

## Data definition

EURING vocabulary (as per the manuals):

- Record: one encounter record.
- Field: a single data element within a record.
- Field name: the official EURING name for a field.
- Type: the data type assigned to a field (Alphabetic, Alphanumeric, Integer, Numeric, Text).
- Code: the coded value stored in a field.
- Code table: the reference table that maps codes to descriptions.
- Column: fixed-width position in EURING2000 records.

EURING uses a record-based format: each record contains a fixed sequence of fields.
The manuals define official field names (with spaces/hyphens), which we preserve for display.

This package introduces a signed numeric type (`NumericSigned`) for the EURING2020 fields Latitude and Longitude. `NumericSigned` behaves like `Numeric`, but allows a leading minus sign and explicitly disallows -0. `NumericSigned` is a small, intentional clarification of the generic numeric types. The manuals clearly permit negative Latitude and Longitude in EURING2020, but the generic `Numeric` definition does not describe signed numbers. Making this explicit in the code helps prevent invalid values while staying faithful to the manuals and real-world usage. If a future revision of the specification formally defines signed numeric fields, this implementation can align with it without breaking compatibility.

### Field keys

For programmatic use, each field also has a stable ASCII [snake_case](https://en.wikipedia.org/wiki/Snake_case) `key`.

The EURING manuals use field names that may include spaces, hyphens, and mixed case. In many programming environments these are awkward to work with (for example when used as object attributes, column names, or identifiers in code). To make decoded output easier to use in Python, JSON, R, and similar tools, the library exposes a normalized ASCII snake_case `key` for every field.

These keys are provided as a practical convenience for developers. They are not part of the formal EURING specification, and consuming systems are free to map them to their own conventions where needed.

## EURING Reference Data

This package ships with EURING reference data in `src/euring/data`.

- All EURING Code tables follow the EURING Manual.
- EURING-published updates for Species, Ringing Schemes, Place Codes, and Circumstances are curated and checked into the package.
- End users do not need to refresh data separately.

### Data sources

- Species: <https://www.euring.org/files/documents/EURING_SpeciesCodes_IOC15_1.csv>
- Place Codes: <https://www.euring.org/files/documents/ECPlacePipeDelimited_0.csv>
- Ringing Schemes: <https://app.bto.org/euringcodes/schemes.jsp?check1=Y&check2=Y&check3=Y&check4=Y&orderBy=SCHEME_CODE>
- Circumstances: <https://app.bto.org/euringcodes/circumstances.jsp>
- All other code tables are derived from the EURING Exchange Code 2020.

## References

- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. Helsinki, Finland ISBN 978-952-94-4399-4
- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. On-line Code Tables. Thetford, U.K. URL https://www.euring.org/data-and-codes/euring-codes

## Acknowledgements

This library is maintained by [Observation.org](https://observation.org). It was originally developed as part of the RingBase project at [Zostera](https://zostera.nl). Many thanks to Zostera for the original development work.
