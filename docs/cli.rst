Command Line Interface
======================

The ``euring`` CLI exposes decode/validate/lookup helpers plus JSON dumps and format conversion.

Commands:

- ``decode``     Decode a EURING record string.
- ``validate``   Validate a EURING record and return errors only.
- ``lookup``     Look up EURING codes (scheme, species, place).
- ``dump``       Dump one or more code tables as JSON.
- ``convert``    Convert EURING2000, EURING2000+, and EURING2020 records.

Examples:

.. code-block:: bash

   # Decode a EURING record
   euring decode "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

   # Decode a EURING record as JSON (includes a _meta.generator block)
   euring decode --json --pretty "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

   # Validate a EURING record (errors only)
   euring validate "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|+420500-0044500|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0|||||||||"

   # Validate a file of EURING records
   euring validate --file euring_records.psv

   # Look up codes (verbose by default)
   euring lookup place GR83

   # Short lookup output
   euring lookup place GR83 --short

   # Lookup output as JSON (includes a _meta.generator block)
   euring lookup --json --pretty place GR83

   # Dump code tables as JSON (includes a _meta.generator block)
   euring dump --pretty age

   # Dump all code tables to a directory
   euring dump --all --output-dir ./code_tables

   # Convert records between EURING2000, EURING2000+, and EURING2020
   euring convert "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000"
   euring convert --to euring2020 "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000"
   euring convert --from euring2020 --to euring2000plus --force "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00||A|9|99|0|4|00000|000|00000|||||52.3760|4.9000||"

Options:

``decode``
  ``--json``  Output JSON instead of text.
  ``--pretty``  Pretty-print JSON output (use with ``--json``).
  ``--format``  Force format: ``euring2000``, ``euring2000plus``, or ``euring2020`` (aliases: ``euring2000+``, ``euring2000p``).

``validate``
  ``--json``  Output JSON instead of text.
  ``--pretty``  Pretty-print JSON output (use with ``--json``).
  ``--format``  Force format: ``euring2000``, ``euring2000plus``, or ``euring2020`` (aliases: ``euring2000+``, ``euring2000p``).
  ``--file``  Read records from a text file.

``lookup``
  ``--short``  Show concise output.
  ``--json``  Output JSON instead of text.
  ``--pretty``  Pretty-print JSON output (use with ``--json``).

``convert``
  ``--from``  Source format (optional): ``euring2000``, ``euring2000plus``, or ``euring2020``.
  ``--to``  Target format: ``euring2000``, ``euring2000plus``, or ``euring2020`` (aliases: ``euring2000+``, ``euring2000p``).
  ``--force``  Allow lossy mappings when downgrading from ``euring2020``.

``dump``
  ``--output``  Write JSON to a file.
  ``--output-dir``  Directory to write JSON code tables.
  ``--pretty``  Pretty-print JSON output.
  ``--force``  Overwrite existing files.
  ``--all``  Dump all code tables (requires ``--output-dir``).
