"""Tests for CLI helper functions."""

from euring import main as main_module


def test_emit_detail_skips_empty(capsys):
    main_module._emit_detail("Label", "")
    assert capsys.readouterr().out == ""


def test_emit_detail_outputs_value(capsys):
    main_module._emit_detail("Label", "Value")
    assert "Label: Value" in capsys.readouterr().out


def test_emit_detail_none_is_silent(capsys):
    main_module._emit_detail("Label", None)
    assert capsys.readouterr().out == ""


def test_emit_detail_bool_outputs_value(capsys):
    main_module._emit_detail_bool("Flag", True)
    assert "Flag: yes" in capsys.readouterr().out


def test_emit_detail_bool_none_is_silent(capsys):
    main_module._emit_detail_bool("Flag", None)
    assert capsys.readouterr().out == ""


def test_emit_glob_hint_for_existing_file(tmp_path, capsys):
    target = tmp_path / "file.txt"
    target.write_text("data", encoding="utf-8")
    main_module._emit_glob_hint(str(target))
    assert "Hint: your shell may have expanded a wildcard." in capsys.readouterr().err


def test_emit_glob_hint_ignores_patterns(capsys):
    main_module._emit_glob_hint("CH*")
    assert capsys.readouterr().err == ""


def test_with_meta_includes_generator():
    payload = main_module._with_meta({"type": "test"})
    assert payload["_meta"]["generator"]["name"] == "euring"


def test_has_errors_with_non_dict():
    assert main_module._has_errors(["error"])
    assert not main_module._has_errors([])


def test_format_error_lines_with_record_and_field_meta():
    errors = {
        "record": [{"message": "Record issue"}],
        "fields": [
            {
                "field": "Field Name",
                "message": "Field issue",
                "key": "field_key",
                "index": 1,
                "position": 2,
                "length": 3,
                "value": "X",
            }
        ],
    }
    lines = main_module._format_error_lines(errors, indent="  ")
    assert any("Record errors:" in line for line in lines)
    assert any("Field errors:" in line for line in lines)
    assert any("field_key" in line for line in lines)
