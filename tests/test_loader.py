"""Tests for data loader helpers."""

from euring.data import loader as loader_module


def test_normalize_code_variants():
    assert loader_module.normalize_code(None) is None
    assert loader_module.normalize_code(True) == "1"
    assert loader_module.normalize_code(False) == "0"
    assert loader_module.normalize_code(5) == "5"
    assert loader_module.normalize_code(5.7) == "5"
    assert loader_module.normalize_code("  ABC ") == "ABC"
    assert loader_module.normalize_code("—") == "--"
    assert loader_module.normalize_code("–") == "--"


def test_load_json_missing_file():
    assert loader_module.load_json("does_not_exist") is None


def test_load_code_map_filters_and_defaults():
    def _fake_load_json(_name):
        return [
            {"code": "A", "description": "Alpha"},
            {"code": "B", "description": "Beta"},
            {"code": None, "description": "Skip"},
            {"code": "C", "description": None},
        ]

    original = loader_module.load_json
    loader_module.load_json = _fake_load_json
    try:
        result = loader_module.load_code_map("ignored", code_filter=lambda code: code != "B")
    finally:
        loader_module.load_json = original
    assert result == {"A": "Alpha"}


def test_load_code_map_empty_data():
    def _fake_load_json(_name):
        return []

    original = loader_module.load_json
    loader_module.load_json = _fake_load_json
    try:
        assert loader_module.load_code_map("ignored") == {}
    finally:
        loader_module.load_json = original


def test_load_table_non_list():
    def _fake_load_json(_name):
        return {"code": "A"}

    original = loader_module.load_json
    loader_module.load_json = _fake_load_json
    try:
        assert loader_module.load_table("ignored") is None
    finally:
        loader_module.load_json = original


def test_load_place_map_fallback():
    def _fake_load_table(_name):
        return None

    def _fake_load_json(_name):
        return [
            {"place_code": "AA00", "code": "Test", "region": "Region"},
            {"place_code": "BB00", "code": "Test", "region": "not specified"},
        ]

    original_table = loader_module.load_table
    original_json = loader_module.load_json
    loader_module.load_table = _fake_load_table
    loader_module.load_json = _fake_load_json
    try:
        result = loader_module.load_place_map()
    finally:
        loader_module.load_table = original_table
        loader_module.load_json = original_json
    assert result["AA00"] == "Test (Region)"
    assert result["BB00"] == "Test"


def test_load_place_details_normalizes_key():
    def _fake_load_table(_name):
        return [{"place_code": "  AA00 ", "code": "Name"}]

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        result = loader_module.load_place_details()
    finally:
        loader_module.load_table = original
    assert "AA00" in result
    assert result["AA00"]["place_code"] == "AA00"


def test_load_scheme_map_formats_label():
    def _fake_load_json(_name):
        return [
            {"code": "AAA", "country": "Country", "ringing_centre": "Centre"},
            {"code": "BBB", "country": "", "ringing_centre": "Centre"},
        ]

    original = loader_module.load_json
    loader_module.load_json = _fake_load_json
    try:
        result = loader_module.load_scheme_map()
    finally:
        loader_module.load_json = original
    assert result["AAA"] == "Centre, Country"
    assert result["BBB"] == "Centre"


def test_load_named_code_map_uses_description():
    def _fake_load_json(_name):
        return [{"code": "1", "description": "One"}]

    original = loader_module.load_json
    loader_module.load_json = _fake_load_json
    try:
        assert loader_module.load_named_code_map("ignored") == {"1": "One"}
    finally:
        loader_module.load_json = original


def test_load_place_details_fallback_to_json():
    def _fake_load_table(_name):
        return None

    def _fake_load_json(_name):
        return [{"place_code": "CC00", "code": "Name"}]

    original_table = loader_module.load_table
    original_json = loader_module.load_json
    loader_module.load_table = _fake_load_table
    loader_module.load_json = _fake_load_json
    try:
        result = loader_module.load_place_details()
    finally:
        loader_module.load_table = original_table
        loader_module.load_json = original_json
    assert "CC00" in result
