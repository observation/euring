Examples
========

Exporting records
-----------------

If you store ringing data in your own database, you can map your internal fields to EURING keys
and write each record as a line in a pipe-delimited file.

.. code-block:: python

   from euring import EuringRecordBuilder

   def export_records(records, path):
       builder = EuringRecordBuilder("euring2000plus")
       errors = []
       with open(path, "w", encoding="utf-8", newline="\n") as handle:
           for row in records:
               builder.update(
                   {
                       "ringing_scheme": row["scheme_code"],
                       "primary_identification_method": row["primary_id_method"],
                       "identification_number": row["ring_number"],
                       "place_code": row["place_code"],
                       "geographical_coordinates": row["coordinates_dms"],
                       "accuracy_of_coordinates": row["accuracy_code"],
                       "date": row["date_yyyymmdd"],
                   }
               )
               try:
                   handle.write(builder.build() + "\n")
               except ValueError as exc:
                   errors.append((row["id"], str(exc)))
       return errors

This approach satisfies the technical submission notes from the EURING Manual:

- EURING data files must use UTF-8 or ASCII encoding; UTF-8 is preferred.
- EURING2000+ or EURING2020 formats are preferred for submission.
- One record per line; a single file containing all records is preferred.
