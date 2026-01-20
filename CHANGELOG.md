# Changelog

## 26.4 (2026-01-20)

- Data: Update EURING Code Tables and document transcription to Python (#85, #86).

## 26.3 (2026-01-19)

- Breaking: Remove `euring_decode_record` and fold decoding into EuringRecord (#76, #81).
- CLI: Add error on file not found (#82).

## 26.2 (2026-01-12)

- Refactor JSON structure and errors structure (#70).
- Make EURING format options explicit (#68, #69).
- Add tests for EURING formats (#67).
- Add documentation for EuringRecordBuilder (#63).

## 26.1 (2026-01-02)

- Use singular naming for place code table (#60).

## 25.3 (2025-12-31)

- Align field names with the EURING manual (#46).
- Add `convert --file` support for converting record files (#47).
- Refactor CLI and add JSON output (#48).
- Add missing code tables (#51).
- Add GitHub release workflow and smoke test coverage (#53).

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
