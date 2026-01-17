Examples
========

Building records
----------------

Use ``EuringRecord`` to assemble a valid EURING record from field values.

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

If you want to allow missing optional values and keep placeholders, pass
``strict=False`` to the record. ``serialize()`` raises ``ValueError`` when a field
fails validation.

Exporting records
-----------------

If you store ringing data in your own database, you can map your internal fields to EURING keys
and write each record as a line in a pipe-delimited file.

.. code-block:: python

   from euring import EuringRecord

   def export_records(records, path):
       record = EuringRecord("euring2000plus")
       errors = []
       with open(path, "w", encoding="utf-8", newline="\n") as handle:
           for row in records:
               record.update(
                   {
                       "ringing_scheme": row["ringing_scheme_code"],
                       "primary_identification_method": row["primary_id_method"],
                       "identification_number": row["ring_number"],
                       "place_code": row["place_code"],
                       "geographical_coordinates": row["coordinates_dms"],
                       "accuracy_of_coordinates": row["accuracy_code"],
                       "date": row["date_yyyymmdd"],
                   }
               )
               try:
                   handle.write(record.serialize() + "\n")
               except ValueError as exc:
                   errors.append((row["id"], str(exc)))
       return errors

This approach satisfies the technical submission notes from the EURING Manual:

- EURING data files must use UTF-8 or ASCII encoding; UTF-8 is preferred.
- EURING2000+ or EURING2020 formats are preferred for submission.
- One record per line; a single file containing all records is preferred.
