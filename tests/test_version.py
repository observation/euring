"""Version metadata tests."""


def test_version():
    import euring

    version = euring.__version__
    assert version != "0+unknown"
    version_parts = version.split(".")
    assert len(version_parts) in (2, 3)


def test_version_fallback(monkeypatch):
    import importlib
    from importlib import metadata

    import euring.__about__ as about

    def _raise(_name):
        raise metadata.PackageNotFoundError

    monkeypatch.setattr(metadata, "version", _raise)
    reloaded = importlib.reload(about)
    assert reloaded.__version__ == "0+unknown"
