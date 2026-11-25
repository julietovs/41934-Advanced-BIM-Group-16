"""Export room data from a saved IFC before or after the Bonsai import."""

import csv
from datetime import datetime
from pathlib import Path

import ifcopenshell
from ifcopenshell.util.element import get_psets

# Set the saved IFC path before each run. After the import, use the IFC saved in Bonsai.
IFC_IN = r""
OUTPUT_FOLDER = Path.home() / "Documents" / "A4_output"
PSET_NAME = "Custom_RoomClimateData"

COLUMNS = (
    ("Temperature (°C)", "DesignTemperature_C", (
        "temperature", "indoor_temperature", "design_temperature",
        "target_temperature", "room_temperature", "setpoint_temperature",
    )),
    ("Occupancy", "DesignOccupancy", (
        "occupancy", "occupants", "number_of_occupants", "occupancy_number",
        "design_occupancy", "people", "number_of_people",
    )),
    ("Supply Airflow (L/s)", "DesignSupplyAirflow_Ls", (
        "supply_airflow", "supply_air_flow", "supply_air", "airflow",
        "air_flow", "design_supply_airflow", "supply_airflow_ls", "ventilation_rate",
    )),
)


def room_values(space):
    psets = get_psets(space, psets_only=True)
    imported = psets.get(PSET_NAME, {})
    existing = {}
    for name, values in psets.items():
        if name == PSET_NAME:
            continue
        for prop, value in values.items():
            if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                existing.setdefault(prop.strip().lower().replace(" ", "_"), value)

    for _, imported_name, aliases in COLUMNS:
        value = imported.get(imported_name)
        if value is None:
            value = next((existing[name] for name in aliases if name in existing), None)
        yield value


def main():
    if not IFC_IN.strip():
        raise ValueError("Set IFC_IN to the path of the saved IFC file.")
    model = ifcopenshell.open(str(Path(IFC_IN).expanduser()))
    spaces = model.by_type("IfcSpace")
    if not spaces:
        raise ValueError("The selected IFC has no IfcSpace objects.")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output = OUTPUT_FOLDER / f"IndoorClimate_{timestamp}.csv"
    with output.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Room Name", "Room Number", *(label for label, _, _ in COLUMNS)])
        for space in spaces:
            writer.writerow([space.LongName or "", space.Name or "", *room_values(space)])

    print(f"Exported {len(spaces)} rooms to {output}")


if __name__ == "__main__":
    main()
