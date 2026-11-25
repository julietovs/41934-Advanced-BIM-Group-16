"""Save supporting CSVs and build the IDS for the confirmed room scope."""

import csv

from ifcopenshell.util.element import get_psets

from .main import INPUT_COLUMNS


def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_room_outputs(run_dir, model, result, write_scope_template):
    rooms = result["rooms"]
    write_csv(run_dir / "results.csv", list(rooms[0]), rooms)
    if write_scope_template:
        write_csv(run_dir / "room_inputs.csv", INPUT_COLUMNS, rooms)
    inventory = (
        {
            "GlobalId": space.GlobalId,
            "RoomNumber": space.Name or "",
            "PropertySet": pset,
            "Field": field,
            "RawValue": value,
        }
        for space in model.by_type("IfcSpace")
        for pset, fields in get_psets(space).items()
        for field, value in fields.items()
        if field != "id"
    )
    write_csv(
        run_dir / "ifc_fields.csv",
        ("GlobalId", "RoomNumber", "PropertySet", "Field", "RawValue"),
        inventory,
    )


def build_ids(result):
    from ifctester import ids

    field_mapping = result["field_mapping"]
    airflow_field = field_mapping["design_supply_airflow"]
    selected = [room["GlobalId"] for room in result["rooms"] if room["include"] == "yes"]
    if not selected:
        raise ValueError("Set include=yes for the rooms to include in the IDS.")
    if not airflow_field:
        raise ValueError("Set AIRFLOW_FIELD to the documented IFC property before generating the IDS.")
    schema = result["ifc_schema"]
    if schema == "IFC4X3":
        schema = result["ifc_schema_identifier"]
    if schema not in ("IFC2X3", "IFC4", "IFC4X3_ADD2"):
        raise ValueError(f"Unsupported IDS IFC version: {schema}")

    document = ids.Ids(title="Group 16 | Room data for the A4 ventilation check")
    for gid in selected:
        spec = ids.Specification(
            name=f"Ventilation input fields for room {gid}",
            ifcVersion=[schema],
            minOccurs=1,
            maxOccurs=1,
        )
        spec.applicability = [
            ids.Entity(name="IFCSPACE"),
            ids.Attribute(name="GlobalId", value=gid),
        ]
        spec.requirements = [
            ids.Property(propertySet=pset, baseName=field)
            for pset, field in (field_mapping["area"], field_mapping["occupancy"], airflow_field)
        ]
        document.specifications.append(spec)
    return document
