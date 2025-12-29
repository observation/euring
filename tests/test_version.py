"""Version metadata tests."""


def test_version():
    import euring

    version = euring.__version__
    assert version != "0+unknown"
    version_parts = version.split(".")
    assert len(version_parts) in (2, 3)
