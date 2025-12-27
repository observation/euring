# euring

[![CI](https://github.com/observation/euring/actions/workflows/ci.yml/badge.svg)](https://github.com/observation/euring/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/observation/euring/badge.svg?branch=main)](https://coveralls.io/github/observation/euring?branch=main)
[![Latest PyPI version](https://img.shields.io/pypi/v/euring.svg)](https://pypi.python.org/pypi/euring)

A Python library and CLI for decoding, validating, and working with EURING bird ringing data records.

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
euring decode "GBB|A0|1234567890|0|1|ZZ|00001|00001|N|0|M|U|U|U|2|2|U|01012024|0|0000|----|+0000000+0000000|1|9|99|0|4"

# Validate a value
euring validate ABC alphabetic

# Look up codes
euring lookup scheme GBB
euring lookup species 00001
```

### Python Library

```python
from euring import euring_decode_record, is_valid_type, TYPE_ALPHABETIC

# Decode a record
record = euring_decode_record("GBB|A0|1234567890|...")

# Validate a value
is_valid = is_valid_type("ABC", TYPE_ALPHABETIC)
```

## Attribution

This library is maintained and open-sourced by [Observation.org](https://observation.org). It originated as part of the RingBase project at [Zostera](https://zostera.nl). Many thanks to Zostera for the original development work.
