"""Command-line interface for the EURING library."""

import json
from pathlib import Path
from typing import Any

import typer

from . import __version__
from .codes import (
    lookup_place_code,
    lookup_place_details,
    lookup_ringing_scheme,
    lookup_ringing_scheme_details,
    lookup_species,
    lookup_species_details,
)
from .converters import convert_euring_record
from .data.loader import load_data
from .decoders import EuringParseException, euring_decode_record
from .types import TYPE_ALPHABETIC, TYPE_ALPHANUMERIC, TYPE_INTEGER, TYPE_NUMERIC, TYPE_TEXT, is_valid_type

app = typer.Typer(help="EURING data processing CLI")


@app.command()
def decode(
    euring_string: str = typer.Argument(..., help="EURING record string to decode"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output"),
    format_hint: str | None = typer.Option(
        None,
        "--format",
        help="Force format: euring2000, euring2000plus, or euring2020 (aliases: euring2000+, euring2000p)",
    ),
):
    """Decode a EURING record string."""
    try:
        record = euring_decode_record(euring_string, format_hint=format_hint)
        if as_json:
            payload = _with_meta(record)
            typer.echo(json.dumps(payload, default=str, indent=2 if pretty else None))
            return
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
    short: bool = typer.Option(False, "--short", help="Show concise output"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output"),
):
    """Look up EURING codes (scheme, species, place)."""
    try:
        if code_type.lower() == "scheme":
            if short:
                result = lookup_ringing_scheme(code)
                if as_json:
                    payload = _with_meta({"type": "scheme", "code": code, "description": result})
                    typer.echo(json.dumps(payload, indent=2 if pretty else None))
                    return
                typer.echo(f"Scheme {code}: {result}")
            else:
                details = lookup_ringing_scheme_details(code)
                if as_json:
                    payload = _with_meta({"type": "scheme", "code": code, **details})
                    typer.echo(json.dumps(payload, default=str, indent=2 if pretty else None))
                    return
                typer.echo(f"Scheme {code}")
                _emit_detail("Ringing centre", details.get("ringing_centre"))
                _emit_detail("Country", details.get("country"))
                _emit_detail_bool("Current", details.get("is_current"))
                _emit_detail_bool("EURING", details.get("is_euring"))
                _emit_detail("Updated", details.get("updated"))
                _emit_detail("Notes", details.get("notes"))
        elif code_type.lower() == "species":
            if short:
                result = lookup_species(code)
                if as_json:
                    payload = _with_meta({"type": "species", "code": code, "name": result})
                    typer.echo(json.dumps(payload, indent=2 if pretty else None))
                    return
                typer.echo(f"Species {code}: {result}")
            else:
                details = lookup_species_details(code)
                if as_json:
                    payload = _with_meta({"type": "species", "code": code, **details})
                    typer.echo(json.dumps(payload, default=str, indent=2 if pretty else None))
                    return
                typer.echo(f"Species {code}")
                _emit_detail("Name", details.get("name"))
                _emit_detail("Updated", details.get("updated"))
                _emit_detail("Notes", details.get("notes"))
        elif code_type.lower() == "place":
            if short:
                result = lookup_place_code(code)
                if as_json:
                    payload = _with_meta({"type": "place", "code": code, "name": result})
                    typer.echo(json.dumps(payload, indent=2 if pretty else None))
                    return
                typer.echo(f"Place {code}: {result}")
            else:
                details = lookup_place_details(code)
                if as_json:
                    payload = _with_meta({"type": "place", "place_code": code, **details})
                    typer.echo(json.dumps(payload, default=str, indent=2 if pretty else None))
                    return
                typer.echo(f"Place {code}")
                _emit_detail("Name", details.get("code"))
                _emit_detail("Region", details.get("region"))
                _emit_detail_bool("Current", details.get("is_current"))
                _emit_detail("Updated", details.get("updated"))
                _emit_detail("Notes", details.get("notes"))
        else:
            typer.echo(f"Unknown lookup type: {code_type}", err=True)
            typer.echo("Available types: scheme, species, place", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Lookup error: {e}", err=True)
        _emit_glob_hint(code)
        raise typer.Exit(1)


@app.command()
def dump(
    table: list[str] = typer.Argument(..., help="Code table name(s) to dump"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write JSON to file"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON"),
):
    """Dump one or more code tables as JSON."""
    data_map: dict[str, Any] = {}
    for name in table:
        data = load_data(name)
        if data is None:
            typer.echo(f"Unknown code table: {name}", err=True)
            raise typer.Exit(1)
        data_map[name] = data
    payload: Any = data_map[table[0]] if len(table) == 1 else data_map
    payload = _with_meta({"data": payload})
    text = json.dumps(payload, indent=2 if pretty else None, default=str)
    if output:
        output.write_text(text, encoding="utf-8")
    else:
        typer.echo(text)


@app.command()
def convert(
    euring_string: str = typer.Argument(..., help="EURING record string to convert"),
    source_format: str | None = typer.Option(
        None, "--from", help="Source format (optional): euring2000, euring2000plus, or euring2020"
    ),
    target_format: str = typer.Option(
        "euring2000plus",
        "--to",
        help="Target format: euring2000, euring2000plus, or euring2020 (aliases: euring2000+, euring2000p)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow lossy mappings (e.g., alphabetic accuracy when downgrading from EURING2020).",
    ),
):
    """Convert EURING2000, EURING2000+, and EURING2020 records."""
    try:
        typer.echo(convert_euring_record(euring_string, source_format, target_format, force=force))
    except ValueError as exc:
        typer.echo(f"Convert error: {exc}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()


def main():
    """Entry point for the CLI."""
    app()


def _emit_detail(label: str, value) -> None:
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    typer.echo(f"  {label}: {text}")


def _emit_detail_bool(label: str, value) -> None:
    if value is None:
        return
    typer.echo(f"  {label}: {'yes' if value else 'no'}")


def _emit_glob_hint(value: str) -> None:
    if any(char in value for char in "*?[]"):
        return
    if Path(value).exists():
        typer.echo("Hint: your shell may have expanded a wildcard. Quote patterns like 'CH*'.", err=True)


def _with_meta(payload: dict[str, Any]) -> dict[str, Any]:
    meta = {
        "generator": {
            "name": "euring",
            "version": __version__,
            "url": "https://github.com/observation/euring",
        }
    }
    combined = dict(payload)
    combined["_meta"] = meta
    return combined
