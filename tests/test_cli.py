"""CLI smoke tests."""

from typer.testing import CliRunner

import euring.main as main_module
from euring import exceptions as euring_exceptions
from euring.coordinates import _lat_to_euring_coordinate, _lng_to_euring_coordinate
from euring.fields import EURING_KEY_INDEX
from euring.main import app
from tests.fixtures import (
    _make_euring2000plus_record_with_invalid_species,
    _make_euring2020_record,
)


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
        result = runner.invoke(app, ["lookup", "ringing_scheme", "example.txt"])
    assert result.exit_code == 1
    assert "Lookup error:" in result.output
    assert "Hint: your shell may have expanded a wildcard." in result.output


def test_decode_cli_success():
    runner = CliRunner()
    record = _load_fixture_records("euring2000plus_examples.py", "EURING2000PLUS_EXAMPLES")[0]
    result = runner.invoke(
        app,
        [
            "decode",
            record,
        ],
    )
    assert result.exit_code == 0
    assert "Decoded EURING record:" in result.output
    assert "Format: EURING2000+" in result.output
    assert "Ringing Scheme: ESA" in result.output


def test_decode_cli_format_mismatch_fails():
    runner = CliRunner()
    record = _make_euring2020_record()
    result = runner.invoke(app, ["decode", "--format", "euring2000", record])
    assert result.exit_code == 1
    combined_output = result.output + getattr(result, "stderr", "")
    expected_length_message = f'Format "euring2000" should be exactly 94 characters, found {len(record)}.'
    assert 'Format "euring2000" should not contain pipe characters ("|").' in combined_output
    assert expected_length_message in combined_output


def test_decode_cli_invalid_format():
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--format", "2000", "GBB"])
    assert result.exit_code == 1
    assert "Parse error" in result.output


def test_decode_cli_invalid_format_hint():
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--format", "2000", "GBB"])
    assert result.exit_code == 1
    assert 'Did you mean "euring2000"?' in result.output


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


def test_decode_cli_file_json(tmp_path):
    import json

    records = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")
    file_path = tmp_path / "euring2000_examples.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert len(payload["records"]) == len(records)


def _load_fixture_records(module_filename: str, list_name: str) -> list[str]:
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    fixture_path = Path(__file__).parent / "fixtures" / module_filename
    spec = spec_from_file_location(module_filename.replace(".py", ""), fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, list_name)


def test_validate_cli_success():
    record = _load_fixture_records("euring2000plus_examples.py", "EURING2000PLUS_EXAMPLES")[0]
    runner = CliRunner()
    result = runner.invoke(app, ["validate", record])
    assert result.exit_code == 0
    assert "Record is valid." in result.output


def test_validate_cli_errors():
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "not-a-record"])
    assert result.exit_code == 1
    assert "Record has errors:" in result.output


def test_validate_cli_json():
    import json

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--json", "not-a-record"])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["errors"]


def test_validate_cli_invalid_format_hint():
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--format", "2020", "GBB"])
    assert result.exit_code == 1
    assert 'Did you mean "euring2020"?' in result.output


def test_validate_cli_forced_euring2000_rejects_pipe_record():
    import json

    record = _make_euring2020_record()
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--json", "--format", "euring2000", record])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    messages = [error["message"] for error in payload["errors"]["record"]]
    expected_length_message = f'Format "euring2000" should be exactly 94 characters, found {len(record)}.'
    assert 'Format "euring2000" should not contain pipe characters ("|").' in messages
    assert expected_length_message in messages


def test_validate_cli_json_output_file(tmp_path):
    import json

    output_path = tmp_path / "validate.json"
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--json", "--output", str(output_path), "not-a-record"])
    assert result.exit_code == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["errors"]


def test_validate_cli_file_success(tmp_path):
    record = _load_fixture_records("euring2000plus_examples.py", "EURING2000PLUS_EXAMPLES")[0]
    file_path = tmp_path / "records.psv"
    file_path.write_text(record, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 0
    assert "All 1 records are valid." in result.output


def test_validate_cli_file_euring2000_examples(tmp_path):
    records = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")
    file_path = tmp_path / "euring2000_examples.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 0
    assert f"All {len(records)} records are valid." in result.output


def test_validate_cli_file_euring2000plus_examples(tmp_path):
    records = _load_fixture_records("euring2000plus_examples.py", "EURING2000PLUS_EXAMPLES")
    file_path = tmp_path / "euring2000plus_examples.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 0
    assert f"All {len(records)} records are valid." in result.output


def test_validate_cli_file_euring2020_examples(tmp_path):
    records = _load_fixture_records("euring2020_examples.py", "EURING2020_EXAMPLES")
    file_path = tmp_path / "euring2020_examples.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 0
    assert f"All {len(records)} records are valid." in result.output


def test_validate_cli_file_errors(tmp_path):
    file_path = tmp_path / "records.psv"
    file_path.write_text("not-a-record", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 1
    assert "records have errors" in result.output


def test_validate_cli_file_json(tmp_path):
    import json

    file_path = tmp_path / "records.psv"
    file_path.write_text("not-a-record", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path), "--json"])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["invalid"] == 1


def test_decode_cli_invalid_species_format_reports_errors():
    import json

    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--json", _make_euring2000plus_record_with_invalid_species()])
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert "errors" in payload
    fields = [error["field"] for error in payload["errors"]["fields"]]
    assert "Species Mentioned" in fields
    assert "Species Concluded" in fields


