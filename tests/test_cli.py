"""CLI smoke tests."""

from typer.testing import CliRunner

import euring.main as main_module
from euring import exceptions as euring_exceptions
from euring.fields import EURING_FIELDS
from euring.main import app
from euring.utils import euring_lat_to_dms, euring_lng_to_dms


def _make_euring2020_record_with_coords() -> str:
    values = [""] * len(EURING_FIELDS)

    def set_value(key: str, value: str) -> None:
        for index, field in enumerate(EURING_FIELDS):
            if field["key"] == key:
                values[index] = value
                return
        raise ValueError(f"Unknown key: {key}")

    set_value("ringing_scheme", "GBB")
    set_value("primary_identification_method", "A0")
    set_value("identification_number", "1234567890")
    set_value("place_code", "AB00")
    set_value("accuracy_of_coordinates", "A")
    set_value("latitude", "52.3760")
    set_value("longitude", "4.9000")
    return "|".join(values)


def _make_euring2000_plus_record_with_invalid_species() -> str:
    values = [
        "GBB",
        "A0",
        "1234567890",
        "0",
        "1",
        "ZZ",
        "12ABC",
        "12ABC",
        "N",
        "0",
        "M",
        "U",
        "U",
        "U",
        "2",
        "2",
        "U",
        "99",
        "99",
        "0",
        "01012024",
        "0",
        "0000",
        "AB00",
        "+0000000+0000000",
        "1",
        "9",
        "99",
        "0",
        "4",
        "00000",
        "000",
        "00000",
    ]
    return "|".join(values)


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


def test_decode_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "decode",
            "--json",
            "--pretty",
            "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip().startswith("{")
    assert '"generator"' in result.output
    assert '"format": "EURING2000"' in result.output


def test_decode_cli_invalid_species_format_reports_errors():
    import json

    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--json", _make_euring2000_plus_record_with_invalid_species()])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "errors" in payload
    assert "Species Mentioned" in payload["errors"]
    assert "Species Concluded" in payload["errors"]


def test_lookup_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83", "--json", "--pretty"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("{")
    assert '"generator"' in result.output
    assert '"type": "place"' in result.output


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
    def _raise_parse(_value, **_kwargs):
        raise euring_exceptions.EuringParseException("bad")

    monkeypatch.setattr(main_module, "euring_decode_record", _raise_parse)
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "GBB|A0"])
    assert result.exit_code == 1
    assert "Parse error: bad" in result.output


def test_decode_cli_unexpected_exception(monkeypatch):
    def _raise_error(_value, **_kwargs):
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


def test_dump_cli_single_table(monkeypatch):
    def _fake_load_data(name):
        if name == "age":
            return [{"code": 0, "description": "Unknown"}]
        return None

    monkeypatch.setattr(main_module, "load_data", _fake_load_data)
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "age"])
    assert result.exit_code == 0
    assert '"_meta"' in result.output
    assert '"data"' in result.output


def test_dump_cli_multiple_tables(monkeypatch):
    def _fake_load_data(name):
        if name == "age":
            return [{"code": 0}]
        if name == "sex":
            return [{"code": "M"}]
        return None

    monkeypatch.setattr(main_module, "load_data", _fake_load_data)
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "age", "sex"])
    assert result.exit_code == 0
    payload = result.output.strip()
    assert '"_meta"' in payload
    assert '"data"' in payload
    assert '"age"' in payload
    assert '"sex"' in payload


def test_convert_cli_success():
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "convert",
            "DERA0CD...5206501ZZ1877018770N0ZUFF22U-----081019710----DECK+502400+00742000820030000000000000",
        ],
    )
    assert result.exit_code == 0
    assert result.output.count("|") > 10


def test_convert_cli_downgrade_with_coords():
    runner = CliRunner()
    lat = euring_lat_to_dms(52.3760)
    lng = euring_lng_to_dms(4.9000)
    result = runner.invoke(
        app,
        [
            "convert",
            "--from",
            "EURING2020",
            "--to",
            "EURING2000PLUS",
            "--force",
            _make_euring2020_record_with_coords(),
        ],
    )
    assert result.exit_code == 0
    fields = result.output.strip().split("|")
    geo_index = next(i for i, f in enumerate(EURING_FIELDS) if f["key"] == "geographical_coordinates")
    assert fields[geo_index] == f"{lat}{lng}"
