from pathlib import Path

base_path = Path(__file__).parent
base_data_path = Path(base_path / Path("data"))

# EXCEL SOURCES RAW FILES
# Turbines_20231027.xlsx


# format conversion
wind_extract_file = base_data_path / Path("1_csv/thewindpower_technical_database.csv")
# raw converted market file (broken encoding)
raw_market_file = base_data_path / Path("1_csv/thewindpower_database.csv")
# fixed market file (fixed encoding)
fixed_market_file = base_data_path / Path("1_csv/thewindpower_database_fixed.csv")

preparation_dir = base_data_path / "2_prep"

# after several filters
filtered_market_file = preparation_dir / "thewindpower_database_filtered.csv"
# turbine table filtered (columns)
filtered_turbine_file = preparation_dir / "thewindpower_technical_database_filtered.csv"

# ## FINAL FILE
final_dir = base_data_path / "3_final_files"
final_dir.mkdir(exist_ok=True)
result_file = final_dir / "output.csv"
#

# MORE PREPARATION
# power_fitting
power_fitting_params_dir = preparation_dir / "power_fit_curve_params"
global_power_fitting_params_file = power_fitting_params_dir / "GLOBAL.json"
###
# matching
matching_dir = preparation_dir / "matching"
all_manufacturers_file = matching_dir / "all_manufacturers.json"
exact_match_lookup_file = matching_dir / "exact_match_lookup.json"
# just to check
manuf_power_turbine_match_file_complete = (
    matching_dir / "manuf_power_most_common_turbine_complete.json"
)
manuf_power_turbine_match_file = matching_dir / "manuf_power_most_common_turbine.json"

# gearbox generator
gearbox_generator_dir = preparation_dir / "gearbox_generator"
gearbox_generator_probability_file = (
    gearbox_generator_dir / "gearbox_generator_probability.json"
)
gearbox_generator_split_probability_file = (
    gearbox_generator_dir / "gearbox_generator_split_probability.json"
)
GEARBOX_GENERATOR_BUCKET_SIZE = 1000

# location
location_dir = preparation_dir / "location"
location_file = location_dir / "location.json"
full_location_responses_file = location_dir / "full_location_responses.json"
location_errors_file = location_dir / "location_errors.json"
location_errors_info_file = location_dir / "location_errors.csv"
LOCATION_BASE_QUERY = "https://nominatim.openstreetmap.org/search?q={}&format=json"
location_fixing_file = location_dir / "location_fixing.json"

# hub height
hub_height_dir = preparation_dir / "hub_height"
global_hh_power_fitting_params_file = power_fitting_params_dir / "GLOBAL.json"


WINDPARK_MARKET_DELIMITER = ","
TURBINE_LOOKUP_DELIMITER = ","

DO_POWER_MATCH_FOR_EXACT_MATCH: bool = True


TURBINE_RELEVANT_COLUMNS = [
    "ID",
    "Name",
    "Manufucturer",
    "Rated power",
    "Rotor diameter",
    "Minimum hub height",
    "Maximum hub height",
    "Gear box",
    "Generators",
]

TURBINE_RENAME_COLUMNS = {
    "ID (#ND = no data)": "ID",
    "Rated power (kW)": "Rated power",
    "Rotor diameter (m)": "Rotor diameter",
    "Minimum hub height (m)": "Minimum hub height",
    "Maximum hub height (m)": "Maximum hub height",
}

WINDPARK_RELEVANT_COLUMNS = [
    "ID",
    "ISO code",
    "Country",
    "State code",
    "Area",
    "City",
    "Name",
    "2nd name",
    "Latitude",
    "Longitude",
    "Location accuracy",
    "Offshore Shore distance",
    "Manufacturer",
    "Turbine",
    "Hub height",
    "Number of turbines",
    "Total power",
    "Commissioning date",
    "Status",
    "Decommissioning date",
]


FN_ID = "ID"
FN_PARK_NAME = "Wind park name"
FN_POWER = "Wind park power"
FN_LOCATION = "Park location"
FN_COMMISSIONING_DATE = "Commissioning date"
FN_STATUS = "Status"
FN_DECOMMISSIONING_DATE = "Decommissioning date"
FN_LATITUDE = "Latitude"
FN_LONGITUDE = "Longitude"
FN_ORIG_LOC_NAME = "location city/area"
FN_RESOLVED_LOC_NAME = "resolved location name"
FN_RESOLVED_ADDRESS_TYPE = "resolved address type"
FN_NUM_TURBINES = "Number of turbines"
FN_MANUFACTURER = "Manufacturer"
FN_TURBINE_MODEL = "Turbine model"
FN_HUB_HEIGHT = "Hub height"
FN_ROT_DIAMETER = "Rotor diameter"
FN_TURBINE_POWER = "Turbine power"
FN_GEARBOX_GENERATOR = "Gearbox generator"
FN_IS_OFFSHORE = "Is offshore"
FN_OFFSHORE_SHORE_DISTANCE = "Offshore shore distance"

FN_X_TURBINE_MATCH = "Turbine match strategy"
FN_X_GEARBOX_GENERATOR_PROB = "gearbox_gen %"
FN_X_GENERATOR_PROB = "generator %"

FINAL_COLUMNS = [
    FN_ID,
    FN_PARK_NAME,
    FN_POWER,
    FN_LOCATION,
    FN_COMMISSIONING_DATE,
    FN_STATUS,
    FN_DECOMMISSIONING_DATE,
    FN_LATITUDE,
    FN_LONGITUDE,
    FN_ORIG_LOC_NAME,
    FN_RESOLVED_LOC_NAME,
    FN_RESOLVED_ADDRESS_TYPE,
    FN_MANUFACTURER,
    FN_TURBINE_MODEL,
    FN_NUM_TURBINES,
    FN_HUB_HEIGHT,
    FN_ROT_DIAMETER,
    FN_TURBINE_POWER,
    FN_GEARBOX_GENERATOR,
    FN_IS_OFFSHORE,
    FN_OFFSHORE_SHORE_DISTANCE,
    FN_X_GEARBOX_GENERATOR_PROB,
    FN_X_GENERATOR_PROB,
]

simple_copy_pairs = {
    "ID": FN_ID,
    "Name": FN_PARK_NAME,
    "Turbine": FN_TURBINE_MODEL,
    "ISO code": FN_LOCATION,
    "Commissioning date": FN_COMMISSIONING_DATE,
    "Status": FN_STATUS,
    "Decommissioning date": FN_DECOMMISSIONING_DATE,
    "Manufacturer": FN_MANUFACTURER,
    "Total power": FN_POWER,
    "TBN_Rotor diameter": FN_ROT_DIAMETER,
    "TBN_Rated power": FN_TURBINE_POWER,
    "Number of turbines": FN_NUM_TURBINES,
}
