from euring.exceptions import EuringConstraintException


def lat_lng_to_euring_coordinates(lat: float, lng: float) -> str:
    """Format latitude and longitude as EURING geographical coordinates."""
    return f"{_lat_to_euring_coordinate(lat)}{_lng_to_euring_coordinate(lng)}"


def euring_coordinates_to_lat_lng(value: str) -> dict[str, float]:
    """Parse EURING geographical coordinates into latitude/longitude decimals."""
    lat_str = value[:7]
    lng_str = value[7:]
    return dict(lat=_euring_coordinate_to_decimal(lat_str), lng=_euring_coordinate_to_decimal(lng_str))


def _euring_coordinate_to_decimal(value: str) -> float:
    """Convert EURING geographical coordinate string to decimal coordinate."""
    try:
        seconds = value[-2:]
        minutes = value[-4:-2]
        degrees = value[:-4]
        result = float(degrees)
        negative = result < 0
        result = abs(result) + (float(minutes) / 60) + (float(seconds) / 3600)
        if negative:
            result = -result
    except (IndexError, ValueError):
        raise EuringConstraintException('Could not parse coordinate "{value}" to decimal.')
    return result


def _decimal_to_euring_coordinate(value: float, degrees_pos: int) -> str:
    """Format a decimal coordinate into EURING DMS text with fixed degree width."""
    parts = _decimal_to_euring_coordinate_components(value)
    return "{quadrant}{degrees}{minutes}{seconds}".format(
        quadrant=parts["quadrant"],
        degrees="{}".format(abs(parts["degrees"])).zfill(degrees_pos),
        minutes="{}".format(parts["minutes"]).zfill(2),
        seconds="{}".format(parts["seconds"]).zfill(2),
    )


def _lat_to_euring_coordinate(value: float) -> str:
    """Convert a latitude in decimal degrees to a EURING coordinate string."""
    return _decimal_to_euring_coordinate(value, degrees_pos=2)


def _lng_to_euring_coordinate(value: float) -> str:
    """Convert a longitude in decimal degrees to a EURING DMS coordinae string."""
    return _decimal_to_euring_coordinate(value, degrees_pos=3)


def _decimal_to_euring_coordinate_components(value: float) -> dict[str, int | float | str]:
    """Convert a decimal coordinate into EURING geographical coordinate components."""
    degrees = int(value)
    submin = abs((value - int(value)) * 60)
    minutes = int(submin)
    seconds = abs((submin - int(submin)) * 60)
    quadrant = "-" if degrees < 0 else "+"
    seconds = int(round(seconds))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees = degrees + 1 if degrees >= 0 else degrees - 1
    return {"quadrant": quadrant, "degrees": degrees, "minutes": minutes, "seconds": seconds}


def _validate_euring_coordinates(value: str | None) -> None:
    """Validate a combined EURING latitude/longitude coordinate string."""
    if value is None:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    if len(value) != 15:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    _validate_euring_coordinate_component(value[:7], degrees_digits=2, max_degrees=90)
    _validate_euring_coordinate_component(value[7:], degrees_digits=3, max_degrees=180)


def _validate_euring_coordinate_component(value: str | None, *, degrees_digits: int, max_degrees: int) -> None:
    """Validate a single EURING coordinate component."""
    if value is None:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    expected_length = 1 + degrees_digits + 2 + 2
    if len(value) != expected_length:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    sign = value[0]
    if sign not in {"+", "-"}:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    degrees = value[1 : 1 + degrees_digits]
    minutes = value[1 + degrees_digits : 1 + degrees_digits + 2]
    seconds = value[1 + degrees_digits + 2 :]
    if not (degrees.isdigit() and minutes.isdigit() and seconds.isdigit()):
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
    if int(degrees) > max_degrees or int(minutes) > 59 or int(seconds) > 59:
        raise EuringConstraintException(f'Value "{value}" is not a valid set of coordinates.')
