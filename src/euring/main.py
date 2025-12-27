"""Command-line interface for the EURING library."""

import typer

from .codes import lookup_place_code, lookup_ringing_scheme, lookup_species
from .decoders import EuringParseException, euring_decode_record
from .types import TYPE_ALPHABETIC, TYPE_ALPHANUMERIC, TYPE_INTEGER, TYPE_NUMERIC, TYPE_TEXT, is_valid_type

app = typer.Typer(help="EURING data processing CLI")


@app.command()
def decode(euring_string: str = typer.Argument(..., help="EURING record string to decode")):
    """Decode a EURING record string."""
    try:
        record = euring_decode_record(euring_string)
        typer.echo("Decoded EURING record:")
        typer.echo(f"Format: {record.get('format', 'Unknown')}")
        typer.echo(f"Scheme: {record.get('scheme', 'Unknown')}")
        if "data" in record:
            typer.echo("Data fields:")
            for key, value in record["data"].items():
                typer.echo(f"  {key}: {value}")
    except EuringParseException as e:
        typer.echo(f"Parse error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    value: str = typer.Argument(..., help="Value to validate"),
    field_type: str = typer.Argument(
        "alphabetic", help="Field type to validate against (alphabetic, alphanumeric, integer, numeric, text)"
    ),
):
    """Validate a value against EURING field types."""
    type_map = {
        "alphabetic": TYPE_ALPHABETIC,
        "alphanumeric": TYPE_ALPHANUMERIC,
        "integer": TYPE_INTEGER,
        "numeric": TYPE_NUMERIC,
        "text": TYPE_TEXT,
    }

    if field_type.lower() not in type_map:
        typer.echo(f"Unknown field type: {field_type}", err=True)
        typer.echo(f"Available types: {', '.join(type_map.keys())}", err=True)
        raise typer.Exit(1)

    eur_type = type_map[field_type.lower()]
    is_valid = is_valid_type(value, eur_type)

    if is_valid:
        typer.echo(f"✓ '{value}' is valid {field_type}")
    else:
        typer.echo(f"✗ '{value}' is not valid {field_type}")
        raise typer.Exit(1)


@app.command()
def lookup(
    code_type: str = typer.Argument(..., help="Type of code to lookup"),
    code: str = typer.Argument(..., help="Code value to lookup"),
):
    """Look up EURING codes (scheme, species, place)."""
    try:
        if code_type.lower() == "scheme":
            result = lookup_ringing_scheme(code)
            typer.echo(f"Scheme {code}: {result}")
        elif code_type.lower() == "species":
            result = lookup_species(code)
            typer.echo(f"Species {code}: {result}")
        elif code_type.lower() == "place":
            result = lookup_place_code(code)
            typer.echo(f"Place {code}: {result}")
        else:
            typer.echo(f"Unknown lookup type: {code_type}", err=True)
            typer.echo("Available types: scheme, species, place", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Lookup error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()


def main():
    """Entry point for the CLI."""
    app()
