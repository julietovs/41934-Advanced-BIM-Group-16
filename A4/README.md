# A4 Tool – Ventilation airflow check for Building #2601

**DTU 41934 Advanced BIM · Group 16 · Analyst · Indoor Climate**

## About the tool

### Problem and claim

The Building #2601 MEP report states that ventilation for offices and meeting rooms was designed using a Category II criterion from DS-EN 16798-2:2019. Our A2 use case turns that design statement into a room-by-room check. A manual review requires matching floor area, design occupancy and design supply airflow from the available model and design information.

Source for the criterion: Building #2601, Part D – MEP report, Section 5.1, Table 5, p. 6. See the [A2 use case](../A2/) and the [A2 BPMN diagram](../A2/IMG/Ventilation_tool.svg).

### What the tool does

The workflow has two parts. The Blender/Bonsai scripts inspect, add and verify room data where needed. The Python checker reads the saved IFC and automatically compares the documented design supply airflow with the calculated minimum for each selected room.

```text
Required airflow [L/s] = 7 × design occupancy + 0.7 × floor area [m²]
Margin [L/s] = design supply airflow − required airflow
```

The result includes the room identifier, inputs and their sources, required and design airflow, margin and status. The assessment applies to the A2 design airflow criterion. Indoor temperature data can demonstrate the Bonsai workflow. The airflow calculation uses area, occupancy and airflow. Thermal comfort, measured performance and overall regulatory compliance are outside the scope of this check.

## Tutorial

### Prerequisites

- Blender with the Bonsai add-on installed
- The original IFC model available locally
- Excel or another CSV viewer
- [Code 1](../A3/Code%201) and [Code 2](../A3/Code%202) from A3
- A course-supported Python installation for the automated ventilation check

### Overview of the scripts

| Script | Purpose | Run in |
| --- | --- | --- |
| [Code 1 – Export room data](../A3/Code%201) | Reads the IFC open in Bonsai and exports available temperature, occupancy and supply airflow values to CSV | Blender → Scripting |
| [Code 2 – Import room data](../A3/Code%202) | Adds room data from CSV to `Custom_RoomClimateData` and writes a new IFC file | Blender → Scripting |

### Step by step

