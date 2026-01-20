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
from .data.code_tables import EURING_CODE_TABLES
from .data.loader import load_data
from .exceptions import EuringParseException
from .formats import FORMAT_EURING2020
from .record import EuringRecord

app = typer.Typer(help="EURING data processing CLI")


@app.command()
def decode(
    euring_string: str | None = typer.Argument(None, help="EURING record to decode"),
    file: Path | None = typer.Option(None, "--file", "-f", help="Read records from a text file (one per line)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write output to a file"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output (requires --json)"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Force EURING format: euring2000, euring2000plus, or euring2020.",
    ),
):
    """Decode EURING records (single record or --file)."""
    try:
        if pretty and not as_json:
            typer.echo("Use --pretty with --json.", err=True)
            raise typer.Exit(1)
        output_format = "json" if as_json else "text"
        if file and euring_string:
            typer.echo("Use either a record or --file, not both.", err=True)
            raise typer.Exit(1)
        if not file and not euring_string:
            typer.echo("Provide a record or use --file.", err=True)
            raise typer.Exit(1)
        if file:
            if output_format != "json":
                typer.echo("Use --json when decoding files.", err=True)
                raise typer.Exit(1)
            lines = _lines_from_file(file)
            records = []
            has_errors = False
            for line in lines:
                record_line = line.strip()
                if not record_line:
                    continue
                record = EuringRecord.decode(record_line, format=format)
                if _has_errors(record.errors):
                    has_errors = True
                records.append(record.to_dict())
            payload = _with_meta({"records": records})
            text = json.dumps(payload, default=str, indent=2 if pretty else None)
            if output:
                output.write_text(text, encoding="utf-8")
                if has_errors:
                    raise typer.Exit(1)
                return
            typer.echo(text)
            if has_errors:
                raise typer.Exit(1)
            return
        record = EuringRecord.decode(euring_string, format=format)
        errors = record.errors
        if output_format == "json":
            payload = _with_meta(record.to_dict())
            text = json.dumps(payload, default=str, indent=2 if pretty else None)
            if output:
                output.write_text(text, encoding="utf-8")
                if _has_errors(errors):
                    raise typer.Exit(1)
                return
            typer.echo(text)
            if _has_errors(errors):
                raise typer.Exit(1)
            return
        typer.echo("Decoded EURING record:")
        format_value = record.display_format
        typer.echo(f"Format: {format_value}")
        fields = record.fields or {}
        if "ringing_scheme" in fields:
            typer.echo(f"Ringing Scheme: {fields['ringing_scheme'].get('value', 'Unknown')}")
        if fields:
            typer.echo("Data fields:")
            for field in fields.values():
                name = field.get("name", "Unknown")
                value = field.get("value", "")
                typer.echo(f"  {name}: {value}")
        if _has_errors(errors):
            typer.echo("Record has errors:", err=True)
            for line in _format_error_lines(errors, indent="  "):
                typer.echo(line, err=True)
            raise typer.Exit(1)
    except EuringParseException as e:
        typer.echo(f"Parse error: {e}", err=True)
        raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="validate")
