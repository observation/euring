Command Line Interface
======================

The ``euring`` CLI exposes decoding, validation, and lookup helpers for EURING2000, EURING2000+, and EURING2020.

Examples:

.. code-block:: bash

   # Decode a EURING record
   euring decode "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

   # Decode a EURING record as JSON (includes a _meta.generator block)
   euring decode --json --pretty "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

   # Validate a value
   euring validate ABC alphabetic

   # Look up codes (verbose by default)
   euring lookup place GR83

   # Short lookup output
   euring lookup place GR83 --short

   # Lookup output as JSON (includes a _meta.generator block)
   euring lookup --json --pretty place GR83

Options:

``decode``
  ``--json``  Output JSON instead of text.
  ``--pretty``  Pretty-print JSON output (use with ``--json``).
  ``--format``  Force format: 2000, 2000+, 2020, or the aliases ``2000plus``/``2000p``.

``lookup``
  ``--short``  Show concise output.
  ``--json``  Output JSON instead of text.
  ``--pretty``  Pretty-print JSON output (use with ``--json``).
