"""Local model path and field mapping for the Group 16 A4 check."""

# Set locally or pass a path after runall.py. Keep your local path out of Git.
MODEL_PATH = r""

# Each field is a (property/quantity set name, field name) pair.
AREA_FIELD = ("Qto_SpaceBaseQuantities", "NetFloorArea")
OCCUPANCY_FIELD = ("Pset_SpaceOccupancyRequirements", "OccupancyNumber")

# Set both after checking ifc_fields.csv and the design data. A3 fields
# use Custom_RoomClimateData as the first item of the pair.
AIRFLOW_FIELD = None
AIRFLOW_UNIT = None  # "L/s", "m3/h" or "m3/s"
