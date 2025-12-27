from __future__ import annotations

import argparse
import datetime
import json
import os
from collections.abc import Iterable

URLS = {
    "schemes": "https://app.bto.org/euringcodes/schemes.jsp?check1=Y&check2=Y&check3=Y&check4=Y&orderBy=SCHEME_CODE",
    "species": "https://app.bto.org/euringcodes/species.jsp",
    "countries": "https://app.bto.org/euringcodes/place.jsp?inactive=on",
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
            parts = parts.split("/")
            day = int(parts[2])
            month = int(parts[1])
            year = int(parts[0]) + 2000
            if year > datetime.date.today().year:
                year -= 100
            return datetime.date(year, month, day)
        return None
    raise ValueError('Parameter `field_type` should be "string", "date", or "bool".')


def _record(cells, fields):
    data = {}
    for index, field in enumerate(fields):
        data[field[0]] = _field_value(cells[index], field[1])
    return data


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


def fetch_all() -> dict[str, list[dict[str, object]]]:
    return {
        "schemes.json": _fetch(URLS["schemes"], SCHEME_FIELDS),
        "species.json": _fetch(URLS["species"], SPECIES_FIELDS),
        "countries.json": _fetch(URLS["countries"], COUNTRY_FIELDS),
        "circumstances.json": _fetch(URLS["circumstances"], CIRCUMSTANCES_FIELDS),
    }


def write_json_files(output_dir: str, datasets: dict[str, Iterable[dict[str, object]]]) -> None:
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