def test_lookup_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83", "--json", "--pretty"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("{")
    assert '"generator"' in result.output
    assert '"type": "place"' in result.output


def test_lookup_cli_ringing_scheme_json_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "ringing_scheme", "AAC", "--short", "--json"])
    assert result.exit_code == 0
    assert '"type": "ringing_scheme"' in result.output
    assert '"description"' in result.output


def test_lookup_cli_ringing_scheme_json_verbose():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "ringing_scheme", "AAC", "--json"])
    assert result.exit_code == 0
    assert '"type": "ringing_scheme"' in result.output
    assert '"ringing_centre"' in result.output


def test_lookup_cli_species_json_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "species", "00010", "--short", "--json"])
    assert result.exit_code == 0
    assert '"type": "species"' in result.output
    assert '"name"' in result.output


def test_lookup_cli_species_json_verbose():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "species", "00010", "--json"])
    assert result.exit_code == 0
    assert '"type": "species"' in result.output
    assert '"updated"' in result.output


def test_lookup_cli_place_json_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "AB00", "--short", "--json"])
    assert result.exit_code == 0
    assert '"type": "place"' in result.output
    assert '"name"' in result.output


def test_decode_cli_non_euring_string():
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "not-a-record"])
    assert result.exit_code == 1
    assert "Decoded EURING record:" in result.output
    assert "Record has errors:" in result.output


def test_decode_cli_parse_exception(monkeypatch):
    def _raise_parse(_cls, _value, **_kwargs):
        raise euring_exceptions.EuringException("bad")

    monkeypatch.setattr(main_module.EuringRecord, "decode", classmethod(_raise_parse))
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "GBB|A0"])
    assert result.exit_code == 1
    assert "Parse error: bad" in result.output


def test_decode_cli_unexpected_exception(monkeypatch):
    def _raise_error(_cls, _value, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(main_module.EuringRecord, "decode", classmethod(_raise_error))
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "GBB|A0"])
    assert result.exit_code == 1
    assert "Unexpected error: boom" in result.output


def test_lookup_cli_unknown_type():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "unknown", "ABC"])
    assert result.exit_code == 1
    assert "Unknown lookup type: unknown" in result.output


def test_lookup_cli_ringing_scheme_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "ringing_scheme", "AAC", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Ringing Scheme AAC: Canberra, Australia"


def test_lookup_cli_species_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "species", "00010", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Species 00010: Struthio camelus"


def test_lookup_cli_generic_table_short():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "age", "1", "--short"])
    assert result.exit_code == 0
    assert "age_mentioned 1: Pullus" in result.output


def test_fields_cli_lists_known_fields():
    runner = CliRunner()
    result = runner.invoke(app, ["fields"])
    assert result.exit_code == 0
    output = result.output
    assert "ringing_scheme\tRinging Scheme\t2000,2000+,2020" in output
    assert "\tDate\t" in output


def test_fields_cli_format_filter_limits_output():
    runner = CliRunner()
    result = runner.invoke(app, ["fields", "--format", "euring2000"])
    assert result.exit_code == 0
    output = result.output
    assert "latitude" not in output
    assert "ringing_scheme" in output


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


def test_dump_cli_unknown_table():
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "unknown"])
    assert result.exit_code == 1
    assert "Unknown code table" in result.output


def test_dump_cli_output_file(tmp_path):
    output_path = tmp_path / "dump.json"
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "sex", "--output", str(output_path)])
    assert result.exit_code == 0
    assert output_path.exists()
    assert '"_meta"' in output_path.read_text(encoding="utf-8")


def test_dump_cli_output_dir_single_table(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "sex", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    outputs = list(tmp_path.glob("code_table_sex.json"))
    assert outputs


def test_convert_cli_file_success(tmp_path):
    records = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")
    file_path = tmp_path / "euring2000_examples.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--file", str(file_path), "--to", "euring2000plus"])
    assert result.exit_code == 0
    lines = [line for line in result.output.splitlines() if line.strip()]
    assert len(lines) == len(records)
    assert all("|" in line for line in lines)


def test_convert_cli_file_output(tmp_path):
    records = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")
    file_path = tmp_path / "euring2000_examples.txt"
    output_path = tmp_path / "converted.txt"
    file_path.write_text("\n".join(records), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["convert", "--file", str(file_path), "--to", "euring2000plus", "--output", str(output_path)],
    )
    assert result.exit_code == 0
    assert result.output.strip() == ""
    output_lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(output_lines) == len(records)


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


def test_convert_cli_invalid_format():
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--to", "bad", "GBB"])
    assert result.exit_code == 1
    assert "Convert error" in result.output


def test_convert_cli_downgrade_with_coords():
    runner = CliRunner()
    lat = _lat_to_euring_coordinate(52.3760)
    lng = _lng_to_euring_coordinate(4.9000)
    euring2020_record_with_coordinates = _make_euring2020_record(
        geographical_coordinates="." * 15,
        accuracy_of_coordinates="A",
        latitude="52.3760",
        longitude="4.9000",
    )
    result = runner.invoke(
        app,
        [
            "convert",
            "--from",
            "euring2020",
            "--to",
            "euring2000plus",
            "--force",
            euring2020_record_with_coordinates,
        ],
    )
    assert result.exit_code == 0
    fields = result.output.strip().split("|")
    accuracy_of_coordinates = fields[EURING_KEY_INDEX["accuracy_of_coordinates"]]
    assert accuracy_of_coordinates == "0"  # Changed from 'A' to '0'
    geographical_coordinates = fields[EURING_KEY_INDEX["geographical_coordinates"]]
    assert geographical_coordinates == f"{lat}{lng}"  # Generated from latitude and longitude
