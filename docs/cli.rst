Command Line Interface
======================

The ``euring`` CLI exposes decoding, validation, and lookup helpers.

Examples:

.. code-block:: bash

   # Decode a EURING record
   euring decode "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|+0000000+0000000|1|9|99|0|4"

   # Validate a value
   euring validate ABC alphabetic

   # Look up codes (verbose by default)
   euring lookup place GR83

   # Short lookup output
   euring lookup place GR83 --short
