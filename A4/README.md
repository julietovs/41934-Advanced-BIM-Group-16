# A4 Tool – Ventilation airflow check for Building #2601

**DTU 41934 Advanced BIM · Group 16 · Analyst · Indoor Climate**

## About the tool

### Problem and claim

The Building #2601 MEP report states that ventilation for offices and meeting rooms was designed using a Category II criterion of 7 L/s per person plus 0.7 L/s per m² of floor area. Our A2 use case turns that design statement into a room-by-room check. A manual review requires matching floor area, design occupancy and design supply airflow from the available model and design information.

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
- The IFC model opened in Bonsai
- Excel (or another CSV viewer)
- The scripts in this repository (Code 1 and Code 2)
- A course-supported Python installation for the automated ventilation check in step 7

### Overview of the scripts

| Script | Purpose | Run in |
| --- | --- | --- |
| Code 1 | Exports room data from the saved IFC to a CSV file so it can be checked before and after import | Blender → Scripting |
| Code 2 | Imports the CSV with indoor climate data into the `IfcSpace` objects | Blender → Scripting |

### Step by step

1. **Run Code 1.** Copy Code 1 into Blender → Scripting and run it. It searches all `IfcSpace` entities for temperature properties and writes the results to a CSV file.

2. **Analyse the generated CSV file.** Open the CSV in Excel. Check which rooms have temperature values and which cells are empty.

3. **Follow the matching path in the BPMN diagram.** If data is missing, follow the path in the [A2 BPMN diagram](../A2/IMG/Ventilation_tool.svg) that matches the situation.

4. **Import the missing data with Code 2.** In our case, the matching path was to import a CSV file with indoor climate data into the IFC model.
   - Prepare the CSV file. The `Room Number` must match `IfcSpace.Name` exactly.
   - Copy Code 2 into Blender → Scripting and run it.
   - Save the IFC file from Bonsai using **Save Project**.

   > **Important:** Code 2 updates the model in memory. Save the IFC file after running the script so that Code 1 can read the changes from the saved file.

5. **Verify the import by running Code 1 again.** Update the IFC input path in Code 1 to point to the file you just saved. Run Code 1 again in Blender → Scripting. Use a different CSV output filename if you want to keep the first export for comparison.

6. **Check the result in Excel.** Open the CSV from the second run of Code 1. Check that the imported values appear on the intended rooms. If a value is still missing, confirm that Code 1 searches for that property in the imported `Custom_RoomClimateData` property set.

