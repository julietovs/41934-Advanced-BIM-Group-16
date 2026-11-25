# A3 TEACH - Importing Indoor Climate Data into an IFC Model with Blender/Bonsai
This repository documents a tutorial for importing room-level indoor climate data from a CSV file into IfcSpace entities using Python in Blender/Bonsai, and for 
verifying that the data is stored in the model. The tutorial builds on the data limitations identified in A1 and the ventilation use case developed in A2 for Building #2601.

## Summary
**Title:** Import indoor climate data from CSV into IFC spaces

**Description:** Check an IFC model for missing indoor temperatures, import a CSV with indoor conditions into IfcSpaces using Python in Blender/Bonsai, verify that the
data is stored in the model, and compare the values with Danish requirements.

## A3a: About the group
- Group number: 16
- Total Python coding confidence score: 3
- Focus area: Indoor Climate
- Role: Analyst
- BIM use: Indoor Climate Analysis
- Selected building: #2601

## A3b: Identify the learning need
### What is the learning need?
In A1 we found that temperature-related properties in the IFC model were missing or contained zero values, which prevented verification of the report's thermal comfort claim. 
In A2 we proposed a ventilation tool that depends on supplementary room data (occupancy and airflow) linked to IfcSpaces. Both depend on the same skill: getting external room-level 
data into an IFC model and checking that it was stored correctly.

### Who needs it?
Students in the Indoor Climate focus area, and other analysts who need to add data from external sources (CSV, Excel, schedules) to rooms in an IFC model.

### Why is it relevant?
Models often arrive with incomplete room data. Being able to import supplementary data in a traceable way, and to verify the result, makes later checks (thermal comfort, ventilation, energy) 
possible and repeatable.

## A3c: Learning objectives
After completing this tutorial, the student can:
1. Use Python in Blender/Bonsai to search an IFC model for indoor temperature properties and export the result to CSV.
2. Prepare a CSV file that can be matched to `IfcSpace` entities.
3. Import values from a CSV into an IFC property set and save the result in the model.
4. Verify that the imported data exists in the saved IFC file.
5. Compare the values with Danish requirements and suggest improvements if they are not met.

## A3d: Walkthrough
This section provides a detail walkthrough of how the Room Climate Export(Code 1) and Import(Code 2) tool works internally.

### Overview of the tool
The tool is comprimised of:
- Code1, which runs inside Blender/bOnsai, reads the indoor climate data from the open IFC   model and writes it to a CSV file.
- Code2, which reads a CSV file with design values per room and writes them into the IFC model as a property set.

Together they make it possible to get room data into the model, and to get a quick overview of which rooms have data and which do not. 

### Supported properties
Three properties are handled per room (`IfcSpace`):

- **TEMPERATURE** (°C)
- **OCCUPANCY** (number of people)
- **SUPPLY_AIRFLOW** (L/s)

In the IFC model the imported values are stored in the property set `Custom_RoomClimateData`:

| Value | Property name in the model |
|---|---|
| Occupancy | `DesignOccupancy` |
| Supply airflow | `DesignSupplyAirflow_Ls` |
| Temperature | `DesignTemperature_C` |

### Workflow
1. Run Code1 to check for existing data in the `Ifc file`. 
2. Run the import script. It reads the CSV, matches each row to an `IfcSpace` by its name, and saves a new IFC file with the data added.
3. Open the new IFC file in Bonsai
4. Run the export script in the Blender Scripting workspace. It writes a CSV with one row per room, and prints a summary.


## Function Deep-Dive

### Code 1

#### Getting the model

Uses the IFC model that is open in Bonsai, so no file path is needed.

```python
try:
    import bonsai.tool as tool        # Bonsai (current name)
except ImportError:
    import blenderbim.tool as tool    # older BlenderBIM versions

# the model that is open in Bonsai
model = tool.Ifc.get()
if model is None:
    raise RuntimeError("No IFC model is open in Bonsai. Open AssignmentAddingCode.ifc first.")
```

