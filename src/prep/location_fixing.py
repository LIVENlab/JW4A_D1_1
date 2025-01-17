from const import filtered_market_file, location_fixing_file
from src.helper import dict_reader, dict_writer, load_json


def do_location_fixing():
    reader = dict_reader(filtered_market_file)
    rows = list(reader)
    writer, fout = dict_writer(filtered_market_file, list(reader.fieldnames))
    writer.writeheader()
    location_fix_data = load_json(location_fixing_file)
    for row in rows:
        if row["Area"] in location_fix_data:
            row["Area"] = location_fix_data[row["Area"]]
        if row["City"] in location_fix_data:
            row["City"] = location_fix_data[row["City"]]
        writer.writerow(row)
    fout.close()