7. **Check the values against the selected criteria.**
   - **Indoor temperature:** Where suitable temperature data are available, use the relevant Category II criteria from DS/EN 16798-1.
   - **Ventilation:** Run the [automated ventilation check](#run-the-ventilation-check) on the saved IFC. It calculates `q_required = 7 × N + 0.7 × A [L/s]`, where `N` is the design occupancy and `A` is the floor area in m². Open `results.csv` to see how the documented design supply airflow compares with the calculated requirement for each selected room. Temperature data can be used to demonstrate the import workflow. The ventilation check needs area, design occupancy and documented design supply airflow.

8. **Suggest improvements where the results show a shortfall.**
   - **Passive measures for temperature issues:** solar shading, night ventilation, thermal mass, improved insulation or airtightness, depending on the cause.
   - **Active measures:** adjusted heating or cooling setpoints, additional heating or cooling capacity, or increased supply airflow where the ventilation check identifies a shortfall.

### Code and example data

- [Code 1 – Find indoor temperatures](bonsai/code_1.py)
- [Code 2 – Import the CSV into the model](bonsai/code_2.py)

[IndoorClimate_import.csv](bonsai/IndoorClimate_import.csv) contains mock data for rooms in Building #2601. These values are for demonstrating the workflow. Use documented project values when assessing the actual building.

### Tutorial formats

- Markdown instructions (this README)
- [Video walkthrough](https://youtu.be/Jzvi-XgDxLw)

See the [A3 Teach section](../A3/) for an explanation of how the scripts work.

### Run the ventilation check

If the IFC already contains the necessary room data, you can start here. Use the IFC file containing the `IfcSpace` objects for the rooms you want to assess, and keep it on your computer.

1. **Set up Python.** Open PowerShell in `A4/`. The commands below use Python 3.14.

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. **Inspect the IFC fields.** Set `MODEL_PATH` in [settings.py](settings.py) to the saved IFC, or pass the quoted local path after `runall.py`. The top-level [main.py](main.py) supports the same arguments.

   ```powershell
   .\.venv\Scripts\python.exe runall.py
   ```

   Open `ifc_fields.csv` in the new results folder. Confirm the field names and units for area, design occupancy and design supply airflow. Set each IFC field in `settings.py` as `("SetName", "FieldName")`. Set `AIRFLOW_FIELD` and `AIRFLOW_UNIT` if the supply airflow is stored in the IFC.

3. **Select the rooms.** Copy the generated `room_inputs.csv` to `A4/`. Enter `yes` for offices and meeting rooms in the A2 scope, `no` for excluded rooms, and leave the field blank for rooms still under review. Keep each `GlobalId` unchanged. Clear the numeric cells for values you want the checker to read from the IFC. Enter any documented supplementary values in the CSV together with their `source`. If you enter `design_airflow`, also specify `airflow_unit`.

4. **Run the comparison.** If you left `MODEL_PATH` blank, add the quoted IFC path immediately after `runall.py`. Open `results.csv` in the new results folder and review the airflow values, margin and status.

   ```powershell
   .\.venv\Scripts\python.exe runall.py --data room_inputs.csv
   ```


## Outputs and results

Each run writes to a new folder under `ventilation_check/results/`.

| Output | What it contains |
| --- | --- |
| `result.json` | Machine-readable results, status counts, criterion and field mapping. |
| `results.csv` | One row per IFC room with the inputs, margin, status, sources and notes. |
| `ifc_fields.csv` | Inventory of room properties and quantities used to identify the field mapping. |
| `room_inputs.csv` | Room selection and input template from a run without `--data`. |
| `ventilation_inputs.ids` | Model information requirements for the selected rooms, generated with `--ids`. |

| Status | Interpretation |
| --- | --- |
| Meets requirement | The documented design airflow meets the calculated minimum. |
| Below requirement | The design airflow falls below the calculated minimum. Review the shortfall and the ventilation design. |
| Insufficient data | A required input is missing, invalid or lacks the required source or unit. |
| Review scope | The room's inclusion has yet to be confirmed. |
| Outside scope | The user explicitly excluded the room. |

**Illustrative example.** For a room of 20 m² designed for two occupants, the required airflow is 28 L/s. If the documented design airflow is 25 L/s, the margin is −3 L/s and the room is marked **Below requirement**.

<!-- After checking Building #2601, replace this comment with the IFC version, room scope, status counts, one representative room and a link to an approved result. -->

## IDS

Confirm at least one room with `include=yes` and configure the area, occupancy and design supply airflow fields to match the IFC. If you have left `MODEL_PATH` blank, add the quoted IFC path after `runall.py`.

```powershell
.\.venv\Scripts\python.exe runall.py --data room_inputs.csv --ids
```

The generated `ventilation_inputs.ids` checks that the configured fields are present on the selected rooms. Validate it against the same IFC in an IDS checker such as IfcTester. The numerical airflow comparison is in `results.csv`. A documented CSV value can support the numerical check even when the corresponding field is missing from the IFC.

## Advanced Building Design

**Stage C (Detailed Design).** Room use, floor area and design occupancy can be reviewed alongside the planned ventilation rates while the team can still adjust the design. HVAC designers can investigate airflow shortfalls. Architects can confirm room use and areas, and BIM analysts can check the model properties, units and data sources.

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
| Code 2 cannot match a room | Check the exact value of `IfcSpace.Name` and the CSV's `Room Number` column. |
| Imported values are missing in the second Code 1 export | Save the IFC in Bonsai, check the IFC input path in Code 1 and confirm it reads the imported property names. |
| A CSV will not write or opens in one column | Close it in Excel before rerunning. Use UTF-8 and select the separator used by that CSV. |
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
