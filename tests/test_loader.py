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


def test_load_data_missing_table():
    assert loader_module.load_data("does_not_exist") is None


def test_load_code_map_filters_and_defaults():
    def _fake_load_data(_name):
        return [
            {"code": "A", "description": "Alpha"},
            {"code": "B", "description": "Beta"},
            {"code": None, "description": "Skip"},
            {"code": "C", "description": None},
        ]

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        result = loader_module.load_code_map("ignored", code_filter=lambda code: code != "B")
    finally:
        loader_module.load_data = original
    assert result == {"A": "Alpha"}


def test_load_code_map_empty_data():
    def _fake_load_data(_name):
        return []

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        assert loader_module.load_code_map("ignored") == {}
    finally:
        loader_module.load_data = original


def test_load_table_non_list():
    def _fake_load_data(_name):
        return {"code": "A"}

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        assert loader_module.load_table("ignored") is None
    finally:
        loader_module.load_data = original


def test_load_place_map_formats_label():
    def _fake_load_table(_name):
        return [
            {"place_code": "AA00", "country": "Test", "region": "Region"},
            {"place_code": "BB00", "country": "Test", "region": ""},
        ]

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        result = loader_module.load_place_map()
    finally:
        loader_module.load_table = original
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


def test_load_place_details_empty():
    def _fake_load_table(_name):
        return None

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        assert loader_module.load_place_details() == {}
    finally:
        loader_module.load_table = original


def test_load_scheme_map_formats_label():
    def _fake_load_table(_name):
        return [
            {"code": "AAA", "country": "Country", "ringing_centre": "Centre"},
            {"code": "BBB", "country": "", "ringing_centre": "Centre"},
        ]

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        result = loader_module.load_scheme_map()
    finally:
        loader_module.load_table = original
    assert result["AAA"] == "Centre, Country"
    assert result["BBB"] == "Centre"


def test_load_named_code_map_uses_description():
    def _fake_load_data(_name):
        return [{"code": "1", "description": "One"}]

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        assert loader_module.load_named_code_map("ignored") == {"1": "One"}
    finally:
        loader_module.load_data = original


def test_load_table_known_and_unknown():
    assert loader_module.load_table("sex")
    assert loader_module.load_table("does_not_exist") is None


def test_code_tables_registry_includes_manual_tables():
    from euring.data.code_tables import EURING_CODE_TABLES

    assert "condition" in EURING_CODE_TABLES
    assert "euring_code_identifier" in EURING_CODE_TABLES


def test_load_other_marks_data_missing():
    def _fake_load_data(_name):
        return None

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        assert loader_module.load_other_marks_data() is None
    finally:
        loader_module.load_data = original


def test_load_named_code_map_skips_missing_values():
    def _fake_load_data(_name):
        return [{"code": None, "description": "Skip"}, {"code": "1", "description": None}]

    original = loader_module.load_data
    loader_module.load_data = _fake_load_data
    try:
        assert loader_module.load_named_code_map("ignored") == {}
    finally:
        loader_module.load_data = original


def test_load_place_map_no_data():
    def _fake_load_table(_name):
        return None

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        assert loader_module.load_place_map() == {}
    finally:
        loader_module.load_table = original


def test_load_species_details_skips_missing_code():
    def _fake_load_table(_name):
        return [{"code": None}, {"code": "00010", "name": "Ok"}]

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        result = loader_module.load_species_details()
    finally:
        loader_module.load_table = original
    assert result == {"00010": {"code": "00010", "name": "Ok"}}


def test_load_scheme_details_skips_missing_code():
    def _fake_load_table(_name):
        return [{"code": None}, {"code": "AAA", "country": "X"}]

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        result = loader_module.load_scheme_details()
    finally:
        loader_module.load_table = original
    assert result == {"AAA": {"code": "AAA", "country": "X"}}


def test_load_scheme_map_no_data():
    def _fake_load_table(_name):
        return None

    original = loader_module.load_table
    loader_module.load_table = _fake_load_table
    try:
        assert loader_module.load_scheme_map() == {}
    finally:
        loader_module.load_table = original
