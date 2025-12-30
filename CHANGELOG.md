# Changelog

## 25.2 (2025-12-30)

- CLI lookup shows verbose details by default and supports `--short` for concise output (#9).
- Add EURING2020 support and fixtures (#21).
- Add EURING format conversion utilities and CLI (#22).
- Add `_meta` to JSON outputs for decode/lookup/dump (#19, #23).
- Add NumericSigned and coordinate validation for EURING2020 lat/long fields (#26, #27, #30).
- Add cross-field validation for EURING2020 coordinates (#27, #30).
- Update manual-backed code tables to match EURING Code 2020 v202 (#29, #32).
- Standardize EURING field name capitalization per manual (#30).
- Add Python Reference docs and update CLI docs (#25, #28).
- Move Condition and EURING Code Identifier into data code tables (#29).
- Add EURING record builder helper for creating records in code (#33).
- Add `dump --all` to export all code tables to a directory (#41).
- Add `validate --file` support for validating record files (#43).

## 25.1 (2025-12-27)

- First release for developer audience.
