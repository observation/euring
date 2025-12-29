"""EURING2020 example records with provenance for tests."""

EURING2020_EXAMPLES = [
    # Source records were upgraded from euring2000_examples.py and euring2000plus_examples.py.
    # All records add EURING2020 latitude/longitude derived from their source DMS coordinates.
    # The first record uses alphabetic accuracy code.
    "DER|A0|CD...52065|0|1|ZZ|18770|18770|N|0|Z|U|F|F|2|2|U|--|--|-|08101971|0|----|DECK|...............|G|8|20|0|3|00000|000|00000||||||||||||||||||||||||||||50.4000|7.7000||",
    "DER|A0|CD...52065|1|4|ZZ|18770|18770|N|0|Z|U|F|F|0|2|U|--|--|-|12071976|0|----|SV55|...............|0|1|01|0|3|01002|023|01739||||||||||||||||||||||||||||58.7000|13.8000||",
    "ESA|A0|Z.....6408|1|4|ZZ|12430|12430|N|0|Z|U|U|U|0|0|U|--|--|-|11082006|0|----|ES14|...............|0|0|99|0|4|00280|241|00097|63.5||U|10|U|U|||||||||3|E||0||||||||||42.0833|-4.7500||",
]

__all__ = ["EURING2020_EXAMPLES"]
