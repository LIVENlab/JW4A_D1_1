import math
from random import choice
from typing import Any

from const import (
    FN_TURBINE_POWER,
    all_manufacturers_file,
    exact_match_lookup_file,
    manuf_power_turbine_match_file, manuf_power_turbine_match_file_complete,
)
from src.helper import load_json, transform_items_to_dict

# just a simple list of exising manufacturers
all_manufacturer: set[str] = set()
all_manufacturer_lower: set[str] = set()
# exact_match: (manufacturer, model) -> complete data
exact_match_lookup_data: dict[tuple[str, str], list[tuple[str, Any]]] = {}
# lookup: (manufacturer, rated power) -> model, count
manuf_power_lookup_data_complete: dict[tuple[str, int], list[tuple[str, int]]] = {}
manuf_power_lookup_data: dict[tuple[str, int], str] = {}
unknown_manufacturers = set()
unkonwn_manu_turbine_combos = set()

match_type_counts = {
    "x1_no_total_power": 0,
    "x2_no_manu": 0,
    "x3_manu_doesnt_exist": 0,
    # #"a_most_common": 0,
    "b_power_match": 0,
    "c_closest_power": 0,
    "d_exact_match": 0,
    "dx_unknown_menu-turbine_combo": 0
}


def load_matching_data():
    global all_manufacturer, all_manufacturer_lower, exact_match_lookup_data, manuf_power_lookup_data_complete, manuf_power_lookup_data
    all_manufacturer = load_json(all_manufacturers_file)
    all_manufacturer_lower = [m.lower() for m in all_manufacturer]
    exact_match_lookup_data = transform_items_to_dict(
        load_json(exact_match_lookup_file)
    )
    manuf_power_lookup_data_complete = transform_items_to_dict(
        load_json(manuf_power_turbine_match_file_complete)
    )
    manuf_power_lookup_data = transform_items_to_dict(
        load_json(manuf_power_turbine_match_file)
    )

    return {
        "all_manufacturer": all_manufacturer,
        "all_manufacturer_lower": all_manufacturer_lower,
        "exact_match_lookup_data": exact_match_lookup_data,
        "manuf_power_lookup_data_complete":manuf_power_lookup_data_complete,
        "manuf_power_lookup_data": manuf_power_lookup_data,
    }


def exact_turbine_lookup(row):
    global exact_match_lookup_data
    return exact_match_lookup_data.get((row["Manufacturer"].lower(), row["Turbine"]))


def find_closest_manufacturer_power(
    manufacturer: str, turbine_power: int
) -> tuple[str, int]:
    # use the complete data, not just the most common, otherwise "Guangdong Mingyang" will not be matched.
    global manuf_power_lookup_data_complete
    # get all manufacturers with the same name as the park
    # manuf_power_lookup keys are tuple (manufacturer, rated power)
    matching_manufacturers = list(
        filter(
            lambda man_power: man_power[0] == manufacturer,
            manuf_power_lookup_data_complete.keys(),
        )
    )
    power_differences = [
        abs(man_powers[1] - turbine_power) for man_powers in matching_manufacturers
    ]
    # get index with the lowest difference
    min_index = power_differences.index(min(power_differences))
    # get the closest (manufacturer, power) pair
    return matching_manufacturers[min_index]


def turbine_match(row):
    global unknown_manufacturers
    manufacturer = str(row["Manufacturer"]).lower()
    turbine = row["Turbine"]
    # Windpark has Manufacturer?
    # Windpark has Manufacturer? NO
    # THIS IS NOT NEEDED HERE. IT IS A STRATEGY
    if manufacturer == "nan":
        match_type_counts["x2_no_manu"] += 1
        return {}

    # Windpark has Manufacturer? YES
    # Manufacturer exist?
    # Manufacturer exist? NO
    if not manufacturer_exists(manufacturer):
        match_type_counts["x3_manu_doesnt_exist"] += 1
        unknown_manufacturers.add(manufacturer)
        return {}
    # Manufacturer exist? YES

    # WPHasTurbine?
    # WPHasTurbine? YES
    if turbine != "nan":
        # ManTurbinePairExists?
        exact_match = exact_turbine_lookup(row)
        # ManTurbinePairExists? YES
        if exact_match:  # ManTurbinePairExists? YES
            # MATCH (d)
            match_type_counts["d_exact_match"] += 1
            # if DO_POWER_MATCH_FOR_EXACT_MATCH:
            #     do_power_match_verfications(row)
            return exact_match
        else:
            match_type_counts["dx_unknown_menu-turbine_combo"] += 1
            unkonwn_manu_turbine_combos.add((manufacturer, turbine))

    # WPHasTurbine? NO
    # OR ManTurbinePairExists? NO

    # Powermatch?
    turbine_power = math.floor(float(row[FN_TURBINE_POWER]))
    man_turbine_lookup: list[tuple[str, int]] = manuf_power_lookup_data.get((manufacturer, turbine_power))
    # Powermatch? YES

    def pick_candidate(man_turbine_lookup: list[tuple[str, int]]) -> str:
        # check if there are several candidates
        if len(man_turbine_lookup) > 1 and man_turbine_lookup[0][1] == man_turbine_lookup[1][1]:
            print(f"Manu-power combo '{(row['Manufacturer'], turbine_power)}' of windpark '{row['ID']}' "
                  f"has several candidates: {[m[0] for m in man_turbine_lookup]}. Picking random one.")
            candidates = list(filter(lambda nc: nc[1] == man_turbine_lookup[0][1], man_turbine_lookup))
            return choice(candidates)[0]
        else:
            return man_turbine_lookup[0][0]

    if man_turbine_lookup:
        row["Turbine"] = pick_candidate(man_turbine_lookup)
        power_match = exact_turbine_lookup(row)
        match_type_counts["b_power_match"] += 1
        # MATCH (b)
        return power_match
    else:  # Powermatch? # NO -> Find the closest power
        # get the closest power-matching turbine
        closest_pair = find_closest_manufacturer_power(manufacturer, turbine_power)
        man_turbine_lookup = manuf_power_lookup_data.get(closest_pair)
        row["Turbine"] = pick_candidate(man_turbine_lookup)
        closest_power_match = exact_turbine_lookup(row)
        # MATCH (c)
        match_type_counts["c_closest_power"] += 1
        return closest_power_match


def manufacturer_exists(manufacturer: str):
    global all_manufacturer, all_manufacturer_lower
    return manufacturer.lower() in all_manufacturer_lower
    # return manufacturer in all_manufacturer
