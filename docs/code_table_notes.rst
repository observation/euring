EURING Code Tables: Assumptions and Adjustments
===============================================

All EURING code tables are transcribed into Python modules under
``src/euring/data/code_table_*.py``. This document records the sources used and
the practical adjustments and assumptions applied during transcription. It is
intended to make our interpretation explicit when formal sources are ambiguous,
inconsistent, or contain errors.

Scope
-----

These notes cover:

- Source material used for each table (manual or external files).
- Adjustments and assumptions applied when source data is unclear.
- Known constraints that affect how code-table values are handled.

Sources
-------

The sources are:

- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. Helsinki, Finland ISBN 978-952-94-4399-4;
- EURING – The European Union for Bird Ringing (2020). The EURING Exchange Code 2020. On-line Code Tables. Thetford, U.K. URL https://www.euring.org/data-and-codes/euring-codes;
- the specific file or resources as specified per table, if any.

General notes
-------------

- Some manual descriptions include cue text such as "one hyphen" or "two
  hyphens" to explain the literal symbol in the code field. We treat these as
  reader hints and omit them from the stored descriptions; the code value itself
  carries that meaning.

Place codes
-----------

Source: https://www.euring.org/files/documents/ECPlacePipeDelimited_0.csv

- Source file contains additional pipe characters within Region/Notes fields.
  We detect the Place Code column by looking for a 4-character code followed by
  a Current flag (Y/N), then treat everything between that and the date as
  Notes. Embedded pipes in notes are normalized to ", " for display.
- Source file is not consistently UTF-8; the official source needs a latin-1
  compatible decode to preserve characters as provided.
- Place codes are normalized by trimming whitespace; leading-space codes present
  in the raw source are treated as data errors and corrected by the fixed file.
- Manual fixes applied to the local source file to replace literal "?" glyphs
  that appear as encoding artifacts in place names (for example, Kärnten).

Species codes
-------------

Source: https://www.euring.org/files/documents/EURING_SpeciesCodes_IOC15_1.csv

- Trailing whitespace in Notes is trimmed to avoid false differences.
- Empty Date_Updated values are stored as `None`.
- The official source is UTF-8 and does not contain pipe characters in Notes.
- Two notes in the official species source use " ? " (codes 12681, 12682). We
  interpret this as an encoding artifact and store an en dash: " – ".

Ringing schemes
---------------

Source: http://blx1.bto.org/euringcodes/ via https://www.euring.org/data-and-codes

- Source is a pipe-delimited table; extra pipe-delimited columns appear after
  the Notes field in the official source. Notes are normalized to ", " for
  display when pipes are present.
- Scheme codes are trimmed of surrounding whitespace to avoid leading-space
  identifiers present in the raw file.
- The official source requires a latin-1 compatible decode to preserve
  characters as provided.
- Dates are normalized from ``DD/MM/YY`` to ``YYYY-MM-DD``.

Circumstances
-------------

Source: http://blx1.bto.org/euringcodes/ via https://www.euring.org/data-and-codes

- Source file is pipe-delimited and contains extra pipes in Description fields.
  Descriptions are normalized to replace embedded pipes with ", " for display.
- Soft hyphen characters in descriptions are removed to avoid reintroducing
  line-break artifacts from the source file.
- The official source requires a latin-1 compatible decode to preserve
  characters as provided.
- Dates are normalized from ``DD/MM/YY`` to ``YYYY-MM-DD``.

Age codes
---------

- The manual provides extended explanatory text for code ``1``; we store the
  shorter description without the multi-line wildfowl/waders note to keep code
  table entries concise.
- The manual lists letter codes ``C`` onwards as "et seq."; we expand ``C``–``Z``
  to explicit year descriptions for completeness.

Condition
---------

- Condition descriptions are shortened for brevity. The manual includes
  extra clauses about identifying rings/marks without capture and guidance
  about using Accuracy of Date for long-dead birds.

Generated sequences
-------------------

- Brood Size codes are generated to cover the full implied ranges (00–50 for a
  single female, 51–99 for more than one female) based on the manual examples.
- Pullus Age codes are generated to cover the implied day range (00–98) in
  addition to the explicit ``--`` and ``99`` codes.

Measurement method tables
-------------------------

- Tarsus Method descriptions are shortened; the manual includes extra
  detail about measurement technique and references to the BTO Ringers'
  Manual and Svensson (1992).

Sexing Method
-------------

- Sexing Method descriptions are shortened; the manual includes additional
  explanatory clauses (for example "including song" for Activity and the
  longer explanation for Size or brightness).

Manual cue-letter capitalization
--------------------------------

- Some manual descriptions use mid-word capitalization to hint the code letter
  (for example, "cLap net", "caVity", "MoulTing"). We normalize these to
  standard capitalization for readability.
