import uuid
from collections import OrderedDict
from hashlib import md5

from .codes import lookup_description
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
    format_display_name,
    format_error,
    normalize_format,
)
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


def euring_decode_record(value, format: str | None = None):
    """
    Decode a EURING record.

    :param value: EURING text
    :param format: Optional format declaration ("euring2000", "euring2000plus", "euring2020")
    :return: OrderedDict with results
    """
    decoder = EuringDecoder(value, format=format)
    return decoder.get_results()


class EuringDecoder:
    """Decode a EURING record into structured data and errors."""

    value_to_decode = None
    results = None
    errors = None

    def __init__(self, value_to_decode, format: str | None = None):
        self.value_to_decode = value_to_decode
        self.format = self._normalize_format(format)
        self._field_positions = {}
        super().__init__()

    def add_record_error(self, message):
        self.errors["record"].append({"message": f"{message}"})

    def add_field_error(
        self,
        field,
        message,
        *,
        value="",
        key=None,
        index=None,
        position=None,
        length=None,
    ):
        payload = {
            "field": field,
            "message": f"{message}",
            "value": "" if value is None else f"{value}",
        }
        if key is not None:
            payload["key"] = key
        if index is not None:
            payload["index"] = index
        if position is not None:
            payload["position"] = position
        if length is not None:
            payload["length"] = length
        self.errors["fields"].append(payload)

    def parse_field(self, fields, index, name, key=None, **kwargs):
        required = kwargs.get("required", True)
        try:
            value = fields[index]
        except IndexError:
            if required:
                self.add_field_error(
                    name,
                    f"Could not retrieve value from index {index}.",
                    value="",
                    key=key,
                    index=index,
                    position=self._field_positions.get(index, {}).get("position"),
                    length=self._field_positions.get(index, {}).get("length"),
                )
            return
        if name in self.results["data"]:
            self.add_field_error(
                name,
                "A value is already present in results.",
                value=value,
                key=key,
                index=index,
                position=self._field_positions.get(index, {}).get("position"),
                length=self._field_positions.get(index, {}).get("length"),
            )
            return
        try:
            decoded = euring_decode_value(value, **kwargs)
        except EuringParseException as e:
            self.add_field_error(
                name,
                e,
                value=value,
                key=key,
                index=index,
                position=self._field_positions.get(index, {}).get("position"),
                length=self._field_positions.get(index, {}).get("length"),
            )
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
        self.errors = {"record": [], "fields": []}
        self._field_positions = {}
        self.results["data"] = OrderedDict()
        self.results["data_by_key"] = OrderedDict()
        self._decode()
        self.clean()
        self.results["errors"] = self.errors

    def _decode(self):
        try:
            fields = self.value_to_decode.split("|")
        except AttributeError:
            self.add_record_error(f'Value "{self.value_to_decode}" cannot be split with pipe character.')
            return

        # Just one field? Then we have EURING2000
        if len(fields) <= 1:
            if self.format and self.format != FORMAT_EURING2000:
                self.add_record_error(
                    f'Format "{format_display_name(self.format)}" conflicts with fixed-width EURING2000 data.'
                )
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
                        self.add_record_error(
                            f'Value "{self.value_to_decode}" invalid EURING2000 code beyond position {start}.'
                        )
                        return
                    end = start + length
                    value = self.value_to_decode[start:end]
                    self._field_positions[index] = {"position": start + 1, "length": length}
                    start = end
                    fields.append(value)
                else:
                    # No length, so we don't expect any more valid fields
                    done = True
            current_format = FORMAT_EURING2000
        else:
            if self.format == FORMAT_EURING2000:
                self.add_record_error(
                    f'Format "{format_display_name(self.format)}" conflicts with pipe-delimited data.'
                )
            current_format = self.format or FORMAT_EURING2000PLUS

        # Parse the fields
        for index, field_kwargs in enumerate(EURING_FIELDS):
            self.parse_field(fields, index, **field_kwargs)
        if current_format in {FORMAT_EURING2000PLUS, FORMAT_EURING2020}:
            is_2020 = self._is_euring2020()
            if is_2020 and current_format == FORMAT_EURING2000PLUS:
                if self.format:
                    data_by_key = self.results.get("data_by_key") or {}
                    accuracy = data_by_key.get("accuracy_of_coordinates")
                    self._add_field_error_for_key(
                        "accuracy_of_coordinates",
                        "Accuracy of Co-ordinates",
                        "Alphabetic accuracy codes or 2020-only fields require EURING2020 format.",
                        value=accuracy.get("value") if accuracy else "",
                    )
                else:
                    current_format = FORMAT_EURING2020
            elif current_format == FORMAT_EURING2020 and self.format is None and not is_2020:
                # Format was explicitly set to EURING2020 elsewhere; keep it as-is.
                pass
        if current_format == FORMAT_EURING2000 and self._accuracy_is_alpha():
            data_by_key = self.results.get("data_by_key") or {}
            accuracy = data_by_key.get("accuracy_of_coordinates")
            self._add_field_error_for_key(
                "accuracy_of_coordinates",
                "Accuracy of Co-ordinates",
                "Alphabetic accuracy codes are only valid in EURING2020.",
                value=accuracy.get("value") if accuracy else "",
            )
        if current_format == FORMAT_EURING2020:
            data_by_key = self.results.get("data_by_key") or {}
            geo = data_by_key.get("geographical_coordinates")
            lat = data_by_key.get("latitude")
            lng = data_by_key.get("longitude")
            geo_value = geo.get("value") if geo else None
            lat_value = lat.get("value") if lat else None
            lng_value = lng.get("value") if lng else None
            if lat_value or lng_value:
                if geo_value and geo_value != "." * 15:
                    self._add_field_error_for_key(
                        "geographical_coordinates",
                        "Geographical Co-ordinates",
                        "When Latitude/Longitude are provided, Geographical Co-ordinates must be 15 dots.",
                        value=geo_value or "",
                    )
            if lat_value and not lng_value:
                self._add_field_error_for_key(
                    "longitude",
                    "Longitude",
                    "Longitude is required when Latitude is provided.",
                    value="",
                )
            if lng_value and not lat_value:
                self._add_field_error_for_key(
                    "latitude",
                    "Latitude",
                    "Latitude is required when Longitude is provided.",
                    value="",
                )

        self.results["format"] = format_display_name(current_format)

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
        self.results["ringing_scheme"] = scheme
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

    def _add_field_error_for_key(self, key, field_name, message, value=None):
        field_index = None
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == key:
                field_index = index
                break
        if value is None:
            data_by_key = self.results.get("data_by_key") or {}
            stored = data_by_key.get(key)
            value = stored.get("value") if stored else ""
        position = self._field_positions.get(field_index, {}).get("position") if field_index is not None else None
        length = self._field_positions.get(field_index, {}).get("length") if field_index is not None else None
        self.add_field_error(
            field_name,
            message,
            value=value,
            key=key,
            index=field_index,
            position=position,
            length=length,
        )

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
    def _normalize_format(format: str | None) -> str | None:
        if not format:
            return None
        try:
            return normalize_format(format)
        except ValueError:
            raise EuringParseException(format_error(format))
