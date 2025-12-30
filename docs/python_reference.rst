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

   builder = EuringRecordBuilder()
   builder.set("ringing_scheme", "GBB")
   builder.set("primary_identification_method", "A0")
   builder.set("identification_number", "1234567890")
   builder.set("place_code", "AB00")
   builder.set("geographical_coordinates", "+0000000+0000000")
   builder.set("accuracy_of_coordinates", "1")
   record = builder.build()
