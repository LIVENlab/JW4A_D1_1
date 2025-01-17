import math
from typing import Any, Callable

from const import (
    FN_TURBINE_POWER,
    TURBINE_LOOKUP_DELIMITER,
    TURBINE_RELEVANT_COLUMNS,
    WINDPARK_RELEVANT_COLUMNS,
    base_data_path,
    filtered_market_file,
    filtered_turbine_file,
    fixed_market_file,
    wind_extract_file, TURBINE_RENAME_COLUMNS,
)
from src.helper import dict_reader, dict_writer
from src.main.strategies import InvalidWindparkException


def wind_park_in_europe_filter(row: dict[str, Any]):
    """
    Filter out wind parks that are not in europe
    :param row:
    :return:
    """
    if row["Continent"] != "Europe":
        raise InvalidWindparkException(f"not in europe", row["Continent"])
    return {}


def no_manufacturer(row: dict[str, Any]):
    """
    Filter out wind parks that have no manufacturer or turbine or power
    :param row:
    :return:
    """
    if not row["Manufacturer"]:
        raise InvalidWindparkException(f"no manufacturer or turbine or power", row)
    return {}


def wind_park_power_filter(row: dict[str, Any]):
    try:
        power = float(row["Total power"])
        assert not math.isnan(power)
    except (ValueError, AssertionError) as er:
        raise InvalidWindparkException(f"Invalid power value: {er}", er)


def number_of_turbines_filter(row: dict[str, Any]):
    try:
        num_turbines = int(row["Number of turbines"])
        assert not math.isnan(num_turbines)
    except (ValueError, AssertionError) as er:
        raise InvalidWindparkException(f"Invalid number of turbines: {er}", er)


filters: list[Callable] = [
    wind_park_in_europe_filter,
    no_manufacturer,
    wind_park_power_filter,
    number_of_turbines_filter,
]


def filter_market(test_all_filters=False):
    """
    :param test_all_filters: if this variable is set, all filters are tested on each row
        (giving more detailed info)
    :return:
    """
    print("filtering market file")
    reader = dict_reader(fixed_market_file)
    writer, fout = dict_writer(filtered_market_file, fieldnames=list(reader.fieldnames))
    writer.writeheader()
    total_rows = 0
    kept_rows = 0
    filter_count = {_filter.__name__: 0 for _filter in filters}
    for row in reader:
        total_rows += 1
        filtered_out = False
        for _filter in filters:
            try:
                _filter(row)
            except InvalidWindparkException as er:
                filtered_out = True
                if not test_all_filters:
                    filter_count[_filter.__name__] = filter_count[_filter.__name__] + 1
                    break
                else:
                    filter_count[_filter.__name__] = filter_count[_filter.__name__] + 1
        if not filtered_out:
            writer.writerow(row)
            kept_rows += 1
    print(f"total rows: {total_rows}")
    print(f"filter: {filter_count}")
    print(f"kept rows: {kept_rows}")
    print(f"-> {filtered_market_file.relative_to(base_data_path)}")
    fout.close()


def remove_irrelevant_columns():
    """
    remove columns that are not relevant for the analysis (defined in const.py)
    :return:
    """
    print("remove irrelevant columns")
    # windpark
    reader = list(dict_reader(filtered_market_file))
    writer, fout = dict_writer(filtered_market_file, WINDPARK_RELEVANT_COLUMNS)
    writer.writeheader()
    for row in reader:
        writer.writerow(
            {
                col: value
                for col, value in row.items()
                if col in WINDPARK_RELEVANT_COLUMNS
            }
        )
    fout.close()
    print(f"-> {filtered_market_file.relative_to(base_data_path)}")
    # turbine table file
    reader = dict_reader(wind_extract_file, delimiter=TURBINE_LOOKUP_DELIMITER)
    writer, fout = dict_writer(filtered_turbine_file, TURBINE_RELEVANT_COLUMNS)
    writer.writeheader()
    for row in reader:
        writer.writerow(
            {
                TURBINE_RENAME_COLUMNS.get(col, col): value
                for col, value in row.items()
                if TURBINE_RENAME_COLUMNS.get(col,  col) in TURBINE_RELEVANT_COLUMNS
            }
        )
    fout.close()
    print(f"-> {filtered_turbine_file.relative_to(base_data_path)}")


def add_turbine_power_column():
    print("adding turbine power column")
    reader = dict_reader(filtered_market_file)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)
    writer, fout = dict_writer(filtered_market_file, fieldnames + [FN_TURBINE_POWER])
    writer.writeheader()
    for row in rows:
        try:
            row[FN_TURBINE_POWER] = float(row["Total power"]) / int(
                row["Number of turbines"]
            )
            writer.writerow(row)
        except:
            print(row)
    fout.close()
    print(f"-> {filtered_market_file.relative_to(base_data_path)}")
