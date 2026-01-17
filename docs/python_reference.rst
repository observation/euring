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

   from euring import EuringRecord

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

``serialize()`` raises ``ValueError`` if required fields are missing or a value
fails validation. Use ``EuringRecord("euring2000plus", strict=False)``
to allow missing optional values and keep placeholders in the output. Use
``export()`` to convert to other EURING string formats.