def validate_record(
    euring_string: str | None = typer.Argument(None, help="EURING record to validate"),
    file: Path | None = typer.Option(None, "--file", "-f", help="Read records from a text file (one per line)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write output to a file"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output (requires --json)"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Force EURING format: euring2000, euring2000plus, or euring2020",
    ),
):
    """Validate EURING records and return errors only."""
    try:
        if pretty and not as_json:
            typer.echo("Use --pretty with --json.", err=True)
            raise typer.Exit(1)
        if file and euring_string:
            typer.echo("Use either a record or --file, not both.", err=True)
            raise typer.Exit(1)
        if not file and not euring_string:
            typer.echo("Provide a record or use --file.", err=True)
            raise typer.Exit(1)

        if file:
            lines = _lines_from_file(file)
            results: list[dict[str, object]] = []
            total = 0
            invalid = 0
            for index, line in enumerate(lines, start=1):
                record_line = line.strip()
                if not record_line:
                    continue
                total += 1
                record = EuringRecord.decode(record_line, format=format)
                errors = record.errors
                if _has_errors(errors):
                    invalid += 1
                    results.append({"line": index, "record": record_line, "errors": errors})
            if as_json:
                payload = _with_meta({"total": total, "invalid": invalid, "errors": results})
                text = json.dumps(payload, default=str, indent=2 if pretty else None)
                if output:
                    output.write_text(text, encoding="utf-8")
                else:
                    typer.echo(text)
                if invalid:
                    raise typer.Exit(1)
                return
            if invalid:
                typer.echo(f"{invalid} of {total} records have errors:")
                for item in results:
                    typer.echo(f"  Line {item['line']}:")
                    for line in _format_error_lines(item["errors"], indent="    "):
                        typer.echo(line)
                raise typer.Exit(1)
            text = f"All {total} records are valid."
            if output:
                output.write_text(text, encoding="utf-8")
            else:
                typer.echo(text)
            return

        record = EuringRecord.decode(euring_string, format=format)
        errors = record.errors
        if as_json:
            payload = _with_meta({"format": record.display_format, "errors": errors})
            text = json.dumps(payload, default=str, indent=2 if pretty else None)
            if output:
                output.write_text(text, encoding="utf-8")
            else:
                typer.echo(text)
            if _has_errors(errors):
                raise typer.Exit(1)
            return
        if _has_errors(errors):
            typer.echo("Record has errors:")
            for line in _format_error_lines(errors, indent="  "):
                typer.echo(line)
            raise typer.Exit(1)
        text = "Record is valid."
        if output:
            output.write_text(text, encoding="utf-8")
        else:
            typer.echo(text)
    except typer.Exit:
        raise
    except EuringParseException as e:
        typer.echo(f"Validation error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def convert(
    euring_string: str | None = typer.Argument(None, help="EURING record to convert"),
    file: Path | None = typer.Option(None, "--file", "-f", help="Read records from a text file (one per line)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write output to a file"),
    source_format: str | None = typer.Option(
        None, "--from", help="Source format (optional): euring2000, euring2000plus, or euring2020"
    ),
    target_format: str = typer.Option(
        FORMAT_EURING2020,
        "--to",
        help="Target format: euring2000, euring2000plus, or euring2020",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow lossy mappings (e.g., alphabetic accuracy when downgrading from EURING2020).",
    ),
):
    """Convert EURING2000, EURING2000+, and EURING2020 records."""
    try:
        if file and euring_string:
            typer.echo("Use either a record or --file, not both.", err=True)
            raise typer.Exit(1)
        if not file and not euring_string:
            typer.echo("Provide a record or use --file.", err=True)
            raise typer.Exit(1)
        if file:
            lines = _lines_from_file(file)
            outputs: list[str] = []
            errors: list[tuple[int, str]] = []
            for index, line in enumerate(lines, start=1):
                record_line = line.strip()
                if not record_line:
                    continue
                try:
                    outputs.append(convert_euring_record(record_line, source_format, target_format, force=force))
                except ValueError as exc:
                    errors.append((index, str(exc)))
            if errors:
                typer.echo("Conversion errors:", err=True)
                for line_number, message in errors:
                    typer.echo(f"  Line {line_number}: {message}", err=True)
                raise typer.Exit(1)
            output_text = "\n".join(outputs)
            if output:
                output.write_text(output_text, encoding="utf-8")
                return
            typer.echo(output_text)
            return
        if output:
            output.write_text(
                convert_euring_record(euring_string, source_format, target_format, force=force), encoding="utf-8"
            )
            return
        typer.echo(convert_euring_record(euring_string, source_format, target_format, force=force))
    except ValueError as exc:
        typer.echo(f"Convert error: {exc}", err=True)
        raise typer.Exit(1)


@app.command()
def lookup(
    code_type: str = typer.Argument(..., help="Type of code to look up (ringing_scheme, species, place)"),
    code: str = typer.Argument(..., help="Code value to look up"),
    short: bool = typer.Option(False, "--short", help="Show concise output"),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output (requires --json)"),
):
    """Look up EURING codes (ringing_scheme, species, place)."""
    try:
        if pretty and not as_json:
            typer.echo("Use --pretty with --json.", err=True)
            raise typer.Exit(1)
        if code_type.lower() in {"ringing_scheme", "scheme"}:
            if short:
                result = lookup_ringing_scheme(code)
                if as_json:
                    payload = _with_meta({"type": "ringing_scheme", "code": code, "description": result})
                    typer.echo(json.dumps(payload, indent=2 if pretty else None))
                    return
                typer.echo(f"Ringing Scheme {code}: {result}")
            else:
                details = lookup_ringing_scheme_details(code)
                if as_json:
                    payload = _with_meta({"type": "ringing_scheme", "code": code, **details})
                    typer.echo(json.dumps(payload, default=str, indent=2 if pretty else None))
                    return
                typer.echo(f"Ringing Scheme {code}")
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
                _emit_detail("Name", details.get("country"))
                _emit_detail("Region", details.get("region"))
                _emit_detail_bool("Current", details.get("is_current"))
                _emit_detail("Updated", details.get("updated"))
                _emit_detail("Notes", details.get("notes"))
        else:
            typer.echo(f"Unknown lookup type: {code_type}", err=True)
            typer.echo("Available types: ringing_scheme, species, place", err=True)
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Lookup error: {e}", err=True)
        _emit_glob_hint(code)
        raise typer.Exit(1)


