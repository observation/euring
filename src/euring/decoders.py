import uuid
from collections import OrderedDict
from hashlib import md5

from .codes import (
    LOOKUP_ACCURACY_PULLUS_AGE,
    LOOKUP_CATCHING_LURES,
    LOOKUP_CATCHING_METHOD,
    LOOKUP_CIRCUMSTANCES,
    LOOKUP_CONDITION,
    LOOKUP_EURING_CODE_IDENTIFIER,
    LOOKUP_MANIPULATED,
    LOOKUP_METAL_RING_INFORMATION,
    LOOKUP_MOVED_BEFORE_ENCOUNTER,
    LOOKUP_PRIMARY_IDENTIFICATION_METHOD,
    LOOKUP_SEX,
    LOOKUP_STATUS,
    LOOKUP_VERIFICATION_OF_THE_METAL_RING,
    lookup_age,
    lookup_brood_size,
    lookup_date,
    lookup_description,
    lookup_geographical_coordinates,
    lookup_other_marks,
    lookup_place_code,
    lookup_pullus_age,
    lookup_ring_number,
    lookup_ringing_scheme,
    lookup_species,
    parse_geographical_coordinates,
)
from .exceptions import EuringParseException
from .types import TYPE_ALPHABETIC, TYPE_ALPHANUMERIC, TYPE_INTEGER, TYPE_NUMERIC, TYPE_TEXT, is_valid_type

