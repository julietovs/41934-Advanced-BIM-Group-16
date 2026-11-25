"""Import room data into the open Bonsai model. Save the IFC in Bonsai after running."""

import csv
import math
from collections import defaultdict
from pathlib import Path

from ifcopenshell.api.pset import add_pset, edit_pset
from ifcopenshell.util.element import get_pset

try:
    import bonsai.tool as tool
except ImportError:
    import blenderbim.tool as tool

# Set this to the CSV with documented room data or the supplied demonstration CSV.
CSV_IN = r""
PSET_NAME = "Custom_RoomClimateData"

ROOM_HEADERS = ("Room Number", "room_number")
FIELDS = (
    (("Temperature (°C)", "temperature_c"), "DesignTemperature_C"),
    (("Occupancy", "occupancy"), "DesignOccupancy"),
    (("Supply Airflow (L/s)", "supply_airflow_ls"), "DesignSupplyAirflow_Ls"),
)


def read_import(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        header = stream.readline()
        stream.seek(0)
        delimiter = ";" if ";" in header else ","
        reader = csv.DictReader(stream, delimiter=delimiter)
        headers = reader.fieldnames or []
        room_header = next((name for name in ROOM_HEADERS if name in headers), None)
        fields = [
            (name, prop)
            for names, prop in FIELDS
            for name in [next((candidate for candidate in names if candidate in headers), None)]
            if name is not None
        ]
        if room_header is None or not fields:
            raise ValueError("The CSV must contain Room Number and at least one indoor climate column.")

        room_rows = {}
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Line {reader.line_num}: wrong number of CSV columns.")
            if not any(value.strip() for value in row.values()):
                continue
            room_number = row[room_header].strip()
            if not room_number or room_number in room_rows:
                raise ValueError(f"Line {reader.line_num}: missing or duplicate room number.")
            properties = {}
            for name, prop in fields:
                raw = row[name].strip()
                if not raw:
                    continue
                try:
                    value = float(raw.replace(",", "."))
                except ValueError as error:
                    raise ValueError(f"Line {reader.line_num}: invalid {name} value.") from error
                if not math.isfinite(value):
                    raise ValueError(f"Line {reader.line_num}: invalid {name} value.")
                if prop == "DesignOccupancy":
                    if value < 0 or not value.is_integer():
                        raise ValueError(f"Line {reader.line_num}: occupancy must be a non-negative whole number.")
                    value = int(value)
                if prop == "DesignSupplyAirflow_Ls" and value < 0:
                    raise ValueError(f"Line {reader.line_num}: supply airflow must be non-negative.")
                properties[prop] = value
            room_rows[room_number] = properties
    return room_rows


def main():
    if not CSV_IN.strip():
        raise ValueError("Set CSV_IN to the path of the import CSV.")
    model = tool.Ifc.get()
    if model is None:
        raise RuntimeError("Open an IFC model in Bonsai before running this script.")

    spaces_by_name = defaultdict(list)
    for space in model.by_type("IfcSpace"):
        if space.Name:
            spaces_by_name[space.Name].append(space)

    rows = read_import(Path(CSV_IN).expanduser())
    updated = 0
    for room_number, properties in rows.items():
        if not properties:
            continue
        spaces = spaces_by_name[room_number]
        if len(spaces) != 1:
            print(f"{room_number}: expected one IfcSpace with this Name, found {len(spaces)}.")
            continue
        space = spaces[0]
        existing = get_pset(space, PSET_NAME, psets_only=True, should_inherit=False)
        pset = model.by_id(existing["id"]) if existing else add_pset(model, product=space, name=PSET_NAME)
        edit_pset(model, pset=pset, properties=properties)
        updated += 1

    print(f"Updated {updated} rooms. Save the IFC using Save Project in Bonsai.")


if __name__ == "__main__":
    main()
