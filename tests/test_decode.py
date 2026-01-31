from euring.decode import (
    euring_detect_format,
    euring_record_to_dict,
)
from euring.fields import (
    EURING2000_FIELDS,
    EURING2000_KEYS,
    EURING2000PLUS_FIELDS,
    EURING2000PLUS_KEYS,
    EURING2020_FIELDS,
    EURING2020_KEYS,
    NON_EURING2000_KEYS,
)
from euring.formats import FORMAT_EURING2000, FORMAT_EURING2000PLUS, FORMAT_EURING2020

from .fixtures import (
    EURING2000_TEST_DATA,
    EURING2000PLUS_TEST_DATA,
    EURING2020_TEST_DATA,
    _make_euring2000_record,
    _make_euring2000plus_record,
    _make_euring2020_record,
)


def test_euring_detect_format():
    assert euring_detect_format("") == FORMAT_EURING2000
    assert euring_detect_format("|" * (len(EURING2000_FIELDS) - 1)) == FORMAT_EURING2000PLUS
    assert euring_detect_format("|" * (len(EURING2000PLUS_FIELDS) - 1)) == FORMAT_EURING2000PLUS
    assert euring_detect_format("|" * (len(EURING2020_FIELDS) - 1)) == FORMAT_EURING2020


def test_euring2000_roundtrip():
    record = _make_euring2000_record(**EURING2000_TEST_DATA)
    assert euring_record_to_dict(record, format=FORMAT_EURING2000) == EURING2000_TEST_DATA


def test_euring2000plus_roundtrip():
    record = _make_euring2000plus_record(**EURING2000PLUS_TEST_DATA)
    assert euring_record_to_dict(record, format=FORMAT_EURING2000PLUS) == EURING2000PLUS_TEST_DATA


def test_euring2000plus_roundtrip_on_euring2000_data():
    record = _make_euring2000plus_record(**EURING2000_TEST_DATA)
    data = euring_record_to_dict(record, format=FORMAT_EURING2000PLUS)
    assert list(data) == list(EURING2000PLUS_KEYS)
    assert {key: value for key, value in data.items() if key in EURING2000_KEYS} == EURING2000_TEST_DATA
    for key in NON_EURING2000_KEYS:
        assert data.get(key, "") == ""


def test_euring2020_roundtrip():
    record = _make_euring2020_record(**EURING2020_TEST_DATA)
    assert euring_record_to_dict(record, format=FORMAT_EURING2020) == EURING2020_TEST_DATA


def test_euring2020_roundtrip_on_euring2000_data():
    record = _make_euring2020_record(**EURING2000_TEST_DATA)
    data = euring_record_to_dict(record, format=FORMAT_EURING2020)
    assert list(data) == list(EURING2020_KEYS)
    assert {key: value for key, value in data.items() if key in EURING2000_KEYS} == EURING2000_TEST_DATA
    for key in NON_EURING2000_KEYS:
        assert data.get(key, "") == ""
