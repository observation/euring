"""Tests for CLI error branches and outputs."""

from pathlib import Path

from typer.testing import CliRunner

from euring.main import app


def _load_fixture_records(module_filename: str, list_name: str) -> list[str]:
    from importlib.util import module_from_spec, spec_from_file_location

    fixture_path = Path(__file__).parent / "fixtures" / module_filename
    spec = spec_from_file_location(module_filename.replace(".py", ""), fixture_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, list_name)


def test_decode_cli_pretty_without_json_fails():
    runner = CliRunner()
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    result = runner.invoke(app, ["decode", "--pretty", record])
    assert result.exit_code == 1
    assert "Use --pretty with --json." in result.output


def test_decode_cli_file_without_json_fails(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path)])
    assert result.exit_code == 1
    assert "Use --json when decoding files." in result.output


def test_decode_cli_file_missing(tmp_path):
    file_path = tmp_path / "missing.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), "--json"])
    assert result.exit_code == 1
    assert f"File not found: {file_path}" in result.output


def test_decode_cli_file_and_record_conflict(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), record])
    assert result.exit_code == 1
    assert "Use either a record or --file" in result.output


def test_decode_cli_file_output_success(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    output_path = tmp_path / "out.json"
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), "--json", "--output", str(output_path)])
    assert result.exit_code == 0
    assert output_path.exists()


def test_decode_cli_file_output_errors(tmp_path):
    file_path = tmp_path / "records.txt"
    file_path.write_text("not-a-record", encoding="utf-8")
    output_path = tmp_path / "out.json"
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), "--json", "--output", str(output_path)])
    assert result.exit_code == 1
    assert output_path.exists()


def test_decode_cli_file_json_errors_no_output(tmp_path):
    file_path = tmp_path / "records.txt"
    file_path.write_text("not-a-record", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--file", str(file_path), "--json"])
    assert result.exit_code == 1


def test_decode_cli_json_output_file_errors(tmp_path):
    output_path = tmp_path / "out.json"
    runner = CliRunner()
    result = runner.invoke(app, ["decode", "--json", "--output", str(output_path), "not-a-record"])
    assert result.exit_code == 1
    assert output_path.exists()


def test_decode_cli_no_input_fails():
    runner = CliRunner()
    result = runner.invoke(app, ["decode"])
    assert result.exit_code == 1
    assert "Provide a record or use --file." in result.output


def test_validate_cli_pretty_without_json_fails():
    runner = CliRunner()
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    result = runner.invoke(app, ["validate", "--pretty", record])
    assert result.exit_code == 1
    assert "Use --pretty with --json." in result.output


def test_validate_cli_file_and_record_conflict(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path), record])
    assert result.exit_code == 1
    assert "Use either a record or --file" in result.output


def test_validate_cli_file_missing(tmp_path):
    file_path = tmp_path / "missing.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path)])
    assert result.exit_code == 1
    assert f"File not found: {file_path}" in result.output


def test_validate_cli_no_input_fails():
    runner = CliRunner()
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 1
    assert "Provide a record or use --file." in result.output


def test_validate_cli_file_json_output(tmp_path):
    file_path = tmp_path / "records.txt"
    file_path.write_text("not-a-record", encoding="utf-8")
    output_path = tmp_path / "validate.json"
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path), "--json", "--output", str(output_path)])
    assert result.exit_code == 1
    assert output_path.exists()


def test_validate_cli_file_output_success(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    output_path = tmp_path / "validate.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "--file", str(file_path), "--output", str(output_path)])
    assert result.exit_code == 0
    assert output_path.exists()


def test_convert_cli_no_input_fails():
    runner = CliRunner()
    result = runner.invoke(app, ["convert"])
    assert result.exit_code == 1
    assert "Provide a record or use --file." in result.output


def test_convert_cli_file_errors(tmp_path):
    file_path = tmp_path / "records.txt"
    file_path.write_text("bad-record", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--file", str(file_path)])
    assert result.exit_code == 1
    assert "Conversion errors:" in result.output


def test_convert_cli_file_missing(tmp_path):
    file_path = tmp_path / "missing.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--file", str(file_path)])
    assert result.exit_code == 1
    assert f"File not found: {file_path}" in result.output


def test_convert_cli_file_and_record_conflict(tmp_path):
    record = _load_fixture_records("euring2000_examples.py", "EURING2000_EXAMPLES")[0]
    file_path = tmp_path / "records.txt"
    file_path.write_text(record, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["convert", "--file", str(file_path), record])
    assert result.exit_code == 1
    assert "Use either a record or --file" in result.output


def test_dump_cli_all_requires_output_dir():
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "--all"])
    assert result.exit_code == 1
    assert "--output-dir is required" in result.output


def test_dump_cli_all_with_table_fails(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "age", "--all", "--output-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "Do not specify table names" in result.output


def test_dump_cli_no_table_fails():
    runner = CliRunner()
    result = runner.invoke(app, ["dump"])
    assert result.exit_code == 1
    assert "Specify one or more code tables" in result.output


def test_dump_cli_output_dir_file_exists(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    output_path = output_dir / "code_table_age.json"
    output_path.write_text("{}", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "age", "--output-dir", str(output_dir)])
    assert result.exit_code == 1
    assert "File exists" in result.output


def test_lookup_cli_pretty_without_json():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "species", "00010", "--pretty"])
    assert result.exit_code == 1
    assert "Use --pretty with --json." in result.output