- Falls back to the older `blenderbim` module name if `bonsai` is not available.
- Stops with a clear message if no model is open.
- Because it reads the live model, unsaved changes are included.

#### Settings and search names

Defines the output folder, the fallback property set, and the property names to look for.

```python
outputFolder = r"C:/.../Advanced BIM/output"
psetName = "Custom_RoomClimateData"

tempNames = ["temperature", "indoor_temperature", "design_temperature",
             "target_temperature", "room_temperature", "setpoint_temperature"]
occNames = ["occupancy", "occupants", "number_of_occupants", "occupancy_number",
            "design_occupancy", "people", "number_of_people"]
airNames = ["supply_airflow", "supply_air_flow", "supply_air", "airflow",
            "air_flow", "design_supply_airflow", "supply_airflow_ls", "ventilation_rate"]
```

- Names are written in lower case, with underscores instead of spaces.
- If the model uses other names, add them to the lists.

#### Output file

Creates a timestamped CSV file and writes the header row.

```python
os.makedirs(outputFolder, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outputFile = "{}/IndoorClimate_{}.csv".format(outputFolder, stamp)

try:
    file = open(outputFile, "w", newline="", encoding="utf-8-sig")
except PermissionError:
    # e.g. OneDrive sync, or the file is open in Excel
    outputFile = os.path.expanduser("~/Documents/IndoorClimate_{}.csv".format(stamp))
    file = open(outputFile, "w", newline="", encoding="utf-8-sig")
```

- The timestamp means earlier results are never overwritten.
- If the folder cannot be written to, for example because OneDrive is syncing or the file is open in Excel, the file is saved in `~/Documents` instead.

#### Searching each room's own property sets

Loops through every `IfcSpace`, then through its property sets and single-value properties.

```python
for space in model.by_type("IfcSpace"):
    temperature = None
    occupancy = None
    airflow = None
    customData = {}

    for rel in space.IsDefinedBy:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        pset = rel.RelatingPropertyDefinition
        if not hasattr(pset, "is_a") or not pset.is_a("IfcPropertySet"):
            continue

        for prop in pset.HasProperties:
            if not prop.is_a("IfcPropertySingleValue") or prop.NominalValue is None or prop.Name is None:
                continue
            value = prop.NominalValue.wrappedValue
            name = prop.Name.lower().replace(" ", "_")

            if pset.Name == psetName:
                customData[prop.Name] = value
            elif name in tempNames:
                temperature = value
            elif name in occNames:
                occupancy = value
            elif name in airNames:
                airflow = value
```

- Only `IfcPropertySingleValue` properties with a value are used.
- The property name is made lower case and spaces become underscores, then compared to the search lists.
- Values in `Custom_RoomClimateData` are not used right away. They are stored in `customData` as a fallback.

#### Fallback to the custom property set

Uses the imported values for anything that was not found in the room's own property sets.

```python
if temperature is None:
    temperature = customData.get("DesignTemperature_C")
if occupancy is None:
    occupancy = customData.get("DesignOccupancy")
if airflow is None:
    airflow = customData.get("DesignSupplyAirflow_Ls")
```

- A value in the room's own property sets always has priority over the imported value.
- This is what makes the same script work both **before and after** the import.

#### Writing the rows and the summary

Writes one row per room, prints it, and counts how many rooms have each value.

```python
writer.writerow([space.LongName or "", space.Name or "",
                 temperature, occupancy, airflow])

print('\t# {:3} | {:8} | {:6} | {:6} | {}'.format(
    count, space.Name or "", str(temperature), str(occupancy), str(airflow)))
```

- Rooms without any values still get a row, with empty cells.
- At the end the script prints the number of rooms, and how many have a temperature, occupancy and supply airflow.
- A count of zero for a value usually means the property names in the model are not in the search lists yet.

