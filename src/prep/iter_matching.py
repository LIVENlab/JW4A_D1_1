from typing import Generator

from const import filtered_market_file
from src.helper import dict_reader
from src.main.turbine_matching import load_matching_data


def iterate_windpark_with_matching_turbines() -> (
    Generator[tuple[dict, dict], None, None]
):
    exact_match_lookup_data = load_matching_data()["exact_match_lookup_data"]

    market_reader = dict_reader(filtered_market_file)
    for windpark in market_reader:
        turbine_data = exact_match_lookup_data.get(
            (windpark["Manufacturer"], windpark["Turbine"])
        )
        if turbine_data:
            yield windpark, turbine_data
