import json
from csv import DictReader
from random import randint
from time import sleep

import requests
from pandas import DataFrame
from tqdm import tqdm

from const import (
    filtered_market_file,
    LOCATION_BASE_QUERY,
    full_location_responses_file,
    location_dir,
    location_errors_info_file,
    location_file,
    location_errors_file
)


def search_windpark_coordinates():
    # coming from files
    full_location_responses = {}
    locations = {}
    location_errors = []
    # for avoiding duplicate checks
    location_error_names = []

    # make sure the folder exists
    location_dir.mkdir(parents=True, exist_ok=True)

    if full_location_responses_file.exists():
        with full_location_responses_file.open(encoding="utf-8") as fin:
            full_location_responses = json.load(fin)
    if location_file.exists():
        with location_file.open(encoding="utf-8") as fin:
            locations = json.load(fin)
    if location_errors_file.exists():
        with location_errors_file.open(encoding="utf-8") as fin:
            location_errors = json.load(fin)
        location_error_names = [e["name"] for e in location_errors if e["name"]]

    try:
        with filtered_market_file.open(encoding="utf-8") as fin:
            reader = DictReader(fin)
            rows = list(reader)
            for row in tqdm(rows):
                if row["Latitude"] == "nan" or row["Longitude"] == "nan":
                    loc_name = ""
                    loc_type = None
                    if (row["Country"], row["Area"], row["City"]) == ('Albania', 'Tiranë', 'nan'):
                        pass
                    if row["City"] and row["City"] != "nan":
                        loc_name = row["City"]
                        loc_type = "city"
                    elif row["Area"] and row["Area"] != "nan":
                        loc_name = row["Area"]
                        loc_type = "area"
                    else:
                        loc_name = row["Country"]
                        loc_type = "country"
                        # print(loc_name)
                    if loc_name == "Steinfurt": # or loc_name == "Nordrhein-Westfalen":
                        pass
                    if loc_name:
                        # we have it already, or we had an error before
                        if loc_name in locations:
                            continue
                        if loc_name in location_error_names:
                            continue
                        print(loc_name)
                        # QUERY!
                        qs = LOCATION_BASE_QUERY.replace("{}", loc_name)
                        if loc_type == "country":
                            qs = qs + "&limit=50"
                        response = requests.get(qs)
                        print(json.dumps(response.json(), indent=2))
                        data = response.json()
                        full_location_responses[loc_name] = data
                        location_data = data[0]
                        if loc_type == "country":
                            for loc in data:
                                if loc["addresstype"] == "country":
                                    location_data = loc
                                    break
                        try:
                            locations[loc_name] = {
                                "longitude": location_data["lon"],
                                "latitude": location_data["lat"],
                                "name": location_data["name"],
                                "addresstype": location_data["addresstype"],
                            }
                        except:
                            print("no location for", loc_name)
                            location_error_names.append(loc_name)
                            location_errors.append({"name": loc_name})
                        sleep(randint(1, 3))

                        # print(f"no location name for {row['ID']}")
                        # location_errors.append({"id": row["ID"]})
    except KeyboardInterrupt:
        print("cancelling location search... saving results")
    finally:
        with full_location_responses_file.open("w", encoding="utf-8") as fout:
            json.dump(full_location_responses, fout, ensure_ascii=False, indent=2)
        with location_file.open("w", encoding="utf-8") as fout:
            json.dump(locations, fout, ensure_ascii=False, indent=2)
        with location_errors_file.open("w", encoding="utf-8") as fout:
            json.dump(location_errors, fout, ensure_ascii=False, indent=2)


def location_error_info():
    # set of error names
    location_errors = set()

    df = DataFrame(columns=["ID", "Country", "Area", "City", "Name"])

    if location_errors_file.exists():
        with location_errors_file.open() as fin:
            location_errors = set([l["name"] for l in json.load(fin) if l["name"]])

    with filtered_market_file.open(encoding="utf-8") as fin:
        reader = DictReader(fin)
        rows = list(reader)
        for row in rows:
            if row["City"]:
                loc_name = row["City"]
            elif row["Area"]:
                loc_name = row["Area"]
            if loc_name in location_errors:
                # add one row, but only data for relevant columns
                data = {k: row[k] for k in df.columns}
                df = df._append(data, ignore_index=True)

    df.to_csv(location_errors_info_file)
    return df


def location_preparation():
    search_windpark_coordinates()
    location_error_info()
