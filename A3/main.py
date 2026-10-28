                    "type": "cell", "criteria": "equal to", "value": '"' + status + '"',
                    "format": book.add_format({"bg_color": color})})
        fields = book.add_worksheet("IFC fields")
        fields.write_row(0, 0, ["GlobalId", "RoomNumber", "Property / quantity set", "Field", "Raw value", "Resolved unit"], header)
        for index, row in enumerate(inventory, 1):
            fields.write_row(index, 0, row)
        fields.set_column(0, 1, 25)
        fields.set_column(2, 5, 48)
        fields.freeze_panes(1, 2)
        if inventory:
            fields.autofilter(0, 0, len(inventory), 5)
        info = book.add_worksheet("Read me")
        lines = ["Group 16 - A3 ventilation check", "Generated: " + datetime.now().isoformat(timespec="seconds"),
                 "Model: " + model_label, "A2 source: MEP report, section 5.1, table 5, p.6 (supplied by group).",
                 "The report itself has not been verified by this script.",
                 "Required L/s = 7 * design occupants + 0.7 * floor area in m2.",
                 "Margin = design supply airflow minus required supply airflow (L/s).",
                 "Scope is confirmed in CSV by GlobalId: include=yes or include=no.",
                 "Blank scope = Review scope, regardless of room name suggestions.",
                 "CSV numeric values override IFC values and must have a documented source.",
                 "CSV area is m2; airflow_unit accepts L/s, m3/h or m3/s. Decimal comma is accepted.",
                 "Blank CSV values leave extracted IFC values unchanged; no undocumented defaults are inserted.",
                 "Area is converted only when its IFC unit can be resolved. No geometry is calculated.",
                 "IFC design supply airflow is read only if AIRFLOW_FIELD and AIRFLOW_UNIT are configured.",
                 "Zero occupants and zero airflow are accepted as inputs; zero area is invalid.",
                 "No pass/fail rounding or tolerance is applied; visible numbers are rounded for display only.",
                 "Inspect IFC fields and confirm property meanings, room scope and unit conventions before use.",
                 "Results are static snapshots. Edit input CSV and rerun, rather than editing Excel outputs.",
                 "Does not verify thermal comfort, CO2 concentration, actual airflow or complete standards compliance.",
                 "Warnings:"] + (warnings or ["None"])
        for i, line in enumerate(lines):
            info.write(i, 0, line)
        info.set_column(0, 0, 125)


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
        write_excel(output / "ventilation_results.xlsx", rows, inventory, warnings, label)
        with (output / "results.csv").open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(RESULT_COLUMNS)
            writer.writerows(rows)
        print("Excel created:", (output / "ventilation_results.xlsx").resolve())
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
        print("Check paths and inputs; close any open output Excel file before rerunning.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
