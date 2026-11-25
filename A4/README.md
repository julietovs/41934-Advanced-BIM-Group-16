# A4 – Ventilation verification for Building #2601

**Group 16 · Analyst · Indoor Climate**

## About the tool

Our A2 use case investigates the claim that the rooms in Building #2601 were designed to meet the selected Category II ventilation criterion. The reference identified in A2 is the Building #2601 MEP report, Section 5.1, Table 5, p. 6. Checking this manually requires finding comparable values for each room in the design information.

The tool reads floor area, design occupancy and design supply airflow for each `IfcSpace`. It calculates the required airflow as `7 × N + 0.7 × A` in L/s, where `N` is the design occupancy and `A` is the floor area in m². The result shows the required and design airflow, their difference (design minus required), the inputs and their sources, and the status for each room. The criterion is fixed to the A2 case. The check covers design supply airflow for the selected criterion and room scope. Measurements, indoor thermal conditions and overall regulatory compliance are outside its scope.

| Status | Meaning |
| --- | --- |
| Meets requirement | The design supply airflow meets the calculated minimum. |
| Below requirement | The design supply airflow is below the calculated minimum. |
| Insufficient data | A required value is missing, invalid or lacks a documented source or unit. |
| Review scope | Inclusion has yet to be confirmed. |
| Outside scope | The room was excluded by the user. |

The pass/fail comparison uses unrounded values with a 10⁻⁹ L/s tolerance for floating-point conversion. The IFC stays local and the tool opens it for reading.

## Run locally on Windows

1. In PowerShell, open the repository's `A4` folder and set up the environment.

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Substitute your course-supported Python version if needed. Set `MODEL_PATH` in `settings.py` to your local IFC, for example `r"C:\Users\Student\Downloads\2601.ifc"`. Keep the IFC and any personal path out of Git. You can instead pass the IFC path as a quoted argument after `runall.py`.

2. Run the initial inventory.

   ```powershell
   .\.venv\Scripts\python.exe runall.py
   ```

   The terminal displays the path to the new results folder. Inspect `ifc_fields.csv` to locate the exact fields. Confirm units and meanings using the IFC authoring data or design documentation. In `settings.py`, set `AREA_FIELD`, `OCCUPANCY_FIELD`, `AIRFLOW_FIELD`, and `AIRFLOW_UNIT` to match the IFC. A field uses the pair `("PropertyOrQuantitySet", "PropertyName")`. The default area and occupancy fields are shown in the table below.

3. Copy the generated `room_inputs.csv` to the `A4` folder. Set `include` to `yes` for the rooms covered by the A2 claim and `no` for excluded rooms. Leave unreviewed rooms blank and keep their GlobalIds. Leave the numeric columns blank to use the IFC values. If you supply a documented value in CSV, put its reference in `source`. Use `area_m2` in m² and specify `airflow_unit` for a CSV airflow value. The input accepts semicolon or comma delimiters and decimal commas or decimal points.

4. Run the check and generate the IDS for the confirmed scope.

   ```powershell
   .\.venv\Scripts\python.exe runall.py --data room_inputs.csv --ids
   ```

   This writes `result.json`, `results.csv`, `ifc_fields.csv` and `ventilation_inputs.ids` under a fresh `ventilation_check/results/run-…/` folder. The `--ids` option needs at least one confirmed room and an airflow field mapping. While setting up the IFC mapping, omit `--ids` to run just the analysis. `main.py` supports the same command-line options.

To run the tests with a synthetic IFC:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Connection to A3

A3 imports indoor climate data into the `Custom_RoomClimateData` property set on `IfcSpace` objects using room numbers. If the design occupancy or design supply airflow is available in the A3-enriched IFC, configure those exact field names and the confirmed airflow unit here. Check that the imported data matches the design source. The A4 room selection links to the IFC using the room GlobalId. If occupancy or airflow comes from a separate MEP model, first bring the documented room values into the room IFC via the A3 workflow, or enter them in the scoped CSV with a source reference.

## Advanced Building Design

**Stage C (Detailed Design)** is the proposed stage. Room layouts and design occupancies are known, so HVAC designers can compare planned airflow with the minimum while there is time to revise the design. Architects can confirm room use and areas. BIM analysts can review the source properties, units and results.

| Required information | How the tool reads it |
| --- | --- |
| Room identity | `IfcSpace.GlobalId` matches the scope CSV. The display columns use `Name` and `LongName`. |
| Floor area | Defaults to `Qto_SpaceBaseQuantities.NetFloorArea`. Configure the field to match the model. IFC area must be positive and have a resolvable area unit. |
| Design occupancy | Defaults to `Pset_SpaceOccupancyRequirements.OccupancyNumber`. A documented whole number of zero or more is accepted. |
| Design supply airflow | Set the field and its documented unit (`L/s`, `m3/h` or `m3/s`). Values are converted to L/s. |

The generated IDS specifies field presence on the confirmed `IfcSpace` objects. Run it against the same model in an IDS checker. The Python results cover numeric validity, unit conversion, documented CSV supplements and the airflow criterion. An IDS failure can identify a missing IFC field even if a documented CSV value allowed the calculation.

## Reuse and sharing

With the `A4` folder on the Python import path, use `from ventilation_check.src.main import analyse` and call `analyse(model)` with an open IfcOpenShell model. Provide `room_inputs` to evaluate an agreed scope. Importing the function performs no analysis or export.

For the course canvas, select an approved run, record the model version, code commit, field mapping, scope and limitations, and share a commit-specific link to the approved result in the block's Notes. Save the block and then the shared workspace. Generated runs are local by default. Copy the selected, approved files to a tracked folder when committing them. Use the Speckle template for the course's Speckle component.

Adapted from [Tim McGinley's Week 11 IFC starter, commit 08c3af9](https://github.com/timmcginley/node-comply-template/tree/08c3af93c66e1f2d1d6553fa7023e9c95db1101a).
