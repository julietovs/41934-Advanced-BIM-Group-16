"""Group 16 | A3: ventilation airflow check for IFC spaces.

INSTALL (Command Prompt):
    py -m pip install ifcopenshell
RUN beside your IFC file:
    py main.py "2601.ifc"
    py main.py "2601.ifc" --data "output/room_inputs.csv"
DEMO (fabricated data; no IFC needed):
    py main.py --demo

First run creates output/results.csv, ifc_fields.csv, and a
room_inputs.csv template. Run details and warnings are saved in run_info.txt. Fill the template, save it, then run with --data.
Existing input templates are NEVER overwritten. All paths are relative to the
current working directory. The IFC is read only; no geometric area is computed.

Criterion supplied in A2: MEP report, section 5.1, table 5, p.6:
    required supply airflow [L/s] = 7 * occupants + 0.7 * floor area [m2].
Checks this criterion only, not thermal comfort or measured performance.
Dependencies: Python 3.9+, IfcOpenShell.
"""

import argparse
import csv
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

# 1. SETTINGS: adapt only after inspecting ifc_fields.csv.
PERSON_RATE = 7.0                 # L/s per person; A2 criterion
AREA_RATE = 0.7                   # L/s per m2; A2 criterion
AREA_FIELDS = [
    ("Qto_SpaceBaseQuantities", "NetFloorArea"),
    ("BaseQuantities", "NetFloorArea"),
    ("PSet_Revit_Dimensions", "Area"),
]
OCCUPANCY_FIELD = ("Pset_SpaceOccupancyRequirements", "OccupancyNumber")
# Optional: set this to the exact property containing ROOM DESIGN SUPPLY airflow.
# Example syntax only: ("YourActualPset", "YourActualProperty")
AIRFLOW_FIELD = None
# Unit for the configured airflow property: "L/s", "m3/h", or "m3/s".
# Must be explicitly confirmed from the IFC/property documentation.
AIRFLOW_UNIT = None

INPUT_COLUMNS = ["GlobalId", "RoomNumber", "RoomName", "include",
                 "area_m2", "occupants", "design_airflow", "airflow_unit", "source"]
RESULT_COLUMNS = ["GlobalId", "RoomNumber", "RoomName", "Scope", "Area [m2]",
                  "Occupants", "Required [L/s]", "Design [L/s]", "Margin [L/s]",
                  "Status", "Notes", "Area source", "Occupancy source", "Airflow source"]


def number(value):
    """Accept decimal comma or point; reject blanks, booleans, NaN and infinity."""
    if value is None or isinstance(value, bool) or str(value).strip() == "":
        return None
    try:
        result = float(str(value).strip().replace(",", "."))
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def airflow_lps(value, unit):
    factors = {"l/s": 1.0, "m3/h": 1 / 3.6, "m3/s": 1000.0}
    key = str(unit or "").lower().replace(" ", "").replace("³", "3")
    amount = number(value)
    return amount * factors[key] if amount is not None and key in factors else None


def suggested_scope(name):
    # These are suggestions only. Scope must be confirmed in the input CSV.
    if re.search(r"\b(office|kontor|meeting|conference|møderum|møterom)\b", name.lower()):
        return "Suggested office/meeting room"
    return "Unclassified"


# 2. READ SUPPLEMENTARY DATA, linked only by unique IFC GlobalId.
def read_inputs(path, valid_ids):
    if path is None:
        return {}, []
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        sample = file.read(8192)
        file.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(file, dialect=dialect)
        if not reader.fieldnames or not set(INPUT_COLUMNS).issubset(reader.fieldnames):
            raise ValueError("CSV must contain these headers: " + ", ".join(INPUT_COLUMNS))
        rows = {}
        for row in reader:
            if not any(str(v or "").strip() for v in row.values()):
                continue
            gid = row["GlobalId"].strip()
            if not gid or gid in rows:
                raise ValueError("Missing or duplicate GlobalId in input CSV: " + gid)
            rows[gid] = row
    warnings = ["CSV GlobalId not found in IFC: " + gid for gid in rows if gid not in valid_ids]
    return rows, warnings


