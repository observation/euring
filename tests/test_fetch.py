"""Tests for fetch helpers (mocked network)."""

import datetime
import json

import pytest
import requests

from euring.data import fetch as fetch_module


class _FakeResponse:
    def __init__(self, content: bytes, *, raise_for_status=None):
        self.content = content
        self._raise_for_status = raise_for_status

    def raise_for_status(self):
        if self._raise_for_status:
            raise self._raise_for_status


def test_fetch_timeout(monkeypatch):
    def _raise_timeout(*_args, **_kwargs):
        raise requests.exceptions.Timeout("timeout")

    monkeypatch.setattr(requests, "get", _raise_timeout)
    with pytest.raises(requests.exceptions.Timeout):
        fetch_module._fetch("https://example.invalid", fetch_module.SCHEME_FIELDS)


def test_fetch_http_error(monkeypatch):
    error = requests.HTTPError("404")

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(b"", raise_for_status=error)

    monkeypatch.setattr(requests, "get", _fake_get)
    with pytest.raises(requests.HTTPError):
        fetch_module._fetch_places_csv("https://example.invalid")


def test_field_value_bool_and_string():
    cell = type("Cell", (), {"find": lambda *_args, **_kwargs: object(), "string": " Test "})()
    assert fetch_module._field_value(cell, "bool") is True
    assert fetch_module._field_value(cell, "string") == "Test"


def test_field_value_date_dot_format():
    cell = type("Cell", (), {"find": lambda *_args, **_kwargs: None, "string": "01.02.2024"})()
    assert fetch_module._field_value(cell, "date") == datetime.date(2024, 2, 1)


def test_field_value_invalid_type():
    cell = type("Cell", (), {"find": lambda *_args, **_kwargs: None, "string": "01/02/24"})()
    with pytest.raises(ValueError):
        fetch_module._field_value(cell, "bogus")


def test_fetch_unexpected_structure(monkeypatch):
    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(b"<html></html>")

    monkeypatch.setattr(requests, "get", _fake_get)
    with pytest.raises(AttributeError):
        fetch_module._fetch("https://example.invalid", fetch_module.SCHEME_FIELDS)


def test_fetch_parses_html_table(monkeypatch):
    html = b"""
    <div id="divAll">
      <table>
        <tr><th>header</th></tr>
        <tr>
          <td>AAA</td>
          <td>Testland</td>
          <td>Center</td>
          <td><img alt="Y"></td>
          <td></td>
          <td>01/02/03</td>
          <td>Notes</td>
        </tr>
      </table>
    </div>
    """

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(html)

    monkeypatch.setattr(requests, "get", _fake_get)
    result = fetch_module._fetch("https://example.invalid", fetch_module.SCHEME_FIELDS)
    assert result == [
        {
            "code": "AAA",
            "country": "Testland",
            "ringing_centre": "Center",
            "is_euring": True,
            "is_current": False,
            "updated": datetime.date(2003, 2, 1),
            "notes": "Notes",
        }
    ]


def test_fetch_species_csv(monkeypatch):
    csv_bytes = b"EURING_Code,Current_Name,Date_Updated,Notes\n00010,Ostrich,01.01.2020,ok\n"

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(csv_bytes)

    monkeypatch.setattr(requests, "get", _fake_get)
    result = fetch_module._fetch_species_csv("https://example.invalid")
    assert result == [
        {
            "code": "00010",
            "name": "Ostrich",
            "updated": datetime.date(2020, 1, 1),
            "notes": "ok",
        }
    ]


def test_fetch_species_csv_invalid_date(monkeypatch):
    csv_bytes = b"EURING_Code,Current_Name,Date_Updated,Notes\n00010,Ostrich,2020-01-01,ok\n"

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(csv_bytes)

    monkeypatch.setattr(requests, "get", _fake_get)
    with pytest.raises(ValueError):
        fetch_module._fetch_species_csv("https://example.invalid")


def test_fetch_places_csv(monkeypatch):
    csv_bytes = b"Country|Region|PlaceCode|Current|Notes|Updated\nGreece|Makedonia|GR83|Y|Note|01/01/20\n"

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(csv_bytes)

    monkeypatch.setattr(requests, "get", _fake_get)
    result = fetch_module._fetch_places_csv("https://example.invalid")
    assert result == [
        {
            "code": "Greece",
            "region": "Makedonia",
            "place_code": "GR83",
            "is_current": True,
            "notes": "Note",
            "updated": datetime.date(2020, 1, 1),
        }
    ]


def test_fetch_places_csv_invalid_date(monkeypatch):
    csv_bytes = b"Country|Region|PlaceCode|Current|Notes|Updated\nGreece|Makedonia|GR83|Y|Note|2020-01-01\n"

    def _fake_get(*_args, **_kwargs):
        return _FakeResponse(csv_bytes)

    monkeypatch.setattr(requests, "get", _fake_get)
    with pytest.raises(ValueError):
        fetch_module._fetch_places_csv("https://example.invalid")


def test_fetch_all_uses_fetchers(monkeypatch):
    def _fake_fetch(_url, _fields):
        return [{"code": "X"}]

    def _fake_species(_url):
        return [{"code": "Y"}]

    def _fake_places(_url):
        return [{"code": "Z"}]

    monkeypatch.setattr(fetch_module, "_fetch", _fake_fetch)
    monkeypatch.setattr(fetch_module, "_fetch_species_csv", _fake_species)
    monkeypatch.setattr(fetch_module, "_fetch_places_csv", _fake_places)
    data = fetch_module.fetch_all()
    assert data["schemes.json"] == [{"code": "X"}]
    assert data["circumstances.json"] == [{"code": "X"}]
    assert data["species.json"] == [{"code": "Y"}]
    assert data["places.json"] == [{"code": "Z"}]


def test_write_json_files(tmp_path):
    datasets = {"sample.json": [{"updated": datetime.date(2020, 1, 1)}]}
    fetch_module.write_json_files(str(tmp_path), datasets)
    data = json.loads((tmp_path / "sample.json").read_text())
    assert data == [{"updated": "2020-01-01"}]


def test_json_formatter_invalid_type():
    with pytest.raises(TypeError):
        fetch_module._json_formatter(object())