1. **Run Code 1.** Open the original IFC in Bonsai. Copy Code 1 into Blender → Scripting, replace the example `outputFolder` path with a writable folder on your computer and run the script. It saves `IndoorClimate_<timestamp>.csv` and prints the path in the console.
2. **Review the CSV.** Check which rooms are missing design occupancy or supply airflow. Use the [A2 BPMN diagram](../A2/IMG/Ventilation_tool.svg) to identify the relevant path. If the IFC already contains the required data, continue directly to the [ventilation check](#run-the-ventilation-check).
3. **Prepare the import CSV.** The value in `room_number` must match the room's `IfcSpace.Name`. Use the following column names for Code 2. Leave any unavailable values blank.

   ```csv
   room_number,occupancy,supply_airflow_ls,temperature_c
   ```

   To try the workflow with the [A3 example CSV](../A3/IndoorClimate_import.csv), make a local copy and rename the columns as shown below. You can keep the `Room Name` column. Match the `DELIMITER` setting in Code 2 to the separator in your CSV. The example contains mock data. Use documented design values for the actual building check.

   | A3 example column | Code 2 expects |
   | --- | --- |
   | Room Number | `room_number` |
   | Occupancy | `occupancy` |
   | Supply Airflow (L/s) | `supply_airflow_ls` |
   | Temperature (°C) | `temperature_c` |

4. **Run Code 2.** Set `IFC_IN` to the original IFC, `CSV_IN` to the prepared CSV and `IFC_OUT` to a different local IFC filename. Run the script in Blender → Scripting. It writes the updated model to `IFC_OUT`.
5. **Verify the import with Code 1.** Open the IFC written by Code 2 in Bonsai and run Code 1 again. Compare the new CSV with the first export. Code 1 uses `Custom_RoomClimateData` as a fallback for each missing value. A value found in another property set, including `0`, can take precedence over the imported value. If the CSV still shows an old value, check the imported property directly on the room in Bonsai.


See the [A3 Teach section](../A3/) and the [video walkthrough](https://youtu.be/Jzvi-XgDxLw) for the tutorial background.



## Information Delivery Specification (IDS)

An IDS is a machine-readable checklist for the information an IFC model should contain. Our room data IDS checks whether the selected room has the properties imported by Code 2 in `Custom_RoomClimateData`.

| Code 2 CSV column | IFC property checked by the IDS |
| --- | --- |
| `temperature_c` | `DesignTemperature_C` |
| `occupancy` | `DesignOccupancy` |
| `supply_airflow_ls` | `DesignSupplyAirflow_Ls` |

1. Open the IFC written to `IFC_OUT` and the IDS in an IDS checker such as IfcTester.
2. Run the validation. The example IDS selects room `113` by its `IfcSpace.Name`, matching the `room_number` column used by Code 2. It expects all three properties for this room because its row in the A3 example CSV contains all three values.
3. For another room, change the applicability value for `Name` in the IDS to its exact room number. Add a specification for each additional room you want to validate. If a CSV field was intentionally left blank, omit its property requirement for that room.

To verify the imported numbers, compare the CSV values with the room properties in Bonsai. Code 1 provides an additional export for review.

## Advanced Building Design

**Stages C (Integrate) and D (Detail).** In Stage C, the workflow supports coordination between architecture and building services by identifying missing room data and importing documented indoor climate information into the IFC model. In Stage D, the IDS can be applied to the final IFC model to verify that the expected properties are present on the selected rooms before delivery.

| Required information | Where the checker gets it |
| --- | --- |
| Room identity and scope | `IfcSpace.GlobalId` links each room to the analysis CSV. The user confirms which rooms are in scope. |
| Floor area | Defaults to `Qto_SpaceBaseQuantities.NetFloorArea`. IFC area must have a resolvable area unit. |
| Design occupancy | Defaults to `Pset_SpaceOccupancyRequirements.OccupancyNumber`. Supply a whole number of zero or more. |
| Design supply airflow | Configure the room property and its documented unit, such as `L/s`, `m3/h` or `m3/s`. The checker converts it to L/s. |

If the required data is in separate design documentation or another model, associate the documented values with the correct rooms through the Bonsai import or the analysis CSV.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Code 2 cannot match a room | Check the exact value of `IfcSpace.Name` and the CSV's `room_number` column. |
| Imported values are missing in the second Code 1 export | Open the IFC written to `IFC_OUT` in Bonsai. Check the imported property set on the room if another property set supplies the value shown in the CSV. |
| A CSV will not write or opens in one column | Check that `outputFolder` is writable and close the CSV in Excel before rerunning. Use UTF-8 and select the separator used by that CSV. |
| The checker finds no rooms | Select an IFC containing `IfcSpace` objects. |
| All rooms show `Review scope` | Set the room scope in `room_inputs.csv` and pass the file with `--data`. |
| A selected room shows `Insufficient data` | Read its notes in `results.csv` and check the property mapping, units or CSV references. |
| `NameError: csv is not defined` in Blender | Copy the complete script, including the imports. |

## Testing, reuse and sharing

From `A4/`, run the tests against a synthetic IFC:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Other Python tools can import `analyse` from `ventilation_check.src.main` and call it with an open IfcOpenShell model and the agreed room scope. The JSON output includes GlobalIds and airflow fields in L/s for downstream use.

For a shared result, record the IFC version, code commit, field mapping, room scope and limitations. Share an approved result through a commit-specific link in the team canvas block's Notes and save the shared workspace. Keep generated local runs and IFC files out of Git. See the [changelog](CHANGELOG.md) for changes to the tool.

## Licence and acknowledgement

The Group 16 code is released under the MIT License. Adapted from [Tim McGinley's Week 11 IFC starter, commit 08c3af9](https://github.com/timmcginley/node-comply-template/tree/08c3af93c66e1f2d1d6553fa7023e9c95db1101a). See the [A4 assignment brief](https://timmcginley.github.io/41934/Assignments/A4.html).
