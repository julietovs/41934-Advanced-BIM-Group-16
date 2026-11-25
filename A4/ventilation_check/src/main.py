"""Read room data and evaluate the Group 16 A2 supply airflow criterion."""

import csv
import math
from collections import Counter

from ifcopenshell.util.element import get_psets
from ifcopenshell.util.unit import convert, get_property_unit

import settings

PERSON_RATE = 7.0  # L/s per person
AREA_RATE = 0.7  # L/s per m²
INPUT_COLUMNS = (
    "GlobalId", "RoomNumber", "RoomName", "include", "area_m2",
    "occupants", "design_airflow", "airflow_unit", "source",
)
FLOW_FACTORS = {"l/s": 1.0, "m3/h": 1 / 3.6, "m3/s": 1000.0}
STATUSES = (
    "Meets requirement", "Below requirement", "Insufficient data",
    "Review scope", "Outside scope",
)


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def airflow_lps(value, unit):
    factor = FLOW_FACTORS.get((unit or "").strip().lower().replace(" ", "").replace("³", "3"))
    amount = number(value)
    if factor is None or amount is None:
        return None
    return number(amount * factor)


def read_inputs(path):
    """Read the scope and optional documented values by IFC GlobalId."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = stream.readline()
        stream.seek(0)
        delimiter = ";" if ";" in header else ","
        reader = csv.DictReader(stream, delimiter=delimiter)
        if not set(INPUT_COLUMNS).issubset(reader.fieldnames or []):
            raise ValueError("Use the headers from the generated room_inputs.csv.")
        rows = {}
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Wrong number of columns on CSV line {reader.line_num}.")
            if not any(value.strip() for value in row.values()):
                continue
            gid = row["GlobalId"].strip()
            if not gid or gid in rows:
                raise ValueError(f"Missing or duplicate GlobalId on CSV line {reader.line_num}.")
            row["include"] = row["include"].strip().lower()
            if row["include"] not in ("", "yes", "no"):
                raise ValueError(f"Use yes, no or blank in include on CSV line {reader.line_num}.")
            rows[gid] = row
    return rows


def read_field(psets, field):
    if field is None:
        return {}
    entry = psets.get(field[0], {}).get(field[1])
    return entry if isinstance(entry, dict) and "value" in entry else {}


def read_area(model, entry):
    value = number(entry.get("value"))
    if value is None:
        return None
    try:
        unit = get_property_unit(model.by_id(entry["id"]), model)
        if unit is None or unit.UnitType != "AREAUNIT":
            return None
        if unit.is_a("IfcSIUnit") and unit.Name == "SQUARE_METRE":
            return number(convert(value, unit.Prefix, unit.Name, None, "SQUARE_METRE"))
        if unit.is_a("IfcConversionBasedUnit"):
            conversion = unit.ConversionFactor
            base = conversion.UnitComponent
            if base.is_a("IfcSIUnit") and base.Name == "SQUARE_METRE":
                in_base_unit = value * conversion.ValueComponent.wrappedValue
                return number(convert(in_base_unit, base.Prefix, base.Name, None, "SQUARE_METRE"))
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
        return None
    return None


def evaluate_room(model, space, extra):
    psets = get_psets(space, verbose=True)
    area_entry = read_field(psets, settings.AREA_FIELD)
    occupancy_entry = read_field(psets, settings.OCCUPANCY_FIELD)
    airflow_entry = read_field(psets, settings.AIRFLOW_FIELD)
    sources = {
        key: "IFC: " + ".".join(field) if entry else None
        for key, field, entry in (
            ("area_source", settings.AREA_FIELD, area_entry),
            ("occupancy_source", settings.OCCUPANCY_FIELD, occupancy_entry),
            ("airflow_source", settings.AIRFLOW_FIELD, airflow_entry),
        )
    }
    values = {
        "area_m2": read_area(model, area_entry),
        "occupants": number(occupancy_entry.get("value")),
        "design_airflow": airflow_lps(airflow_entry.get("value"), settings.AIRFLOW_UNIT),
    }
    source = extra.get("source", "").strip()
    issues = []
    for column, source_key in (
        ("area_m2", "area_source"),
        ("occupants", "occupancy_source"),
        ("design_airflow", "airflow_source"),
    ):
        raw = extra.get(column, "").strip()
        if raw:
            values[column] = (
                airflow_lps(raw, extra.get("airflow_unit"))
                if column == "design_airflow" else number(raw)
            )
            sources[source_key] = f"CSV: {source}" if source else "CSV: source missing"
            if not source:
                issues.append(f"Document the source for {column} in room_inputs.csv.")

    area, people, flow = values["area_m2"], values["occupants"], values["design_airflow"]
    area_valid = area is not None and area > 0
    occupancy_valid = people is not None and people >= 0 and people.is_integer()
    flow_valid = flow is not None and flow >= 0
    if not area_valid:
        issues.append("Floor area missing, invalid or without a resolvable IFC area unit.")
    if not occupancy_valid:
        issues.append("Design occupancy must be a whole number of zero or more.")
    if not flow_valid:
        issues.append("Design supply airflow missing, invalid or without a configured unit.")

    required = number(PERSON_RATE * people + AREA_RATE * area) if area_valid and occupancy_valid else None
    if area_valid and occupancy_valid and required is None:
        issues.append("Calculated airflow is out of range.")
    margin = flow - required if flow_valid and required is not None else None
    scope = extra.get("include", "")
    if scope == "no":
        status = "Outside scope"
    elif scope != "yes":
        status = "Review scope"
    elif issues:
        status = "Insufficient data"
    else:
        meets = margin >= 0 or math.isclose(flow, required, rel_tol=0, abs_tol=1e-9)
        status = "Meets requirement" if meets else "Below requirement"

    return {
        "GlobalId": space.GlobalId,
        "RoomNumber": space.Name or "",
        "RoomName": space.LongName or "",
        "include": scope,
        "area_m2": area,
        "occupants": int(people) if occupancy_valid else None,
        "required_airflow_lps": required,
        "design_airflow_lps": flow if flow_valid else None,
        "margin_lps": margin,
        "status": status,
        **sources,
        "notes": " ".join(issues) if scope != "no" else "",
    }


def analyse(model, *, room_inputs=None):
    """Return JSON-compatible results from an open IFC, without editing it."""
    room_inputs = room_inputs or {}
    spaces = model.by_type("IfcSpace")
    ids = {space.GlobalId for space in spaces}
    if not spaces:
        raise ValueError("No IfcSpace found. Select an IFC that contains the rooms.")
    if len(ids) != len(spaces) or not all(ids):
        raise ValueError("Room GlobalIds must be present and unique.")
    unknown = room_inputs.keys() - ids
    if unknown:
        raise ValueError("GlobalIds in the CSV are missing from this IFC: " + ", ".join(sorted(unknown)))
    rooms = [evaluate_room(model, space, room_inputs.get(space.GlobalId, {})) for space in spaces]
    counts = Counter(room["status"] for room in rooms)
    return {
        "criterion": {
            "source": "Group 16 A2, Building #2601 MEP report, section 5.1, table 5, p. 6",
            "person_rate_lps": PERSON_RATE,
            "area_rate_lps_per_m2": AREA_RATE,
        },
        "ifc_schema": model.schema,
        "ifc_schema_identifier": model.schema_identifier,
        "field_mapping": {
            "area": settings.AREA_FIELD,
            "occupancy": settings.OCCUPANCY_FIELD,
            "design_supply_airflow": settings.AIRFLOW_FIELD,
            "design_supply_airflow_unit": settings.AIRFLOW_UNIT,
        },
        "summary": {status: counts[status] for status in STATUSES},
        "rooms": rooms,
    }
