from typing import Any

import numpy as np

from const import (
    FN_GEARBOX_GENERATOR,
    FN_TURBINE_POWER,
    FN_X_GEARBOX_GENERATOR_PROB,
    FN_X_GENERATOR_PROB,
    GEARBOX_GENERATOR_BUCKET_SIZE,
    gearbox_generator_probability_file,
    gearbox_generator_split_probability_file,
)
from src.helper import load_json

if gearbox_generator_probability_file.exists():
    power_gearbox_generator_probabilities: dict[int, dict[str, float]] = {
        int(k): v for k, v in load_json(gearbox_generator_probability_file).items()  # type: ignore
    }

if gearbox_generator_split_probability_file.exists():
    power_generator_from_gearbox_probabilities: dict[
        str, dict[int, dict[str, float]]
    ] = {}

    data = load_json(gearbox_generator_split_probability_file)
    for gearbox_type, values in data.items():  # type: ignore
        power_generator_from_gearbox_probabilities[gearbox_type] = {
            int(k): v for k, v in values.items()
        }


def _gearbox_strategy(row: dict[str, Any]) -> tuple[str, float]:
    gearbox = row.get("TBN_Gear box")
    if gearbox == "No":
        return "dd", 1
    else:
        return "gb", 1


def _pick_random_generator_from_gearbox(
    turbine_power: int, gearbox: str
) -> tuple[str, float]:
    global power_generator_from_gearbox_probabilities
    power_generato_probabilities = power_generator_from_gearbox_probabilities[gearbox]
    bucket_power = (
        turbine_power // GEARBOX_GENERATOR_BUCKET_SIZE
    ) * GEARBOX_GENERATOR_BUCKET_SIZE
    if bucket_power not in power_generato_probabilities:
        max_bucket_power = max(power_generato_probabilities.keys())
        print(f"warning, turbine power very large, using max bucket: {turbine_power}:{bucket_power} > {max_bucket_power}")
        bucket_power = max_bucket_power

    # choose the largest bucket which has a generator (fix required after using complete turbine dataset)
    generator_prob = {}
    while not generator_prob:
        generator_prob = power_generato_probabilities[bucket_power]
        bucket_power -= GEARBOX_GENERATOR_BUCKET_SIZE
    generators = list(generator_prob.keys())
    probabilities = list(generator_prob.values())
    selection = np.random.choice(generators, p=probabilities)
    return selection, generator_prob[selection]


def _generator_strategy(row: dict[str, Any], gearbox: str) -> tuple[str, float]:
    """
    :return: tuple of generator and probability
    """
    generators_converter = {
        "dfig": ["ASYNC", "ASYNC DF", "DF", "IND", "DFIG"],
        "eesg": ["SYNC", "SYNC Wounded"],
        "pmsg": ["SYNC PM", "PM"]
    }
    generator = row.get("TBN_Generators")
    if not generator or generator == "#ND":
        return _pick_random_generator_from_gearbox(
            round(float(row[FN_TURBINE_POWER])), gearbox
        )
    for key, value in generators_converter.items():
        if generator in value:
            return f"{gearbox}_{key}", 1
    raise Exception(f"generator not found: {generator}")


def _pick_gearbox_generator(turbine_power: int) -> tuple[str, float]:
    global power_gearbox_generator_probabilities
    pggp = power_gearbox_generator_probabilities
    bucket_power = (
        turbine_power // GEARBOX_GENERATOR_BUCKET_SIZE
    ) * GEARBOX_GENERATOR_BUCKET_SIZE
    if bucket_power not in pggp:
        max_bucket_power = max(pggp.keys())
        print(
            f"warning, turbine power very large '{turbine_power}:{bucket_power} >"
            f" {max_bucket_power}, using max bucket"
        )
        bucket_power = max_bucket_power

    gearboxes_generator_prob = power_gearbox_generator_probabilities[bucket_power]
    gearboxes_generators = list(gearboxes_generator_prob.keys())
    probabilities = list(gearboxes_generator_prob.values())
    selection = np.random.choice(gearboxes_generators, p=probabilities)
    return selection, gearboxes_generator_prob[selection]


def gearbox_generator_strategy(row):
    """
    When we have no gearbox (implies also no generator), we pick a gearbox_generator
    from the gearbox_generator_probabilities.json file.
    If we have a gearbox, we check if there is a generator. If there is no generator,
    we pick a generator from the gearbox_generator_split_probability_file.json file.
    :param row:
    :return:
    """
    result = {}

    gearbox = row.get("TBN_Gear box")
    if not gearbox or gearbox == "#ND":
        # pick gearbox_generator
        gearbox_generator, gearbox_generator_prob = _pick_gearbox_generator(
            round(float(row[FN_TURBINE_POWER]))
        )
        result[FN_GEARBOX_GENERATOR] = gearbox_generator
        result[FN_X_GEARBOX_GENERATOR_PROB] = round(gearbox_generator_prob, 4)
    else:
        gearbox, gearbox_prob = _gearbox_strategy(row)
        gearbox_generator, generator_prob = _generator_strategy(row, gearbox)
        result[FN_GEARBOX_GENERATOR] = gearbox_generator
        if generator_prob == 1:
            result[FN_X_GEARBOX_GENERATOR_PROB] = 1
        result[FN_X_GENERATOR_PROB] = round(generator_prob, 4)

    # result[FN_X_GENERATOR_PROB] = round(generator_prob, 4)
    return result
