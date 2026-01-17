from collections import OrderedDict

from .codes import lookup_description
from .exceptions import EuringParseException
from .fields import EURING_FIELDS
from .formats import (
    FORMAT_EURING2000,
    FORMAT_EURING2000PLUS,
    FORMAT_EURING2020,
    format_display_name,
    normalize_format,
    unknown_format_error,
)
from .rules import field_name_for_key, record_rule_errors, requires_euring2020
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


def decode_fields(value, format: str | None = None) -> dict[str, object]:
    """Decode a EURING record into fields, errors, and the detected format."""
    decoder = _EuringDecoder(value, format=format)
    result = decoder.get_results()
    record_format = decoder.record_format or (normalize_format(format) if format else FORMAT_EURING2000PLUS)
    return {
        "format": record_format,
        "fields": result.get("fields", OrderedDict()),
        "errors": result.get("errors", {"record": [], "fields": []}),
    }


def euring_decode_record(value, format: str | None = None):
    """
    Decode a EURING record.

    :param value: EURING text
    :param format: Optional format declaration ("euring2000", "euring2000plus", "euring2020")
    :return: EuringRecord instance
    """
    result = decode_fields(value, format=format)
    from .record import EuringRecord

    record = EuringRecord(result["format"], strict=False)
    record.fields = result["fields"]
    record.errors = result["errors"]
    return record


class _EuringDecoder:
    """Decode a EURING record into structured data and errors."""

    value_to_decode = None
    results = None
    errors = None

    def __init__(self, value_to_decode, format: str | None = None):
        """Initialize a decoder for a single record."""
        self.value_to_decode = value_to_decode
        self.format = self._normalize_format(format)
        self._data = OrderedDict()
        self._data_by_key = OrderedDict()
        self._field_positions = {}
        self.record_format: str | None = None
        super().__init__()

    def add_record_error(self, message):
        """Add a record-level error."""
        self.errors["record"].append({"message": f"{message}"})

    def add_field_error(
        self,
        field,
        message,
        *,
        value="",
        key=None,
        index=None,
    ):
        """Add a field-level error with optional metadata."""
        payload = {
            "field": field,
            "message": f"{message}",
            "value": "" if value is None else f"{value}",
        }
        if key is not None:
            payload["key"] = key
        if index is not None:
            payload["index"] = index
            if self.record_format == FORMAT_EURING2000:
                payload["position"] = self._field_positions.get(index, {}).get("position")
                payload["length"] = self._field_positions.get(index, {}).get("length")
        self.errors["fields"].append(payload)

    def parse_field(self, fields, index, name, key=None, **kwargs):
        """Parse and validate a field value into the result structure."""
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
                )
            return
        if name in self._data:
            self.add_field_error(
                name,
                "A value is already present in results.",
                value=value,
                key=key,
                index=index,
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
            )
            return
        self._data[name] = decoded
        if key:
            if decoded is None:
                self._data_by_key[key] = None
            else:
                decoded["key"] = key
                self._data_by_key[key] = decoded

    def decode(self):
        """Decode the record and populate results/errors."""
        self.results = OrderedDict()
        self.errors = {"record": [], "fields": []}
        self._field_positions = {}
        self._data = OrderedDict()
        self._data_by_key = OrderedDict()
        self._decode()
        if "record" not in self.results:
            self.results["record"] = {"format": None}
        if "fields" not in self.results:
            self.results["fields"] = OrderedDict()
        self.results["errors"] = self.errors

    def _decode(self):
        """Perform the internal decoding steps."""
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
        values_by_key = self._values_by_key()
        if current_format in {FORMAT_EURING2000PLUS, FORMAT_EURING2020}:
            is_2020 = requires_euring2020(values_by_key)
            if is_2020 and current_format == FORMAT_EURING2000PLUS and self.format is None:
                current_format = FORMAT_EURING2020
            elif current_format == FORMAT_EURING2020 and self.format is None and not is_2020:
                # Format was explicitly set to EURING2020 elsewhere; keep it as-is.
                pass
        for error in record_rule_errors(current_format, values_by_key):
            self._add_field_error_for_key(
                error["key"],
                field_name_for_key(error["key"]),
                error["message"],
                value=error["value"],
            )

        # Record metadata output is assembled after field validation.

        self.results["record"] = {"format": format_display_name(current_format)}
        self.results["fields"] = self._build_fields()
        self.record_format = current_format

    def get_results(self):
        """Return decoded results, decoding if needed."""
        if self.results is None:
            self.decode()
        return self.results

    def _build_fields(self) -> OrderedDict:
        """Build the public fields mapping from decoded values."""
        fields = OrderedDict()
        for index, field in enumerate(EURING_FIELDS):
            key = field["key"]
            if key not in self._data_by_key:
                continue
            decoded = self._data_by_key.get(key)
            value = None if decoded is None else decoded.get("value", "")
            fields[key] = {
                "name": field["name"],
                "value": value,
                "order": index,
            }
        return fields

    def _add_field_error_for_key(self, key, field_name, message, value=None):
        """Add a field error using a field key to look up metadata."""
        field_index = None
        for index, field in enumerate(EURING_FIELDS):
            if field.get("key") == key:
                field_index = index
                break
        if value is None:
            stored = self._data_by_key.get(key)
            value = stored.get("value") if stored else ""
        self.add_field_error(
            field_name,
            message,
            value=value,
            key=key,
            index=field_index,
        )

    def _is_euring2020(self) -> bool:
        """Return True when decoded values require EURING2020."""
        return requires_euring2020(self._values_by_key())

    def _values_by_key(self) -> dict[str, str]:
        """Return decoded values keyed by field key."""
        return {key: (value.get("value") if value else "") for key, value in self._data_by_key.items()}

    @staticmethod
    def _normalize_format(format: str | None) -> str | None:
        """Normalize a user-provided format string or raise."""
        if not format:
            return None
        try:
            return normalize_format(format)
        except ValueError:
            raise EuringParseException(unknown_format_error(format))
