Command Line Interface
======================

The ``euring`` CLI exposes decoding, validation, and lookup helpers.

Examples:

.. code-block:: bash

   # Decode a EURING record
   euring decode "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"

   # Validate a value
   euring validate ABC alphabetic

   # Look up codes (verbose by default)
   euring lookup place GR83

   # Short lookup output
   euring lookup place GR83 --short
