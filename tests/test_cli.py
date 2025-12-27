"""CLI smoke tests."""

from typer.testing import CliRunner

from euring.main import app


def test_lookup_place_verbose_includes_details():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83"])
    assert result.exit_code == 0
    assert "Place GR83" in result.output
    assert "Name: Greece" in result.output
    assert "Region: Makedonia" in result.output
    assert "Notes: Corresponds to the new divisions of Dytiki Makedonia?" in result.output


def test_lookup_place_short_is_concise():
    runner = CliRunner()
    result = runner.invoke(app, ["lookup", "place", "GR83", "--short"])
    assert result.exit_code == 0
    assert result.output.strip() == "Place GR83: Greece (Makedonia)"
