from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
from collections.abc import Iterable

SPECIES_CSV_URL = "https://www.euring.org/files/documents/EURING_SpeciesCodes_IOC15_1.csv"
PLACES_CSV_URL = "https://www.euring.org/files/documents/ECPlacePipeDelimited_0.csv"
URLS = {
    "schemes": "https://app.bto.org/euringcodes/schemes.jsp?check1=Y&check2=Y&check3=Y&check4=Y&orderBy=SCHEME_CODE",
    "circumstances": "https://app.bto.org/euringcodes/circumstances.jsp",
}

SCHEME_FIELDS = [
    ["code", "string"],
    ["country", "string"],
    ["ringing_centre", "string"],
    ["is_euring", "bool"],
    ["is_current", "bool"],
    ["updated", "date"],
    ["notes", "string"],
]

SPECIES_FIELDS = [
    ["code", "string"],
    ["name", "string"],
    ["updated", "date"],
    ["notes", "string"],
]

COUNTRY_FIELDS = [
    ["code", "string"],
    ["region", "string"],
    ["place_code", "string"],
    ["is_current", "bool"],
    ["notes", "string"],
    ["updated", "date"],
]

CIRCUMSTANCES_FIELDS = [
    ["code", "string"],
    ["name", "string"],
    ["description", "string"],
    ["updated", "date"],
]


def _field_value(cell, field_type: str):
    if field_type == "bool":
        return bool(cell.find("img", alt="Y"))
    content = cell.string or ""
    content = content.replace("\xad", "")
    if field_type == "string":
        return content.strip()
    if field_type == "date":
        parts = content.strip()
        if parts:
            day, month, year = _parse_table_date_parts(parts)
            return datetime.date(year, month, day)
        return None
    raise ValueError('Parameter `field_type` should be "string", "date", or "bool".')


def _parse_table_date_parts(value: str) -> tuple[int, int, int]:
    if "/" in value:
        parts = value.split("/")
    elif "." in value:
        parts = value.split(".")
    else:
        raise ValueError(f'Invalid date format "{value}".')
    if len(parts) != 3:
        raise ValueError(f'Invalid date format "{value}".')
    part_a, part_b, part_c = parts
    if len(part_a) == 4:
        year = int(part_a)
        month = int(part_b)
        day = int(part_c)
    elif len(part_c) == 4:
        day = int(part_a)
        month = int(part_b)
        year = int(part_c)
    elif len(part_a) == 2 and len(part_c) == 2:
        day = int(part_a)
        month = int(part_b)
        year = _normalize_two_digit_year(int(part_c))
    elif int(part_a) > 31:
        year = int(part_a)
        month = int(part_b)
        day = int(part_c)
    elif int(part_c) > 31:
        day = int(part_a)
        month = int(part_b)
        year = int(part_c)
    else:
        year = _normalize_two_digit_year(int(part_a))
        month = int(part_b)
        day = int(part_c)
    return day, month, year


def _normalize_two_digit_year(year: int) -> int:
    if year < 100:
        year += 2000
        if year > datetime.date.today().year:
            year -= 100
    return year


def _record(cells, fields):
    data = {}
    for index, field in enumerate(fields):
        data[field[0]] = _field_value(cells[index], field[1])
    return data


def _parse_species_csv_date(value: str | None) -> datetime.date | None:
    return _parse_csv_date(value)


def _parse_place_csv_date(value: str | None) -> datetime.date | None:
    return _parse_csv_date(value)


def _parse_csv_date(value: str | None) -> datetime.date | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if "." in text:
        return datetime.datetime.strptime(text, "%d.%m.%Y").date()
    if "/" in text:
        try:
            return datetime.datetime.strptime(text, "%d/%m/%Y").date()
        except ValueError:
            return datetime.datetime.strptime(text, "%d/%m/%y").date()
    raise ValueError(f'Invalid date format "{value}".')


def _fetch(url: str, fields: list[list[str]]) -> list[dict[str, object]]:
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, features="html.parser")
    table = soup.find("div", id="divAll")
    result = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) == len(fields):
            result.append(_record(cells, fields))
    return result


def _fetch_species_csv(url: str) -> list[dict[str, object]]:
    import requests

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    # EURING place CSV has no charset in headers and uses ISO-8859-1 (latin-1).
    text = response.content.decode("latin-1")
    reader = csv.DictReader(text.splitlines())
    result = []
    for row in reader:
        result.append(
            {
                "code": row.get("EURING_Code", ""),
                "name": row.get("Current_Name", ""),
                "updated": _parse_species_csv_date(row.get("Date_Updated")),
                "notes": row.get("Notes", ""),
            }
        )
    return result


def _fetch_places_csv(url: str) -> list[dict[str, object]]:
    import requests

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    try:
        text = response.content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = response.content.decode("latin-1")
    reader = csv.reader(text.splitlines(), delimiter="|")
    rows = list(reader)
    if not rows:
        return []
    result = []
    for row in rows:
        if row and row[0] == "Country":
            continue
        if not row:
            continue
        trimmed = list(row)
        while trimmed and trimmed[-1] == "":
            trimmed.pop()
        core = (trimmed + ["", "", "", "", "", ""])[:6]
        country = core[0]
        region = core[1]
        place_code = core[2]
        is_current = core[3] == "Y"
        notes = core[4].strip()
        updated = core[5]
        result.append(
            {
                "code": country,
                "region": region,
                "place_code": place_code,
                "is_current": is_current,
                "notes": notes,
                "updated": _parse_place_csv_date(updated),
            }
        )
    return result


def fetch_all() -> dict[str, list[dict[str, object]]]:
    """Fetch EURING reference datasets and return them keyed by filename."""
    return {
        "schemes.json": _fetch(URLS["schemes"], SCHEME_FIELDS),
        "species.json": _fetch_species_csv(SPECIES_CSV_URL),
        "places.json": _fetch_places_csv(PLACES_CSV_URL),
        "circumstances.json": _fetch(URLS["circumstances"], CIRCUMSTANCES_FIELDS),
    }


def write_json_files(output_dir: str, datasets: dict[str, Iterable[dict[str, object]]]) -> None:
    """Write reference datasets to JSON files in the target directory."""
    os.makedirs(output_dir, exist_ok=True)
    for filename, data in datasets.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, default=_json_formatter, indent=2, ensure_ascii=False)


def _json_formatter(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    raise TypeError(f"Type {type(value)!r} not serializable")


def main() -> None:
    """CLI entry point for fetching reference datasets."""
    parser = argparse.ArgumentParser(description="Fetch EURING reference data from euringcodes.")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write JSON files (default: current directory).",
    )
    args = parser.parse_args()
    datasets = fetch_all()
    write_json_files(args.output_dir, datasets)


if __name__ == "__main__":
    main()
