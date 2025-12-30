# euring

[![CI](https://github.com/observation/euring/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/observation/euring/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/observation/euring/badge.svg?branch=main)](https://coveralls.io/github/observation/euring?branch=main)
[![Latest PyPI version](https://img.shields.io/pypi/v/euring.svg)](https://pypi.org/project/euring/)

A Python library and CLI for decoding, validating, and working with EURING bird ringing data records (EURING2000, EURING2000+, EURING2020).

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

# Decode with an explicit format hint (aliases: EURING2000+ / EURING2000P)
euring decode --format euring2020 "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"
euring decode --format euring2000plus "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

# Validate a EURING record (errors only)
euring validate "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"

# Validate a file of EURING records
euring validate --file euring_records.psv

# Look up codes
euring lookup scheme GBB
euring lookup species 00010

# Look up a code and ouput result as JSON (includes a _meta.generator block)
euring lookup --json --pretty scheme GBB

# Dump code tables as JSON (includes a _meta.generator block)
euring dump --pretty age

# Dump all code tables to a directory
euring dump --all --output-dir ./code_tables

# Convert records between EURING2000, EURING2000+, and EURING2020
euring convert "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000"
euring convert --to euring2020 "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000"
euring convert --to euring2000 --force "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"
euring convert --from euring2020 --to euring2000plus --force "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00||A|9|99|0|4|00000|000|00000|||||52.3760|4.9000||"

```

### Python Library

```python
from euring import EuringRecordBuilder, euring_decode_record, is_valid_type, TYPE_ALPHABETIC

# Decode a record
record = euring_decode_record(
    "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"
)

# Build a record (EURING2000+ by default)
builder = EuringRecordBuilder()
builder.set("ringing_scheme", "GBB")
builder.set("primary_identification_method", "A0")
builder.set("identification_number", "1234567890")
builder.set("place_code", "AB00")
builder.set("geographical_coordinates", "+0000000+0000000")
builder.set("accuracy_of_coordinates", "1")
record = builder.build()

# Validate a value
is_valid = is_valid_type("ABC", TYPE_ALPHABETIC)
```

Decoded records expose two field mappings:

- `data`: keyed by the official EURING field name (as in the manual)
- `data_by_key`: keyed by a stable ASCII snake_case `key` for programmatic use

Each field entry includes the raw `value`, a human-readable `description` (when available), and the `key`.

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

This package introduces a signed numeric type (`NumericSigned`) for the EURING2020 fields Latitude and Longitue. `NumericSigned` behaves like `Numeric`, but allows a leading minus sign and explicitly disallows -0. `NumericSigned` is a small, intentional clarification of the generic numeric types. The manuals clearly permit negative Latitude and Longitude in EURING2020, but the generic `Numeric` definition does not describe signed numbers. Making this explicit in the code helps prevent invalid values while staying faithful to the manuals and real-world usage. If a future revision of the specification formally defines signed numeric fields, this implementation can align with it without breaking compatibility.

### Field keys

For programmatic use, each field also has a stable ASCII [snake_case](https://en.wikipedia.org/wiki/Snake_case) `key`.

The EURING manuals use field names that may include spaces, hyphens, and mixed case. In many programming environments these are awkward to work with (for example when used as object attributes, column names, or identifiers in code). To make decoded output easier to use in Python, JSON, R, and similar tools, the library exposes a normalized ASCII snake_case `key` for every field.

These keys are provided as a practical convenience for developers. They are not part of the formal EURING specification, and consuming systems are free to map them to their own conventions where needed.

## EURING Reference Data

This package ships with EURING reference data in `src/euring/data`.

- All EURING Code tables follow the EURING Manual.
- EURING-published updates for species, schemes, places, and circumstances are curated and checked into the package.
- End users do not need to refresh data separately.

### Data sources

- Species codes: <https://www.euring.org/files/documents/EURING_SpeciesCodes_IOC15_1.csv>
- Place codes: <https://www.euring.org/files/documents/ECPlacePipeDelimited_0.csv>
- Schemes: <https://app.bto.org/euringcodes/schemes.jsp?check1=Y&check2=Y&check3=Y&check4=Y&orderBy=SCHEME_CODE>
- Circumstances: <https://app.bto.org/euringcodes/circumstances.jsp>
- All other code tables are derived from the EURING Exchange Code 2020.

## References

- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. Helsinki, Finland ISBN 978-952-94-4399-4
- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. On-line Code Tables. Thetford, U.K. URL https://www.euring.org/data-and-codes/euring-codes

## Acknowledgements

This library is maintained and open-sourced by [Observation.org](https://observation.org). It was originally developed as part of the RingBase project at [Zostera](https://zostera.nl). Many thanks to Zostera for the original development work.
