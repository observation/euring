Python Reference
================

Public API
~~~~~~~~~~

.. automodule:: euring
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: __all__

Usage examples
~~~~~~~~~~~~~~

Build a EURING record:

.. code-block:: python

   from euring import EuringRecordBuilder

   builder = EuringRecordBuilder("euring2000plus")
   builder.set("ringing_scheme", "GBB")
   builder.set("primary_identification_method", "A0")
   builder.set("identification_number", "1234567890")
   builder.set("place_code", "AB00")
   builder.set("geographical_coordinates", "+0000000+0000000")
   builder.set("accuracy_of_coordinates", "1")
   record = builder.build()

``build()`` raises ``ValueError`` if required fields are missing or a value
fails validation. Use ``EuringRecordBuilder("euring2000plus", strict=False)``
to allow missing optional values and keep placeholders in the output.