EURING_FIELDS = [
    dict(name="Ringing Scheme", type=TYPE_ALPHABETIC, length=3, lookup=lookup_ringing_scheme),
    dict(
        name="Primary identification method",
        type=TYPE_ALPHANUMERIC,
        length=2,
        lookup=LOOKUP_PRIMARY_IDENTIFICATION_METHOD,
    ),
    dict(name="Identification number (ring)", type=TYPE_ALPHANUMERIC, length=10, lookup=lookup_ring_number),
    dict(
        name="Verification of the metal ring", type=TYPE_INTEGER, length=1, lookup=LOOKUP_VERIFICATION_OF_THE_METAL_RING
    ),
    dict(name="Metal ring information", type=TYPE_INTEGER, length=1, lookup=LOOKUP_METAL_RING_INFORMATION),
    dict(name="Other marks information", type=TYPE_ALPHABETIC, length=2, lookup=lookup_other_marks),
    dict(name="Species mentioned", type=TYPE_INTEGER, length=5, lookup=lookup_species),
    dict(name="Species concluded", type=TYPE_INTEGER, length=5, lookup=lookup_species),
    dict(name="Manipulated", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_MANIPULATED),
    dict(name="Moved before recovery", type=TYPE_INTEGER, length=1, lookup=LOOKUP_MOVED_BEFORE_ENCOUNTER),
    dict(name="Catching method", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_CATCHING_METHOD),
    dict(name="Catching lures", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_CATCHING_LURES),
    dict(name="Sex mentioned", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_SEX),
    dict(name="Sex concluded", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_SEX),
    dict(name="Age mentioned", type=TYPE_ALPHANUMERIC, length=1, lookup=lookup_age),
    dict(name="Age concluded", type=TYPE_ALPHANUMERIC, length=1, lookup=lookup_age),
    dict(name="Status", type=TYPE_ALPHABETIC, length=1, lookup=LOOKUP_STATUS),
    dict(name="Brood size", type=TYPE_INTEGER, length=2, lookup=lookup_brood_size),
    dict(name="Pullus age", type=TYPE_INTEGER, length=2, lookup=lookup_pullus_age),
    dict(name="Accuracy of pullus age", type=TYPE_ALPHANUMERIC, length=1, lookup=LOOKUP_ACCURACY_PULLUS_AGE),
    dict(name="Date", type=TYPE_INTEGER, length=8, lookup=lookup_date),
    dict(name="Accuracy of date", type=TYPE_INTEGER, length=1),
    dict(name="Time", type=TYPE_ALPHANUMERIC, length=4),
    dict(name="Place Code", type=TYPE_ALPHANUMERIC, length=4, lookup=lookup_place_code),
    dict(
        name="Geographical co-ordinates",
        type=TYPE_ALPHANUMERIC,
        length=15,
        parser=parse_geographical_coordinates,
        lookup=lookup_geographical_coordinates,
    ),
    dict(name="Accuracy of co-ordinates", type=TYPE_INTEGER, length=1),
    dict(name="Condition", type=TYPE_INTEGER, length=1, lookup=LOOKUP_CONDITION),
    dict(name="Circumstances", type=TYPE_INTEGER, length=2, lookup=LOOKUP_CIRCUMSTANCES),
    dict(name="Circumstances presumed", type=TYPE_INTEGER, length=1),
    dict(name="EURING Code identifier", type=TYPE_INTEGER, length=1, lookup=LOOKUP_EURING_CODE_IDENTIFIER),
    dict(name="Derived data - distance", type=TYPE_INTEGER, min_length=0, max_length=5),
    dict(name="Derived data - direction", type=TYPE_INTEGER, length=3),
    dict(name="Derived data - elapsed time", type=TYPE_INTEGER, min_length=0, max_length=5),
    # Starting with Wing Length, fields are no longer required
    # EURING 2000+ Manual, page 4
    dict(name="Wing length", type=TYPE_NUMERIC, required=False),
    dict(name="Third primary", type=TYPE_NUMERIC, required=False),
    dict(name="State of wing point", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Mass", type=TYPE_NUMERIC, required=False),
    dict(name="Moult", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Plumage code", type=TYPE_ALPHANUMERIC, length=1, required=False),
    dict(name="Hind claw", type=TYPE_NUMERIC, required=False),
    dict(name="Bill length", type=TYPE_NUMERIC, required=False),
    dict(name="Bill method", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Total head length", type=TYPE_NUMERIC, required=False),
    dict(name="Tarsus", type=TYPE_NUMERIC, required=False),
    dict(name="Tarsus method", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Tail length", type=TYPE_NUMERIC, required=False),
    dict(name="Tail diference", type=TYPE_NUMERIC, required=False),
    dict(name="Fat score", type=TYPE_INTEGER, length=1, required=False),
    dict(name="Fat score method", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Pectoral muscle", type=TYPE_INTEGER, length=1, required=False),
    dict(name="Brood patch", type=TYPE_ALPHANUMERIC, length=1, required=False),
    dict(name="Primary score", type=TYPE_INTEGER, max_length=2, required=False),
    dict(name="Primary moult", type=TYPE_ALPHANUMERIC, length=10, required=False),
    dict(name="Old greater coverts", type=TYPE_INTEGER, length=1, required=False),
    dict(name="Alula", type=TYPE_INTEGER, length=1, required=False),
    dict(name="Carpal covert", type=TYPE_INTEGER, length=1, required=False),
    dict(name="Sexing method", type=TYPE_ALPHABETIC, length=1, required=False),
    dict(name="Place name", type=TYPE_TEXT, required=False),
    dict(name="Remarks", type=TYPE_TEXT, required=False),
    dict(name="Reference", type=TYPE_TEXT, required=False),
]


def euring_decode_value(
    value, type, required=True, length=None, min_length=None, max_length=None, parser=None, lookup=None
):
    # A minimum length of 0 is the same as not required
    if min_length == 0:
        required = False
    # What to do with an empty value
    if value == "":
        if required is False:
            # If not required, an empty value will result in None, regardless of the type check
            return None
        else:
            raise EuringParseException('Required field, empty value "" is not permitted.')
    # Check the type
    if not is_valid_type(value, type):
        raise EuringParseException(f'Value "{value}" is not valid for type {type}.')
    # Length checks
    value_length = len(value)
    # Check length
    if length is not None:
        if value_length != length:
            raise EuringParseException(f'Value "{value}" is length {value_length} instead of {length}.')
    # Check min_length
    if min_length is not None:
        if value_length < min_length:
            raise EuringParseException(f'Value "{value}" is length {value_length}, should be at least {min_length}.')
    # Check max_length
    if max_length is not None:
        if value_length > max_length:
            raise EuringParseException(f'Value "{value}" is length {value_length}, should be at most {max_length}.')
    # Results
    results = {"value": value}
    # Extra parser if needed
    if parser:
        value = parser(value)
        results["parsed_value"] = value
    # Look up description
    results["description"] = lookup_description(value, lookup)
    # Return results
    return results


def euring_decode_record(value):
    """
    Decode a EURING record.

    :param value: EURING text
    :return: OrderedDict with results
    """
    decoder = EuringDecoder(value)
    return decoder.get_results()


class EuringDecoder:
    value_to_decode = None
    results = None
    errors = None

    def __init__(self, value_to_decode):
        self.value_to_decode = value_to_decode
        super().__init__()

    def add_error(self, field, message):
        if not field:
            field = 0
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(f"{message}")

    def parse_field(self, fields, index, name, **kwargs):
        required = kwargs.get("required", True)
        try:
            value = fields[index]
        except IndexError:
            if required:
                self.add_error(name, f"Could not retrieve value from index {index}.")
            return
        if name in self.results["data"]:
            self.add_error(name, "A value is already present in results.")
            return
        try:
            self.results["data"][name] = euring_decode_value(value, **kwargs)
        except EuringParseException as e:
            self.add_error(name, e)

    def clean(self):
        # Removed Django Point creation for standalone version
        pass

    def decode(self):
        self.results = OrderedDict()
        self.errors = OrderedDict()
        self.results["data"] = OrderedDict()
        self._decode()
        self.clean()
        self.results["errors"] = self.errors

    def _decode(self):
        try:
            fields = self.value_to_decode.split("|")
        except AttributeError:
            self.add_error(0, f'Value "{self.value_to_decode}" cannot be split with pipe character.')
            return

        # Just one field? Then we have EURING2000
        if len(fields) <= 1:
            fields = []
            start = 0
            done = False
            for index, field_kwargs in enumerate(EURING_FIELDS):
                # EURING20000 stops after position 94
                if start >= 94:
                    break
                # Get length from length or max_length
                length = field_kwargs.get("length", field_kwargs.get("max_length", None))
                if length:
                    # If there is a length, let's go
                    if done:
                        self.add_error(
                            0,
                            f'Value "{self.value_to_decode}" invalid EURING2000 code beyond position {start}.',
                        )
                        return
                    end = start + length
                    value = self.value_to_decode[start:end]
                    start = end
                    fields.append(value)
                else:
                    # No length, so we don't expect any more valid fields
                    done = True
            self.results["format"] = "EURING2000"
        else:
            self.results["format"] = "EURING2000+"

        # Parse the fields
        for index, field_kwargs in enumerate(EURING_FIELDS):
            self.parse_field(fields, index, **field_kwargs)

        # Some post processing
        try:
            scheme = self.results["data"]["Ringing Scheme"]["value"]
        except KeyError:
            scheme = "---"
        try:
            ring = self.results["data"]["Identification number (ring)"]["description"]
        except KeyError:
            ring = "----------"
        try:
            date = self.results["data"]["Date"]["description"]
        except KeyError:
            date = None
        self.results["ring"] = ring
        self.results["scheme"] = scheme
        self.results["animal"] = f"{scheme}#{ring}"
        self.results["date"] = date
        # Unique hash for this euring code
        self.results["hash"] = md5(f"{self.value_to_decode}".encode()).hexdigest()
        # Unique id for this record
        self.results["id"] = uuid.uuid4()

    def get_results(self):
        if self.results is None:
            self.decode()
        return self.results
