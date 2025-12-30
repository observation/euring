"""Tests for dump --all."""

from typer.testing import CliRunner

from euring.main import app


def test_dump_all_writes_files(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["dump", "--all", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    outputs = list(tmp_path.glob("code_table_*.json"))
    assert outputs


def test_dump_all_refuses_overwrite(tmp_path):
    runner = CliRunner()
    first = runner.invoke(app, ["dump", "--all", "--output-dir", str(tmp_path)])
    assert first.exit_code == 0
    second = runner.invoke(app, ["dump", "--all", "--output-dir", str(tmp_path)])
    assert second.exit_code == 1
    assert "use --force to overwrite" in second.output