@app.command()
def dump(
    table: list[str] = typer.Argument(None, help="Code table name(s) to dump"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write JSON to a file"),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Write JSON files to a directory"),
    pretty: bool = typer.Option(False, "--pretty", help="Pretty-print JSON output"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    all: bool = typer.Option(False, "--all", help="Dump all code tables (requires --output-dir)"),
):
    """Dump code tables as JSON."""
    if all:
        if table:
            typer.echo("Do not specify table names when using --all.", err=True)
            raise typer.Exit(1)
        if output_dir is None:
            typer.echo("--output-dir is required when using --all.", err=True)
            raise typer.Exit(1)
        output_dir.mkdir(parents=True, exist_ok=True)
        for name in sorted(EURING_CODE_TABLES.keys()):
            data = load_data(name)
            if data is None:
                continue
            payload = _with_meta({"data": data})
            text = json.dumps(payload, indent=2 if pretty else None, default=str)
            output_path = output_dir / f"code_table_{name}.json"
            if output_path.exists() and not force:
                typer.echo(f"File exists: {output_path} (use --force to overwrite)", err=True)
                raise typer.Exit(1)
            output_path.write_text(text, encoding="utf-8")
        return
    if not table:
        typer.echo("Specify one or more code tables, or use --all.", err=True)
        raise typer.Exit(1)
    data_map: dict[str, Any] = {}
    for name in table:
        data = load_data(name)
        if data is None:
            typer.echo(f"Unknown code table: {name}", err=True)
            raise typer.Exit(1)
        data_map[name] = data
    payload: Any = data_map[table[0]] if len(table) == 1 else data_map
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in data_map.items():
            output_path = output_dir / f"code_table_{name}.json"
            if output_path.exists() and not force:
                typer.echo(f"File exists: {output_path} (use --force to overwrite)", err=True)
                raise typer.Exit(1)
            file_payload = _with_meta({"data": data})
            file_text = json.dumps(file_payload, indent=2 if pretty else None, default=str)
            output_path.write_text(file_text, encoding="utf-8")
        return
    payload = _with_meta({"data": payload})
    text = json.dumps(payload, indent=2 if pretty else None, default=str)
    if output:
        output.write_text(text, encoding="utf-8")
    else:
        typer.echo(text)


if __name__ == "__main__":
    app()


def main():
    """Entry point for the CLI."""
    app()


def _has_errors(errors: dict[str, object]) -> bool:
    """Return True when a structured errors payload contains entries."""
    if not isinstance(errors, dict):
        return bool(errors)
    record_errors = errors.get("record", [])
    field_errors = errors.get("fields", [])
    return bool(record_errors) or bool(field_errors)


def _format_error_lines(errors: dict[str, object], *, indent: str) -> list[str]:
    """Format structured errors into human-readable lines."""
    lines: list[str] = []
    record_errors = errors.get("record", []) if isinstance(errors, dict) else []
    field_errors = errors.get("fields", []) if isinstance(errors, dict) else []
    if record_errors:
        lines.append(f"{indent}Record errors:")
        for error in record_errors:
            message = error.get("message", "")
            lines.append(f"{indent}  - {message}")
    if field_errors:
        lines.append(f"{indent}Field errors:")
        for error in field_errors:
            field = error.get("field", "Unknown field")
            message = error.get("message", "")
            meta: list[str] = []
            if "key" in error and error["key"]:
                meta.append(f"key={error['key']}")
            if "index" in error and error["index"] is not None:
                meta.append(f"index={error['index']}")
            if "position" in error and error["position"] is not None:
                meta.append(f"position={error['position']}")
            if "length" in error and error["length"] is not None:
                meta.append(f"length={error['length']}")
            if "value" in error and error["value"] != "":
                meta.append(f'value="{error["value"]}"')
            label = f"{field} ({', '.join(meta)})" if meta else field
            lines.append(f"{indent}  - {label}: {message}")
    return lines


def _emit_detail(label: str, value) -> None:
    """Emit a labeled value when present."""
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    typer.echo(f"  {label}: {text}")


def _emit_detail_bool(label: str, value) -> None:
    """Emit a labeled boolean value when present."""
    if value is None:
        return
    typer.echo(f"  {label}: {'yes' if value else 'no'}")


def _emit_glob_hint(value: str) -> None:
    """Warn when a glob-like string may have been expanded by the shell."""
    if any(char in value for char in "*?[]"):
        return
    if Path(value).exists():
        typer.echo("Hint: your shell may have expanded a wildcard. Quote patterns like 'CH*'.", err=True)


def _with_meta(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach generator metadata to a JSON payload."""
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


def _lines_from_file(file):
    """Read a text file and return lines, exiting on missing files."""
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)
    return lines
