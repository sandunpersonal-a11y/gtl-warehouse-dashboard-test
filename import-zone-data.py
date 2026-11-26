"""Import the Details tab of an Excel workbook into the dashboard snapshot."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import posixpath
import re
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
TEXT_FIELDS = {
    "building": "BUILDING NAME", "floor": "FLOOR LEVEL", "zone": "ZONE",
    "subLocation": "SUB LOCATION", "storeType": "STORE TYPE",
}
NUMBER_FIELDS = {
    "total": "TOTAL AREA", "non": "NON SELLING", "rented": "RENTED",
    "used": "USING", "balance": "BALANCE", "cbm": "CBM",
}


def workbook_rows(path):
    with ZipFile(path) as book:
        workbook = ET.fromstring(book.read("xl/workbook.xml"))
        sheet = workbook.find(f".//{NAMESPACE}sheet[@name='Details']")
        if sheet is None:
            raise ValueError("The workbook must contain a Details tab.")
        relationships = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        target = next(rel.get("Target") for rel in relationships
                      if rel.get("Id") == sheet.get(REL_ID))
        sheet_path = target.lstrip("/") if target.startswith("/") else posixpath.join("xl", target)
        shared = []
        if "xl/sharedStrings.xml" in book.namelist():
            shared = ["".join(node.text or "" for node in item.iter(f"{NAMESPACE}t"))
                      for item in ET.fromstring(book.read("xl/sharedStrings.xml"))]

        root = ET.fromstring(book.read(posixpath.normpath(sheet_path)))
        for row in root.iter(f"{NAMESPACE}row"):
            cells = {}
            for cell in row:
                column = re.match(r"[A-Z]+", cell.attrib["r"]).group()
                value = cell.findtext(f"{NAMESPACE}v", default="")
                kind = cell.get("t")
                if kind == "s":
                    value = shared[int(value)]
                elif kind == "inlineStr":
                    value = "".join(node.text or "" for node in cell.iter(f"{NAMESPACE}t"))
                elif cell.find(f"{NAMESPACE}f") is not None and not value:
                    value = "#UNCALCULATED"
                cells[column] = value.strip()
            yield row.attrib["r"], cells


def import_rows(path):
    sheet = workbook_rows(path)
    for _, cells in sheet:
        headers = {" ".join(value.upper().split()): column for column, value in cells.items()}
        if "BUILDING NAME" in headers:
            break
    else:
        raise ValueError("BUILDING NAME header not found in Details.")
    if "TOTAL AREA" not in headers and "TOTAT AREA" in headers:
        headers["TOTAL AREA"] = headers["TOTAT AREA"]
    missing = (set(TEXT_FIELDS.values()) | set(NUMBER_FIELDS.values())) - headers.keys()
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))

    records = []
    for line, cells in sheet:
        record = {key: cells.get(headers[label], "") for key, label in TEXT_FIELDS.items()}
        if not any(record[key] for key in ("building", "floor", "zone")):
            continue
        if not all(record[key] for key in ("building", "floor", "zone")):
            raise ValueError(f"Row {line}: building, floor and zone are required.")
        record["building"] = record["building"].upper()
        for key, label in NUMBER_FIELDS.items():
            value = cells.get(headers[label], "") or "0"
            try:
                number = float(value.replace(",", ""))
            except ValueError:
                raise ValueError(f"Row {line}: {label} must contain a calculated number.") from None
            if not math.isfinite(number):
                raise ValueError(f"Row {line}: {label} must contain a finite number.")
            record[key] = int(number) if number.is_integer() else number
        record.update(nonSelling=record["non"], utilized=record["used"],
                      available=max(0, record["balance"]), rawAvailable=record["balance"])
        records.append(record)
    if not records:
        raise ValueError("No zone records found in Details.")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate without writing the snapshot")
    args = parser.parse_args()
    try:
        rows = import_rows(args.workbook)
        if args.check:
            print(f"Validated {len(rows)} zone records. Snapshot unchanged.")
            return
        destination = Path(__file__).with_name("zone-data.json")
        snapshot = {"updatedAt": datetime.now(timezone.utc).isoformat(), "rows": rows}
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                delete=False) as output:
            pending = Path(output.name)
            try:
                json.dump(snapshot, output, ensure_ascii=False, indent=2, allow_nan=False)
                output.write("\n")
                output.close()
                pending.replace(destination)
            finally:
                pending.unlink(missing_ok=True)
        print(f"Saved {len(rows)} zone records to {destination.name}.")
    except (BadZipFile, ET.ParseError, KeyError, IndexError, StopIteration, OSError, ValueError) as error:
        parser.exit(1, f"Import failed: {error}\n")


if __name__ == "__main__":
    main()