# 3. EXTRACT IFC SPACES AND INSPECT PROPERTY / QUANTITY SETS.
def read_ifc(path):
    try:
        import ifcopenshell
        from ifcopenshell.util.element import get_psets
        from ifcopenshell.util.unit import get_property_unit, convert_unit
    except ImportError as exc:
        raise RuntimeError("Install dependencies: py -m pip install ifcopenshell") from exc
    model = ifcopenshell.open(str(path))
    # Target unit in a separate in-memory file; the input model is unchanged.
    target_file = ifcopenshell.file(schema="IFC4")
    square_metre = target_file.create_entity("IfcSIUnit", UnitType="AREAUNIT", Name="SQUARE_METRE")
    records, inventory = [], []
    for space in model.by_type("IfcSpace"):
        psets = get_psets(space, verbose=True)
        record = {"gid": space.GlobalId, "number": space.Name or "",
                  "name": space.LongName or "", "area": None, "occupants": None,
                  "flow": None, "area_source": "", "occupancy_source": "",
                  "flow_source": "", "extraction_notes": []}
        if not record["gid"]:
            raise ValueError("IfcSpace missing GlobalId: #" + str(space.id()))

        def field(pair):
            item = psets.get(pair[0], {}).get(pair[1])
            return item if isinstance(item, dict) and "value" in item else None

        for pset_name, properties in psets.items():
            for key, entry in properties.items():
                if key == "id":
                    continue
                value = entry.get("value") if isinstance(entry, dict) else entry
                unit_text = ""
                if isinstance(entry, dict) and entry.get("id"):
                    try:
                        unit = get_property_unit(model.by_id(entry["id"]), model)
                        unit_text = str(unit) if unit else "Not declared / not resolved"
                    except (RuntimeError, ValueError, TypeError, AttributeError):
                        unit_text = "Could not resolve"
                inventory.append([space.GlobalId, record["number"], pset_name, key,
                                  str(value), unit_text])

        # Do not guess unitless area or fall back from an invalid preferred area.
        for pair in AREA_FIELDS:
            entry = field(pair)
            if entry is None:
                continue
            record["area_source"] = "IFC: " + ".".join(pair)
            try:
                prop = model.by_id(entry["id"])
                unit = get_property_unit(prop, model)
                raw = number(entry["value"])
                if unit is None or getattr(unit, "UnitType", None) != "AREAUNIT" or raw is None:
                    raise ValueError("Missing/invalid area value or area unit")
                record["area"] = convert_unit(raw, unit, square_metre)
            except (RuntimeError, ValueError, TypeError, KeyError, AttributeError) as exc:
                record["extraction_notes"].append("Area unresolved: " + str(exc))
            break
        entry = field(OCCUPANCY_FIELD)
        if entry is not None:
            record["occupants"] = number(entry["value"])
            record["occupancy_source"] = "IFC: " + ".".join(OCCUPANCY_FIELD)
        if AIRFLOW_FIELD:
            entry = field(AIRFLOW_FIELD)
            if entry is not None:
                record["flow"] = airflow_lps(entry["value"], AIRFLOW_UNIT)
                record["flow_source"] = "IFC: " + ".".join(AIRFLOW_FIELD) + "; unit=" + str(AIRFLOW_UNIT)
        records.append(record)
    ids = [r["gid"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate IfcSpace GlobalId values; cannot safely map inputs.")
    return records, inventory


# 4. CHECK ONE ROOM. Keep its identity, inputs and result together.
def evaluate(record, supplemental):
    row = dict(record)
    notes = list(row.get("extraction_notes", []))
    scope = str(supplemental.get("include", "")).strip().lower()
    source = str(supplemental.get("source", "")).strip()
    source_missing = False
    for csv_key, internal, label in [("area_m2", "area", "area_source"),
                                      ("occupants", "occupants", "occupancy_source"),
                                      ("design_airflow", "flow", "flow_source")]:
        raw = supplemental.get(csv_key, "")
        if str(raw or "").strip():
            row[internal] = (airflow_lps(raw, supplemental.get("airflow_unit"))
                             if internal == "flow" else number(raw))
            row[label] = "CSV: " + (source or "SOURCE MISSING")
            source_missing |= not bool(source)
    area, people, flow = row["area"], row["occupants"], row["flow"]
    issues = []
    if area is None or area <= 0:
        issues.append("Missing/invalid floor area (> 0 m2 required)")
    if people is None or people < 0 or not float(people).is_integer():
        issues.append("Missing/invalid design occupancy (whole number >= 0 required)")
    if flow is None or flow < 0:
        issues.append("Missing/invalid supply airflow or unconfirmed unit")
    if source_missing:
        issues.append("Document the source for supplementary numeric inputs")
    required = PERSON_RATE * people + AREA_RATE * area if not any("area" in x or "occupancy" in x for x in issues) else None
    margin = flow - required if flow is not None and flow >= 0 and required is not None else None
    if scope in ("no", "n", "0", "false"):
        status, scope_label = "Outside scope", "Excluded by CSV"
    elif scope not in ("yes", "y", "1", "true"):
        status = "Review scope"
        scope_label = suggested_scope(row["name"] + " " + row["number"])
        notes.append("Set include=yes for confirmed offices/meeting rooms; no for other spaces")
    else:
        scope_label = "Confirmed office/meeting room"
        status = "Insufficient data" if issues else ("Meets requirement" if margin >= 0 else "Below requirement")
    notes.extend(issues)
    return [row["gid"], row["number"], row["name"], scope_label, area, people,
            required, flow, margin, status, "; ".join(notes),
            row["area_source"], row["occupancy_source"], row["flow_source"]]


# 5. WRITE CSV OUTPUTS. Edit input CSV and rerun to update results.
def write_csv_outputs(output, rows, inventory, warnings, model_label):
    with (output / "results.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(RESULT_COLUMNS)
        writer.writerows(rows)
    with (output / "ifc_fields.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["GlobalId", "RoomNumber", "Property / quantity set",
                         "Field", "Raw value", "Resolved unit"])
        writer.writerows(inventory)
    lines = [
        "Group 16 - A3 ventilation check",
        "Generated: " + datetime.now().isoformat(timespec="seconds"),
        "Model: " + model_label,
        "A2 source: MEP report, section 5.1, table 5, p.6 (supplied by group).",
        "The report itself has not been verified by this script.",
        "Required L/s = 7 * design occupants + 0.7 * floor area in m2.",
        "Margin = design supply airflow minus required airflow (L/s).",
        "Confirm scope in room_inputs.csv: include=yes or include=no.",
        "Blank scope = Review scope. Room names are suggestions only.",
        "Supplementary numeric inputs override IFC values and require a source.",
        "CSV area is m2; airflow_unit accepts L/s, m3/h or m3/s.",
        "Blank CSV values leave extracted IFC values unchanged.",
        "Area requires a resolved IFC area unit; no geometry is calculated.",
        "IFC airflow requires configured AIRFLOW_FIELD and AIRFLOW_UNIT.",
        "Zero occupants and zero airflow are accepted; zero area is invalid.",
        "No pass/fail rounding or tolerance is applied.",
        "Outputs are snapshots: edit room_inputs.csv and rerun.",
        "The IFC model is unchanged.",
        "Does not verify thermal comfort, CO2, measured airflow or full standards compliance.",
        "Status counts: " + str(dict(Counter(row[9] for row in rows))),
        "Warnings:",
    ] + (warnings or ["None"])
    (output / "run_info.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def demo_records():
    records, inputs = [], {}
    for gid, name, area, people, flow in [("DEMO-1", "Office", 20, 2, 30),
                                          ("DEMO-2", "Meeting room", 30, 6, 55),
                                          ("DEMO-3", "Office", 15, None, 25)]:
        records.append({"gid": gid, "number": gid, "name": name, "area": area,
                        "occupants": people, "flow": flow, "area_source": "FABRICATED DEMO",
                        "occupancy_source": "FABRICATED DEMO", "flow_source": "FABRICATED DEMO"})
        inputs[gid] = {"include": "yes"}
    return records, inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ifc", nargs="?", help="Path to IFC model")
    parser.add_argument("--data", type=Path, help="Completed supplementary CSV")
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--demo", action="store_true", help="Fabricated example; does not validate your building")
    args = parser.parse_args()
    if args.demo and (args.ifc or args.data):
        parser.error("Use --demo alone, without an IFC or --data")
    if not args.demo and not args.ifc:
        parser.error("Provide an IFC file, or use --demo")
    try:
        if args.demo:
            records, inputs = demo_records()
            inventory, warnings = [], ["FABRICATED DEMO DATA - NOT BUILDING RESULTS"]
            label = "FABRICATED DEMO - NOT BUILDING #2601"
            output = args.output / "demo"
        else:
            records, inventory = read_ifc(args.ifc)
            inputs, warnings = read_inputs(args.data, {r["gid"] for r in records})
            output, label = args.output, str(Path(args.ifc).resolve())
            if not records:
                warnings.append("No IfcSpace found. Select a model containing rooms, often the architectural IFC.")
        output.mkdir(parents=True, exist_ok=True)
        rows = [evaluate(record, inputs.get(record["gid"], {})) for record in records]
        template = output / "room_inputs.csv"
        if not template.exists():
            with template.open("x", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(INPUT_COLUMNS)
                for r in records:
                    writer.writerow([r["gid"], r["number"], r["name"], "", "", "", "", "", ""])
        write_csv_outputs(output, rows, inventory, warnings, label)
        print("Results CSV created:", (output / "results.csv").resolve())
        print("IFC fields CSV created:", (output / "ifc_fields.csv").resolve())
        print("Run information:", (output / "run_info.txt").resolve())
        print("Input template (existing file preserved):", template.resolve())
        print("Status counts:", dict(Counter(row[9] for row in rows)))
        for warning in warnings:
            print("WARNING:", warning)
        if not args.demo:
            print("Confirm scope in CSV: include=yes for offices/meeting rooms; no for other spaces.")
            print("Fill missing inputs + source, then rerun with --data followed by the CSV path.")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print("ERROR:", exc)
        print("Check paths and inputs; close any open output CSV files before rerunning.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
