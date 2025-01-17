import pandas as pd

from const import (
    FINAL_COLUMNS,
    FN_TURBINE_MODEL,
    GEARBOX_GENERATOR_BUCKET_SIZE,
    filtered_market_file,
    gearbox_generator_probability_file,
    gearbox_generator_split_probability_file,
    location_fixing_file, result_file,
    simple_copy_pairs, preparation_dir, global_hh_power_fitting_params_file,
)
from const import (
    all_manufacturers_file,
    exact_match_lookup_file,
    filtered_turbine_file,
    fixed_market_file,
    global_power_fitting_params_file,
    raw_market_file,
    wind_extract_file,
)
from src.helper import dict_reader, dict_writer
from src.main.gearbox_generator_strategies import gearbox_generator_strategy
from src.main.strategies import (
    InvalidWindparkException,
    estimate_gentype_rotdia_of_missturbines,
    hub_height_strategy,
    load_data,
    location_strategy,
    offshore_distance_strategy,
    turbine_power_strategy,
)
from src.main.turbine_matching import (
    load_matching_data,
    match_type_counts,
    turbine_match, unknown_manufacturers, unkonwn_manu_turbine_combos,
)
from src.prep.convert_format_fix_encoding import (
    step_1_convert_csv,
    step_2_fix_encoding,
    step_3_name_fixing, convert_weird_turbine_excel2csv,
)
from src.prep.filter_market import (
    add_turbine_power_column,
    filter_market,
    remove_irrelevant_columns,
)
from src.prep.gearbox_generator_probabilities import calc_probabilities
from src.prep.location_fixing import do_location_fixing
from src.prep.prepare_hub_height import create_hh_filtered_turbine_power_fitting
from src.prep.prepare_location_search import location_preparation
from src.prep.prepare_matching import prepare_turbine_matching
from src.prep.prepare_power_fit import create_filtered_turbine_power_fitting

strategies = [
    # If we have a turbine, we take the value of the technical data,
    # instead of the market data
    turbine_power_strategy,
    hub_height_strategy,
    estimate_gentype_rotdia_of_missturbines,
    gearbox_generator_strategy,
    location_strategy,
    offshore_distance_strategy,
]


def run_checked_preparation(
    redo_fix_encoding=False,
    redo_filter=False,
    test_all_filters=False,
    redo_power_fitting_params=False,
    redo_prepare_matching=False,
    redo_gearbox_generator=False,
    redo_continue_location_search=False,
    redo_prepare_hub_height_estimation=False,
):
    preparation_dir.mkdir(exist_ok=True)
    """
    Check which preparation needs to be done (based on files existence), and do them
    """
    if (not wind_extract_file.exists()) or (not raw_market_file.exists()):
        print("File conversion should be done (manually if it fails)")
        step_1_convert_csv()

    # fix encoding and windpark names
    if not fixed_market_file.exists() or redo_fix_encoding:
        step_2_fix_encoding()
        step_3_name_fixing()
        convert_weird_turbine_excel2csv()

    # filtering, removing irrelevant columns, adding turbine power column
    if (
        not filtered_market_file.exists()
        or not filtered_turbine_file.exists()
        or redo_filter
    ):
        filter_market(test_all_filters=test_all_filters)
        remove_irrelevant_columns()
        add_turbine_power_column()

    if location_fixing_file.exists():
        do_location_fixing()

    # power fitting parameters
    if not global_power_fitting_params_file.exists() or redo_power_fitting_params:
        create_filtered_turbine_power_fitting()

    # turbine matching
    if (
        any(not f.exists() for f in [all_manufacturers_file, exact_match_lookup_file])
        or redo_prepare_matching
    ):
        prepare_turbine_matching()

    if (
        not gearbox_generator_probability_file.exists()
        or not gearbox_generator_split_probability_file.exists()
        or redo_gearbox_generator
    ):
        calc_probabilities(GEARBOX_GENERATOR_BUCKET_SIZE)

    # location
    if redo_continue_location_search:
        location_preparation()

    if (
        redo_prepare_hub_height_estimation
        or not global_hh_power_fitting_params_file.exists()
    ):
        create_hh_filtered_turbine_power_fitting()


def final_validation():
    df = pd.read_csv(result_file)
    no_nan_columns = ["Latitude", "Longitude", "Hub height", "Rotor diameter"]

    for col in no_nan_columns:
        try:
            assert not df[col].isnull().values.any()
        except AssertionError:
            print(f"Some rows have no '{col}':")
            for row in df[df[col].isnull()].iterrows():
                print(row[1]["ID"])


def main_loop(do_final_validation:bool=True):
    reader = dict_reader(filtered_market_file)
    writer, fout = dict_writer(result_file, FINAL_COLUMNS)
    writer.writeheader()

    load_data()
    load_matching_data()

    for line in reader:
        # for line in tqdm(reader):
        result_row = {}
        # turbine_data = lookup_turbine(line)
        turbine_data = turbine_match(line)
        filter_out = False
        if turbine_data:
            # we cant just merge the dicts cuz, some keys overlap
            # print(set(line.keys()).intersection(set(turbine_data.keys())))
            # print(turbine_data)
            line.update({f"TBN_{key}": value for (key, value) in turbine_data.items()})
            result_row[FN_TURBINE_MODEL] = turbine_data["Name"]
            if line["Turbine"] != turbine_data["Name"]:
                raise Exception("Turbine name changed")
            line["Turbine"] = turbine_data["Name"]
        for strategy in strategies:
            try:
                result_row.update(strategy(line))
            except InvalidWindparkException as er:
                filter_out = True
                break
            # except Exception as er:
            #     print(f"strategy broke: {strategy.__name__}: {er}")

        if filter_out:
            continue

        simple_copy_data = {
            v: line.get(k) for k, v in simple_copy_pairs.items() if line.get(k)
        }
        result_row.update(simple_copy_data)
        writer.writerow(result_row)

    print(match_type_counts)

    # load result_file with pandas and sort the rows by ID
    # df = pd.read_csv(result_file, encoding="utf-8")
    # df.sort(by=["ID"], inplace=True)
    # df.to_csv(result_file, index=False, encoding="utf-8")

    print(f"Unknown manufacturer: {unknown_manufacturers}")
    print(f"Unknown manu-turbine combo: {unkonwn_manu_turbine_combos}")
    if do_final_validation:
        final_validation()


def run(
    run_main_loop=True,
    final_validation=True,
    redo_fix_encoding=False,
    redo_filter=False,
    test_all_filters=False,
    redo_power_fitting_params=False,
    redo_prepare_matching=False,
    redo_gearbox_generator=False,
    redo_continue_location_search=False,
    redo_prepare_hub_height_estimation=False,
):
    run_checked_preparation(
        redo_fix_encoding=redo_fix_encoding,
        redo_filter=redo_filter,
        test_all_filters=test_all_filters,
        redo_power_fitting_params=redo_power_fitting_params,
        redo_prepare_matching=redo_prepare_matching,
        redo_gearbox_generator=redo_gearbox_generator,
        redo_continue_location_search=redo_continue_location_search,
        redo_prepare_hub_height_estimation=redo_prepare_hub_height_estimation,
    )
    if run_main_loop:
        main_loop(final_validation)

