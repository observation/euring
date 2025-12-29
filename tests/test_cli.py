"""CLI smoke tests."""

from typer.testing import CliRunner

import euring.main as main_module
from euring import exceptions as euring_exceptions
from euring.main import app


def test_lookup_place_verbose_includes_details():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83"])
    assert result.exit_code == 0
    assert "Place GR83" in result.output
    assert "Name: Greece" in result.output
    assert "Region: Makedonia" in result.output
    assert (
        "Notes: Corresponds to the new divisions of Dytiki Makedonia, "
        "Kentriki Makedonia and Anatoliki Makedonia kai Thraki, west of the River Nestos." in result.output
    )


def test_lookup_place_short_is_concise():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Place GR83: Greece (Makedonia)"


def test_lookup_glob_hint_when_shell_expands_to_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("example.txt", "w", encoding="utf-8") as handle:
            handle.write("data")
        result = runner.invoke(app, ["lookup", "scheme", "example.txt"])
    assert result.exit_code == 1
    assert "Lookup error:" in result.output
    assert "Hint: your shell may have expanded a wildcard." in result.output


def test_decode_cli_success():
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "decode",
            "GBB|A0|1234567890|0|1|ZZ|00010|00010|N|0|M|U|U|U|2|2|U|01012024|0|0000|AB00|+0000000+0000000|1|9|99|0|4",
        ],
    )
    assert result.exit_code == 0
    assert "Decoded EURING record:" in result.output
    assert "Format: EURING2000+" in result.output
    assert "Scheme: GBB" in result.output


def test_decode_cli_non_euring_string():
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "not-a-record"])
    assert result.exit_code == 0
    assert "Decoded EURING record:" in result.output


def test_validate_cli_success():
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "ABC", "alphabetic"])
    assert result.exit_code == 0
    assert "is valid alphabetic" in result.output


def test_validate_cli_invalid_type():
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "ABC", "integer"])
    assert result.exit_code == 1
    assert "is not valid integer" in result.output


def test_validate_cli_unknown_type():
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "ABC", "bogus"])
    assert result.exit_code == 1
    assert "Unknown field type: bogus" in result.output


def test_decode_cli_parse_exception(monkeypatch):
    def _raise_parse(_value):
        raise euring_exceptions.EuringParseException("bad")

    monkeypatch.setattr(main_module, "euring_decode_record", _raise_parse)
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "GBB|A0"])
    assert result.exit_code == 1
    assert "Parse error: bad" in result.output


def test_decode_cli_unexpected_exception(monkeypatch):
    def _raise_error(_value):
        raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "euring_decode_record", _raise_error)
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "GBB|A0"])
    assert result.exit_code == 1
    assert "Unexpected error: boom" in result.output


def test_lookup_cli_unknown_type():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "unknown", "ABC"])
    assert result.exit_code == 1
    assert "Unknown lookup type: unknown" in result.output


def test_lookup_cli_scheme_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "scheme", "AAC", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Scheme AAC: Canberra, Australia"


def test_lookup_cli_species_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "species", "00010", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Species 00010: Struthio camelus"
