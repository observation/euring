import uuid
from collections import OrderedDict
from hashlib import md5

from .codes import lookup_description
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .types import is_valid_type


def euring_decode_value(
    value, type, required=True, length=None, min_length=None, max_length=None, parser=None, lookup=None
):
    """Decode a single EURING field value with type checks, parsing, and lookup."""
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


def euring_decode_record(value, format_hint: str | None = None):
    """
    Decode a EURING record.

    :param value: EURING text
    :param format_hint: Optional format hint ("EURING2000", "EURING2000+", "EURING2020")
    :return: OrderedDict with results
    """
    decoder = EuringDecoder(value, format_hint=format_hint)
    return decoder.get_results()


class EuringDecoder:
    """Decode a EURING record into structured data and errors."""

    value_to_decode = None
    results = None
    errors = None

    def __init__(self, value_to_decode, format_hint: str | None = None):
        self.value_to_decode = value_to_decode
        self.format_hint = self._normalize_format_hint(format_hint)
        super().__init__()

    def add_error(self, field, message):
        if not field:
            field = 0
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(f"{message}")

    def parse_field(self, fields, index, name, key=None, **kwargs):
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
            decoded = euring_decode_value(value, **kwargs)
        except EuringParseException as e:
            self.add_error(name, e)
            return
        self.results["data"][name] = decoded
        if key:
            if decoded is None:
                self.results["data_by_key"][key] = None
            else:
                decoded["key"] = key
                self.results["data_by_key"][key] = decoded

    def clean(self):
        # Removed Django Point creation for standalone version
        pass

    def decode(self):
        self.results = OrderedDict()
        self.errors = OrderedDict()
        self.results["data"] = OrderedDict()
        self.results["data_by_key"] = OrderedDict()
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
            if self.format_hint and self.format_hint != "EURING2000":
                self.add_error(0, f'Format hint "{self.format_hint}" conflicts with fixed-width EURING2000 data.')
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
            if self.format_hint == "EURING2000":
                self.add_error(0, 'Format hint "EURING2000" conflicts with pipe-delimited data.')
            self.results["format"] = self.format_hint or "EURING2000+"

        # Parse the fields
        for index, field_kwargs in enumerate(EURING_FIELDS):
            self.parse_field(fields, index, **field_kwargs)
        if self.results["format"] in {"EURING2000+", "EURING2020"}:
            is_2020 = self._is_euring2020()
            if is_2020 and self.results["format"] == "EURING2000+":
                if self.format_hint:
                    self.add_error(
                        "Accuracy of Co-ordinates",
                        "Alphabetic accuracy codes or 2020-only fields require EURING2020 format.",
                    )
                else:
                    self.results["format"] = "EURING2020"
            elif self.results["format"] == "EURING2020" and self.format_hint is None and not is_2020:
                # Format was explicitly set to EURING2020 elsewhere; keep it as-is.
                pass
        if self.results["format"] == "EURING2000" and self._accuracy_is_alpha():
            self.add_error(
                "Accuracy of Co-ordinates",
                "Alphabetic accuracy codes are only valid in EURING2020.",
            )
        if self.results["format"] == "EURING2020":
            data_by_key = self.results.get("data_by_key") or {}
            geo = data_by_key.get("geographical_coordinates")
            lat = data_by_key.get("latitude")
            lng = data_by_key.get("longitude")
            geo_value = geo.get("value") if geo else None
            lat_value = lat.get("value") if lat else None
            lng_value = lng.get("value") if lng else None
            if lat_value or lng_value:
                if geo_value and geo_value != "." * 15:
                    self.add_error(
                        "Geographical Co-ordinates",
                        "When Latitude/Longitude are provided, Geographical Co-ordinates must be 15 dots.",
                    )
            if lat_value and not lng_value:
                self.add_error("Longitude", "Longitude is required when Latitude is provided.")
            if lng_value and not lat_value:
                self.add_error("Latitude", "Latitude is required when Longitude is provided.")

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

    def _is_euring2020(self) -> bool:
        data_by_key = self.results.get("data_by_key") or {}
        if self._accuracy_is_alpha():
            return True
        for key in ("latitude", "longitude", "current_place_code", "more_other_marks"):
            value = data_by_key.get(key)
            if value and value.get("value"):
                return True
        return False

    def _accuracy_is_alpha(self) -> bool:
        data_by_key = self.results.get("data_by_key") or {}
        accuracy = data_by_key.get("accuracy_of_coordinates")
        if not accuracy:
            return False
        value = accuracy.get("value")
        return bool(value) and value.isalpha()

    @staticmethod
    def _normalize_format_hint(format_hint: str | None) -> str | None:
        if not format_hint:
            return None
        raw = format_hint.strip()
        normalized = raw.upper()
        if normalized.startswith("EURING"):
            normalized = normalized.replace("EURING", "")
        else:
            hint = _format_hint_suggestion(normalized)
            message = f'Unknown format hint "{format_hint}". Use euring2000, euring2000plus, or euring2020.'
            if hint:
                message = f"{message} Did you mean {hint}?"
            raise EuringParseException(message)
        if normalized in {"2000", "2000+", "2000PLUS", "2000P", "2020"}:
            if normalized in {"2000PLUS", "2000P"}:
                normalized = "2000+"
            return f"EURING{normalized}"
        raise EuringParseException(
            f'Unknown format hint "{format_hint}". Use euring2000, euring2000plus, or euring2020.'
        )


def _format_hint_suggestion(normalized: str) -> str | None:
    if normalized in {"2000", "2000+", "2000PLUS", "2000P"}:
        return "euring2000plus"
    if normalized == "2020":
        return "euring2020"
    return None
