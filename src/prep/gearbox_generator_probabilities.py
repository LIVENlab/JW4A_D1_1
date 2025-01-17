from collections import Counter

from const import (
    GEARBOX_GENERATOR_BUCKET_SIZE,
    filtered_turbine_file,
    gearbox_generator_dir,
    gearbox_generator_probability_file,
    gearbox_generator_split_probability_file,
)
from src.helper import dict_reader, dump_json


def gearbox_lookup(gearbox):
    if not gearbox or gearbox == "#ND":
        return ""
    if gearbox == "No":
        return "dd"
    else:
        return "gb"


def generator_lookup(generator):
    generators_converter = {
        "dfig": ["ASYNC", "ASYNC DF", "DF", "IND", "DFIG"],
        "eesg": ["SYNC", "SYNC Wounded"],
        "pmsg": ["SYNC PM"],
        "": ["#ND"],
    }

    for key, value in generators_converter.items():
        if generator in value:
            return key


def calc_probabilities(gearbox_generator_bucket_size: int):
    gearbox_generator_dir.mkdir(exist_ok=True)

    reader = dict_reader(filtered_turbine_file)
    rows = list(reader)

    power_gearbox_generator: dict[int, Counter] = {}
    all_gearbox_generators = set()
    # iterate through all turbines
    for row in rows:
        p = int(row["Rated power"])
        gearbox = gearbox_lookup(row["Gear box"])
        generator = generator_lookup(row["Generators"])

        if gearbox and generator:
            gearbox_generator = f"{gearbox}_{generator}"
            power_gearbox_generator.setdefault(
                p // GEARBOX_GENERATOR_BUCKET_SIZE * GEARBOX_GENERATOR_BUCKET_SIZE,
                Counter(),
            ).update([gearbox_generator])
            all_gearbox_generators.add(gearbox_generator)

    power_gearbox_generator_rel = {}
    power_gearbox_gearbox_spec_generators: dict[str, dict[int, str]] = {
        "gb": {},
        "dd": {},
    }

    for p, counter in sorted(power_gearbox_generator.items()):
        # print(p, counter)
        # values = counter.values()
        total = counter.total()
        rel = {k: v / total for k, v in counter.items()}
        # print(rel)
        power_gearbox_generator_rel[p] = rel

        for gearbox_type in ["dd", "gb"]:
            values = [v for k, v in counter.items() if k.split("_")[0] == gearbox_type]
            total = sum(values)
            rel = {
                k: v / total
                for k, v in counter.items()
                if k.split("_")[0] == gearbox_type
            }
            # print(rel)
            power_gearbox_gearbox_spec_generators[gearbox_type][p] = rel

    dump_json(gearbox_generator_probability_file, power_gearbox_generator_rel)

    dump_json(
        gearbox_generator_split_probability_file, power_gearbox_gearbox_spec_generators
    )
