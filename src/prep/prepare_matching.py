from const import (
    all_manufacturers_file,
    base_data_path,
    exact_match_lookup_file,
    filtered_market_file,
    filtered_turbine_file,
    manuf_power_turbine_match_file,
    manuf_power_turbine_match_file_complete,
    matching_dir,
)
from src.helper import dict_reader, dump_json


def prepare_turbine_matching():
    print("prepare turbine matching")
    all_manufacturer = set()
    exact_match_lookup_data = {}
    manuf_power_lookup_data_complete = {}
    manuf_power_lookup_data = {}

    matching_dir.mkdir(exist_ok=True)
    reader = dict_reader(filtered_turbine_file)

    # collect all manufacturers, create the exact match lookup and prepare the
    # manuf_power_lookup
    turbine_rows = list(reader)
    for row in turbine_rows:
        all_manufacturer.add(row["Manufucturer"])
        exact_match_lookup_data[(row["Manufucturer"].lower(), row["Name"])] = row
        manuf_power_lookup_data_complete.setdefault(
           (row["Manufucturer"].lower(), int(row["Rated power"]))
        ,[]).append([row["Name"], 0])

    # dump the data (all manufacturers, exact match lookup and manuf_power_lookup)
    dump_json(all_manufacturers_file, list(all_manufacturer))
    print(f"-> {all_manufacturers_file.relative_to(base_data_path)}")
    dump_json(exact_match_lookup_file, list(exact_match_lookup_data.items()))
    print(f"-> {exact_match_lookup_file.relative_to(base_data_path)}")

    # iterate through all windparks and add the number of turbines to the
    market_reader = dict_reader(filtered_market_file)
    for windpark in market_reader:
        turbine_data = exact_match_lookup_data.get(
            (windpark["Manufacturer"].lower(), windpark["Turbine"])
        )
        # match found
        if turbine_data:
            # add to lookup
            manuf_power_list = manuf_power_lookup_data_complete[
                (windpark["Manufacturer"].lower(), int(turbine_data["Rated power"]))
            ]
            turbine_exists = False
            # check if turbine exists in manu, power list (add number or create)
            for turbine_power in manuf_power_list:
                if turbine_power[0] == windpark["Turbine"]:
                    turbine_power[1] += int(windpark["Number of turbines"])
                    turbine_exists = True
                    break

    # sort all manuf_power lists by number of turbines
    for manu_power, name_count in manuf_power_lookup_data_complete.items():
        name_count_sorted = sorted(
            name_count, key=lambda x: x[1], reverse=True
        )
        manuf_power_lookup_data_complete[manu_power] = name_count_sorted
        # this one is actually redundant cuz of the 2nnd check
        if all([nc[1] == 0 for nc in name_count_sorted]) and len(name_count_sorted) > 1:
            print(f"Manu-power combo has more than 1 turbine, but none exists in the windpark dataset: {(manu_power, name_count)}")
        # check, if there are several with the same count
        elif len(name_count_sorted) > 1 and name_count_sorted[0][1] == name_count_sorted[1][1]:
            print(f"Manu-power combo has more than 1 turbine, with the same count: "
                  f"{list(filter(lambda nc: nc[1] == name_count_sorted[0][1], name_count_sorted))}")


    # store complete lists
    dump_json(
        manuf_power_turbine_match_file_complete,
        list(manuf_power_lookup_data_complete.items()),
    )
    print(f"-> {manuf_power_turbine_match_file_complete.relative_to(base_data_path)}")
    # just take the name of the most common turbine
    for manu_power, name_count in manuf_power_lookup_data_complete.items():
        if name_count:
            manuf_power_lookup_data[manu_power] = name_count[0][0]
    # store that lookup
    # redundant. the same as "manuf_power_lookup_data_complete"
    dump_json(manuf_power_turbine_match_file, list(manuf_power_lookup_data_complete.items()))
    print(f"-> {manuf_power_turbine_match_file.relative_to(base_data_path)}")
