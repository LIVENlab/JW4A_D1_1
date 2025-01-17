import re
from typing import Any

from const import (
    FN_HUB_HEIGHT,
    FN_IS_OFFSHORE,
    FN_LATITUDE,
    FN_LONGITUDE,
    FN_OFFSHORE_SHORE_DISTANCE,
    FN_ROT_DIAMETER,
    FN_TURBINE_POWER,
    location_file, FN_ORIG_LOC_NAME, FN_RESOLVED_LOC_NAME, FN_RESOLVED_ADDRESS_TYPE,
)
from src.helper import load_json
from src.prep.prepare_hub_height import fit_hh_value
from src.prep.prepare_power_fit import fit_value


class InvalidWindparkException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


location_lookup: dict[str, dict[str, float]]
hub_height_data: dict[str, float]
hub_height_average: float


def load_data():
    global location_lookup, hub_height_data, hub_height_average
    location_lookup = load_json(location_file)  # type: ignore


def turbine_power_strategy(row: dict[str, Any]):
    """
    replace the turbine power with the exact power if it is available
    """
    exact_power = row.get("TBN_Rated power")
    if exact_power:
        return {FN_TURBINE_POWER: row["TBN_Rated power"]}
    return {FN_TURBINE_POWER: row.get(FN_TURBINE_POWER)}


def hub_height_strategy(row: dict[str, Any]):
    height = str(row["Hub height"])
    if height != "nan":
        return {FN_HUB_HEIGHT: height}
    else:
        fitted_value = fit_hh_value(row[FN_TURBINE_POWER])
        return {FN_HUB_HEIGHT: round(fitted_value, 2)}


def estimate_gentype_rotdia_of_missturbines(row: dict[str, Any]):
    rot_dia = row.get('TBN_Rotor diameter')
    if rot_dia:
        return {FN_ROT_DIAMETER: row[FN_TURBINE_POWER]}
    else:
        fitted_value = fit_value(row[FN_TURBINE_POWER])
        return {FN_ROT_DIAMETER: round(fitted_value, 2)}



def location_strategy(row: dict[str, Any]):
    """
    get the defined location-name (city or area) and look it up in the location_lookup (prepares in 4_x_preps.py)
    :param row:
    :return:
    """
    global location_lookup
    loc_name = ""
    if row["Latitude"] != "nan" and row["Longitude"] != "nan":
        return {
            FN_ORIG_LOC_NAME: loc_name,
            FN_LATITUDE: row["Latitude"],
            FN_LONGITUDE: row["Longitude"]
        }
    else:
        if row["City"] and row["City"] != "nan":
            loc_name = row["City"]
        elif row["Area"] and row["Area"] != "nan":
            loc_name = row["Area"]
        else:
            loc_name = row["Country"]
        if loc_name:
            location_coordinates = location_lookup.get(loc_name)
            if location_coordinates:
                return {
                    FN_ORIG_LOC_NAME: loc_name,
                    FN_LATITUDE: location_coordinates["latitude"],
                    FN_LONGITUDE: location_coordinates["longitude"],
                    FN_RESOLVED_LOC_NAME: location_coordinates["name"],
                    FN_RESOLVED_ADDRESS_TYPE: location_coordinates["addresstype"]
                }
            else:
                print(f"Location not found: {loc_name}, {row['Country'], row['Area'],row['City']}")
        else:
            print(f"Location name is empty: {row}")
    return {FN_ORIG_LOC_NAME: loc_name}


def offshore_distance_strategy(row: dict[str, Any]):
    orig_value = row["Offshore Shore distance"]
    is_offshore = False
    shore_distance = ""
    if orig_value == "No":
        pass
    elif orig_value.startswith("Yes"):
        is_offshore = True
        distance_string = re.findall(r"\d+", orig_value)
        if distance_string:
            shore_distance = distance_string[0]
    else:
        print(f"Offshore Shore distance, weird value: {orig_value}")

    result = {
        FN_IS_OFFSHORE: is_offshore,
        FN_OFFSHORE_SHORE_DISTANCE: shore_distance,
    }

    if is_offshore:
        result[FN_LATITUDE] = ""
        result[FN_LONGITUDE] = ""
        result[FN_RESOLVED_LOC_NAME] = "OFFSHORE"
        result[FN_RESOLVED_ADDRESS_TYPE] = ""

    return result
