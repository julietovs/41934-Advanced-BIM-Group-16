"""Local model path and field mapping for the Group 16 A4 check."""
import os

# ---------- SETTINGS ----------

# Set your local IFC model path
BASE_FOLDER = r"C:/Users/Amalie Pallesen/OneDrive - OsloMet/Dokumenter/Msc Sustainable Energy Systems/Semester 3/Advanced BIM"

MODEL_PATH = os.path.join(BASE_FOLDER, "AssignmentAddingCode.ifc")

OUTPUT_FOLDER = os.path.join(BASE_FOLDER, "output")

PSET_NAME = "Custom_RoomClimateData"


# ---------- IFC DATA FIELDS ----------

# Each field is a (property/quantity set name, field name) pair.
AREA_FIELD = ("Qto_SpaceBaseQuantities", "NetFloorArea")

OCCUPANCY_FIELD = ("Pset_SpaceOccupancyRequirements", "OccupancyNumber")

# Set both after checking ifc_fields.csv and the design data.
# A3 fields use Custom_RoomClimateData as the first item of the pair.
AIRFLOW_FIELD = None
AIRFLOW_UNIT = None  # "L/s", "m3/h" or "m3/s"
