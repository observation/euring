"""Tests for CLI helper functions."""

from euring import main as main_module


def test_emit_detail_skips_empty(capsys):
    main_module._emit_detail("Label", "")
    assert capsys.readouterr().out == ""


def test_emit_detail_outputs_value(capsys):
    main_module._emit_detail("Label", "Value")
    assert "Label: Value" in capsys.readouterr().out


def test_emit_detail_bool_outputs_value(capsys):
    main_module._emit_detail_bool("Flag", True)
    assert "Flag: yes" in capsys.readouterr().out


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
