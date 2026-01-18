"""
Minimal smoke test.

This test verifies that the package can be installed and that
its most basic public API is usable. It intentionally avoids
pytest and any optional dependencies.
"""


def main():
    import euring

    # Basic import works
    assert hasattr(euring, "__version__")

    # One minimal functional call
    from euring import EuringRecord

    record = EuringRecord.decode(
        "DERA0CD...5206514ZZ1877018770N0ZUFF02U-----120719760----SV55+584200+01348000101030100202301739"
    )
    assert record.display_format == "EURING2000"
    assert record.errors == {"record": [], "fields": []}


if __name__ == "__main__":
    main()
