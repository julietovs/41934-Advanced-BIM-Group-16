import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ifcopenshell
from ifcopenshell import guid
from ifctester import ids

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import settings
from ventilation_check.src.main import analyse


def create_model():
    model = ifcopenshell.file(schema="IFC4")
    area_unit = model.create_entity("IfcSIUnit", UnitType="AREAUNIT", Name="SQUARE_METRE")
    model.create_entity(
        "IfcProject", GlobalId=guid.new(),
        UnitsInContext=model.create_entity("IfcUnitAssignment", Units=[area_unit]),
    )
    spaces = []
    for index, airflow in enumerate((100.8, 90.0, None, 100.8, 100.8), 1):
        room = model.create_entity("IfcSpace", GlobalId=guid.new(), Name=str(index))
        spaces.append(room)
        quantity = model.create_entity("IfcQuantityArea", Name="NetFloorArea", AreaValue=20.0)
        qset = model.create_entity(
            "IfcElementQuantity", GlobalId=guid.new(), Name="Qto_SpaceBaseQuantities",
            Quantities=[quantity],
        )
        model.create_entity(
            "IfcRelDefinesByProperties", GlobalId=guid.new(),
            RelatedObjects=[room], RelatingPropertyDefinition=qset,
        )
        sets = [("Pset_SpaceOccupancyRequirements", "OccupancyNumber", "IfcInteger", 2)]
        if airflow is not None:
            sets.append(("Custom_RoomClimateData", "TestFlow", "IfcReal", airflow))
        for pset_name, field, data_type, value in sets:
            prop = model.create_entity(
                "IfcPropertySingleValue", Name=field, NominalValue=model.create_entity(data_type, value),
            )
            pset = model.create_entity(
                "IfcPropertySet", GlobalId=guid.new(), Name=pset_name, HasProperties=[prop],
            )
            model.create_entity(
                "IfcRelDefinesByProperties", GlobalId=guid.new(),
                RelatedObjects=[room], RelatingPropertyDefinition=pset,
            )
    return model, spaces


class VentilationTests(unittest.TestCase):
    def test_room_results_and_ids(self):
        model, spaces = create_model()
        first, second, third, fourth, fifth = [room.GlobalId for room in spaces]
        inputs = {gid: {"include": "yes"} for gid in (first, second, third)}
        inputs[fourth] = {"include": "no"}
        before = model.to_string()
        with patch.multiple(
            settings, AIRFLOW_FIELD=("Custom_RoomClimateData", "TestFlow"), AIRFLOW_UNIT="m3/h",
        ):
            result = analyse(model, room_inputs=inputs)
        expected = ["Meets requirement", "Below requirement", "Insufficient data", "Outside scope", "Review scope"]
        self.assertEqual([room["status"] for room in result["rooms"]], expected)
        self.assertEqual(result["rooms"][0]["required_airflow_lps"], 28.0)
        self.assertAlmostEqual(result["rooms"][0]["design_airflow_lps"], 28.0)
        self.assertIsNone(result["rooms"][2]["design_airflow_lps"])
        self.assertEqual(result["rooms"][4]["GlobalId"], fifth)
        self.assertEqual(model.to_string(), before)

        from ventilation_check.src.exports import build_ids

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ventilation_inputs.ids"
            self.assertTrue(build_ids(result).to_xml(str(path)))
            specification = ids.open(str(path), validate=True)
            specification.validate(model)
            self.assertEqual([spec.status for spec in specification.specifications], [True, True, False])

    def test_runner_exports_csv_and_json_in_separate_runs(self):
        model, spaces = create_model()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "example with spaces.ifc"
            model.write(str(source))
            original = source.read_bytes()
            command = [sys.executable, str(ROOT / "runall.py"), str(source), "--results-dir", str(root)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            baseline = next(root.glob("ventilation_check/run-*/room_inputs.csv"))
            with baseline.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, delimiter=";")
                rows = list(reader)
                columns = reader.fieldnames
            rows[0].update(include="yes", design_airflow="100,8", airflow_unit="m3/h", source="Test schedule")
            scope = root / "scope.csv"
            with scope.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
            subprocess.run(command + ["--data", str(scope)], check=True, capture_output=True, text=True)
            outputs = list(root.glob("ventilation_check/run-*/result.json"))
            self.assertEqual(len(outputs), 2)
            verified = next(path for path in outputs if path.parent != baseline.parent)
            result = json.loads(verified.read_text(encoding="utf-8"))
            self.assertEqual(result["summary"]["Meets requirement"], 1)
            self.assertEqual(result["rooms"][0]["GlobalId"], spaces[0].GlobalId)
            self.assertTrue((verified.parent / "results.csv").is_file())
            self.assertTrue((verified.parent / "ifc_fields.csv").is_file())
            self.assertEqual(source.read_bytes(), original)