### Code 2 - Importing CSV file

#### Settings

Defines the files, the CSV delimiter and the name of the property set.

```python
IFC_IN  = r"C:/.../AssignmentAddingCode.ifc"
IFC_OUT = r"C:/.../AssignmentAddingCode_climate.ifc"   # save as a NEW file
CSV_IN  = r"C:/.../room_climate.csv"
DELIMITER = ","        # Danish Excel often exports ";" and decimal commas!
PSET_NAME = "Custom_RoomClimateData"
```

- The output is saved as a new file, so the original model is never overwritten.
- `DELIMITER` must be changed to `";"` if the CSV was exported from Danish Excel.

#### Loading the model and collecting the rooms

Opens the IFC file and builds a dictionary that links each room name to its `IfcSpace`.

```python
model = ifcopenshell.open(IFC_IN)
spaces = {s.Name: s for s in model.by_type("IfcSpace") if s.Name}
```

- Spaces without a `Name` are skipped.
- This gives a fast lookup by room number, for example `spaces["1.02"]`.
- If two spaces share the same name, the last one is used.

#### to_float

Converts a text value from the CSV to a number.

```python
def to_float(text):
    """Return float or None for empty/invalid values (never guess a value)."""
    try:
        return float(str(text).strip().replace(",", "."))
    except ValueError:
        return None
```

- Removes whitespace and replaces a decimal comma with a decimal point, so `"21,5"` becomes `21.5`.
- Returns `None` for empty or invalid values instead of guessing or crashing.

#### Reading the CSV and matching the rooms

Loops through every row of the CSV and finds the matching room.

```python
with open(CSV_IN, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter=DELIMITER):
        key = row["room_number"].strip()
        space = spaces.get(key)
        if space is None:
            report.append((key, "no IfcSpace with this Name"))
            continue
```

- `utf-8-sig` removes the invisible BOM character that Excel often adds.
- `csv.DictReader` reads each row as a dictionary, using the column headers as keys.
- A row with a room number that does not exist in the model is added to `report` and skipped.

#### Converting the values and recording problems

Converts the three values and notes which ones are missing.

```python
values = {
    "DesignOccupancy": to_float(row["occupancy"]),
    "DesignSupplyAirflow_Ls": to_float(row["supply_airflow_ls"]),
    "DesignTemperature_C": to_float(row["temperature_c"]),
}
missing = [k for k, v in values.items() if v is None]
if missing:
    report.append((key, f"missing/invalid: {missing}"))
```

- The dictionary keys are the property names used in the IFC model.
- Values that could not be converted are listed in `report`.

#### Writing the property set

Adds the valid values to the room.

```python
props = {k: v for k, v in values.items() if v is not None}
if props:
    pset = ifcopenshell.api.pset.add_pset(model, product=space, name=PSET_NAME)
    ifcopenshell.api.pset.edit_pset(model, pset=pset, properties=props)
```

- Only valid values are written, so a room with a bad temperature still gets its occupancy and airflow.
- If a room has no valid values, no property set is created.

#### Saving and reporting

Saves the model as a new file and prints the problems found.

```python
model.write(IFC_OUT)

for key, msg in report:
    print(f"{key}: {msg}")
```

- Example output: `2.14: no IfcSpace with this Name` or `1.03: missing/invalid: ['DesignTemperature_C']`.

---

---

### Known Limitations

- The room number in the CSV must match the `IfcSpace` name exactly.
- If the same room appears twice in the CSV, the import script adds the property set twice. Depending on the IfcOpenShell version, this may create a duplicate.
- The export only searches normal property sets (`IfcPropertySingleValue`). Values stored in quantity sets (`IfcElementQuantity`) are not found.
- The import script saves a separate IFC file, so Bonsai's open model does not receive the new values until the new file is opened.



## A3h: Software Licence
The code in this tutorial is released under the MIT License, in line with A2. See the license in MIT License.
