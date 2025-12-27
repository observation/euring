"""Tests for fetch helpers (mocked network)."""

import datetime

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
