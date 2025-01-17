import csv
import os
from collections import Counter
from csv import DictReader, DictWriter
from pathlib import Path
from typing import Optional

import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

from const import (
    WINDPARK_MARKET_DELIMITER,
    base_data_path,
    fixed_market_file,
    raw_market_file, wind_extract_file,
)

base_dir = Path(r"data/0_base")
base_csv_dir = Path(r"data/1_csv")


# prepare_dir = Path(r"data/2_encoding_name_fixes")
# created in step 2 and needed in step 3
# encoding_fixed_file = fixed_files_dir / "aarhus_wind_farm_market_fix.csv"


def step_1_convert_csv():
    print("step_1_convert_csv")
    wind_farm_info_file = base_dir / "aarhus_wind_farm_market.xlsx"
    wind_info_clean_file = base_dir / "Wind_extract_clean.xls"
    parameter_file = base_dir / "Parameters data.xlsx"

    excel_files = [wind_farm_info_file, wind_info_clean_file, parameter_file]

    base_csv_dir.mkdir(exist_ok=True)

    for file in excel_files:
        # convert to csv
        if file.with_suffix(".csv").exists():
            continue
        print(file)
        print("->", base_csv_dir / file.with_suffix(".csv").name)
        try:
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            with open(base_csv_dir / file.with_suffix(".csv").name, "w", encoding="utf-8") as f:
                c = csv.writer(f)
                for index, r in enumerate(ws.rows):
                    try:
                        c.writerow([cell.value for cell in r])
                    except UnicodeEncodeError as e:
                        print(f"skip index: {index}, {r}, {e}")
        except InvalidFileException as e:
            print(f"skip {file}, {e}")


def step_2_fix_encoding():
    print("step_2_fix_encoding")
    encoding_errs = {
        'Ã¡': 'á',  # Spanish, Portuguese, Hungarian, Czech
        'Ã¢': 'â',  # French, Portuguese, Romanian, Turkish
        'Ã£': 'ã',  # Portuguese
        'Ã¤': 'ä',  # German, Swedish, Finnish, Estonian, Latvian, Lithuanian
        'Ã¥': 'å',  # Swedish, Danish, Norwegian
        'Ã¦': 'æ',  # Danish, Norwegian, Icelandic
        'Ã§': 'ç',  # Portuguese, Catalan, Turkish
        'Ã¨': 'è',  # French, Italian, Catalan
        'Ã©': 'é',  # French, Spanish, Portuguese, Catalan
        'Ãª': 'ê',  # French, Portuguese
        'Ã«': 'ë',  # Dutch, French
        'Ã¬': 'ì',  # Italian
        'Ã­': 'í',  # Spanish, Portuguese, Czech
        'Â ': '',
        'Ã®': 'î',  # French, Romanian
        'Ã¯': 'ï',  # Catalan, Dutch, French
        'Ã±': 'ñ',  # Spanish
        'Ã²': 'ò',  # Italian, Catalan
        'Ã³': 'ó',  # Spanish, Portuguese, Catalan, Polish, Hungarian
        'Ã´': 'ô',  # French, Portuguese
        'Ãµ': 'õ',  # Portuguese, Estonian
        'Ã¶': 'ö',  # German, Swedish, Finnish, Estonian, Latvian, Lithuanian
        'Ã¸': 'ø',  # Danish, Norwegian
        'Ã¹': 'ù',  # Italian
        'Ãº': 'ú',  # Spanish, Portuguese
        'Ã»': 'û',  # French, Portuguese
        'Ã¼': 'ü',  # German, Spanish, Catalan, Dutch, French
        'Ã½': 'ý',  # Czech, Icelandic
        'Ã¿': 'ÿ',  # French, Catalan
        'Ä': 'ā',  # Latvian
        'Äƒ': 'ă',  # Romanian
        'Ä…': 'ą',  # Polish, Lithuanian
        'Ä‡': 'ć',  # Polish, Croatian, Serbian, Bosnian
        'Ä': 'č',  # Czech, Slovak, Slovenian
        'Ä': 'ď',  # Czech, Slovak
        'Ä‘': 'đ',  # Croatian, Serbian, Bosnian
        'Ä“': 'ē',  # Latvian
        'Ä•': 'ĕ',  # Romanian
        'Ä—': 'ė',  # Lithuanian
        'ę': 'Ę',  # Polish, Lithuanian
        'ě': 'Ě',  # Czech, Slovak
        'Ä': 'ğ',  # Turkish
        'ÄŸ': 'Ğ',  # Turkish
        'ġ': 'Ġ',  # Maltese
        'ģ': 'Ģ',  # Latvian
        'Ä¥': 'ĥ',  # Esperanto
        'Ä§': 'ħ',  # Maltese
        'ĩ': 'Ĩ',  # Vietnamese
        'Ä«': 'ī',  # Latvian
        'Ä­': 'ĭ',  # Romanian
        'Ä¯': 'į',  # Lithuanian
        'ij': 'ĳ',  # Dutch
        'Äµ': 'ĵ',  # Esperanto
        'ķ': 'Ķ',  # Latvian
        'Äº': 'ĺ',  # Slovak
        'Ä¼': 'ļ',  # Latvian
        'Ä¾': 'ľ',  # Slovak
        'Å‚': 'ł',  # Polish
        'Å„': 'ń',  # Polish
        'Å†': 'ņ',  # Latvian
        'Åˆ': 'ň',  # Czech, Slovak
        'Å‡': 'Ň',  # Czech, Slovak
        'Å‘': 'ő',  # Hungarian
        'Å“': 'œ',  # French
        'Å•': 'ŕ',  # Slovak
        'Å—': 'ŗ',  # Latvian
        'Å™': 'ř',  # Czech
        'Å¡': 'š',  # Czech, Slovak, Slovenian, Croatian, Serbian, Bosnian
        'Å£': 'ţ',  # Romanian
        'Å¥': 'ť',  # Slovak, Czech
        'Å§': 'ŧ',  # Maltese
        'Å«': 'ū',  # Latvian
        'Å­': 'ŭ',  # Esperanto, Bulgarian
        'Å¯': 'ů',  # Czech
        'Å±': 'ű',  # Hungarian
        'Å³': 'ų',  # Lithuanian
        'Åµ': 'ŵ',  # Welsh
        'Å·': 'ŷ',  # Welsh
        'Åº': 'ź',  # Polish
        'Å¼': 'ż',  # Polish
        'Å¾': 'ž',  # Czech, Slovak, Slovenian, Croatian, Serbian, Bosnian
        # 'Ä‘': 'đ',  # Croatian, Serbian, Bosnian
        'Æ’': 'ƒ',  # Dutch
        # 'Å‚': 'ł',  # Polish
        'Æ„': '„',  # German, Polish
        'Æ…': '…',  # Polish
        'Æ†': '†',  # Polish
        'Æ‡': '‡',  # Polish
        'Æˆ': 'ˆ',  # Polish
        'Æ‰': '‰',  # Polish
        'ÆŠ': 'Š',  # Slovenian
        'Æ‹': '‹',  # Polish
        'ÆŒ': 'Œ',  # Polish, French
        "ÃŸ": "ß",  # German,
        "Ã ": "à",  # French, Italian,
        # "Ã": "Á",  # Spanish, Portuguese, Hungarian, Czech,
        "€™": "’",  # French, Italian, Catalan,
        # "Ã": "Á",  # Spanish, Portuguese, Hungarian, Czech,
        # "Ã¢": "â",  # French, Portuguese, Romanian, Turkish,
        # "Ã£": "ã",  # Portuguese,
        # "Ã¤": "ä",  # German, Swedish, Finnish, Estonian, Latvian, Lithuanian,
        # "Ã¥": "å",  # Swedish, Danish, Norwegian,
        # "Ã¦": "æ",  # Danish, Norwegian, Icelandic,
    }

    # open "aarhus_wind_farm_market.csv" and check if all values in column "Name" are unique
    # if not, add a number to the end of the name
    cols = ["Country", "Area", "City", "Name", "2nd name", "Developer", "Operator", "Owner", "Manufacturer"]

    fout = fixed_market_file.open("w")

    with raw_market_file.open() as fin:
        reader = csv.DictReader(fin, delimiter=WINDPARK_MARKET_DELIMITER)
        writer = csv.DictWriter(fout, reader.fieldnames, delimiter=",")
        writer.writeheader()
        for line in reader:
            for col in cols:
                # print(line[col])
                for key, value in encoding_errs.items():
                    line[col] = line[col].replace(key, value)
            writer.writerow(line)
    print(f"-> {fixed_market_file.relative_to(base_data_path)}")
    fout.close()


def step_3_name_fixing():
    print("step_3_name_fixing")
    # open encoding fix file and read with DictReader
    # Use Counter on Name
    # if value > 1, add a number to the end of the name
    # write to new file
    with fixed_market_file.open() as fin:
        reader = DictReader(fin)
        names = [line["Name"] for line in reader]
        name_counts = Counter(names)
        # print(name_counts)
        # print(len(name_counts))

    duplicates = [name for name, count in name_counts.items() if count > 1]

    # open file again with DictReader
    # Open a Writer and write the header
    # for each line, check if Name is in duplicates
    # if yes, add a number to the end of the name
    # write to new file
    name_indices = {}

    lines = []
    with fixed_market_file.open() as fin:
        reader = DictReader(fin)
        for line in reader:
            if line["Name"] in duplicates:
                name_indices[line["Name"]] = name_indices.get(line["Name"], 0) + 1
                line["Name"] = f'{line["Name"]}_{str(name_indices[line["Name"]])}'
            lines.append(line)

    with fixed_market_file.open("w") as fout:
        writer = DictWriter(fout, reader.fieldnames, delimiter=",")
        writer.writeheader()
        for line in lines:
            writer.writerow(line)

    # verification, should print a empty list
    with fixed_market_file.open() as fin:
        reader = DictReader(fin)
        names = [line["Name"] for line in reader]
        name_counts = Counter(names)

    duplicates = [name for name, count in name_counts.items() if count > 1]
    assert len(duplicates) == 0
    print(f"-> {fixed_market_file.relative_to(base_data_path)}")


def convert_weird_turbine_excel2csv():
    source_file = base_data_path / "0_base/Turbines_20231027.xlsx"
    wb = openpyxl.load_workbook(source_file)
    ws = wb.active
    with open(wind_extract_file,"w",encoding="utf-8") as fout:
        for row in ws.iter_rows():
            fout.write(row[0].value.replace("'", '"').replace(" ", " ")+os.linesep)


if __name__ == "__main__":
    # step 1. convert Excel files to csv
    # Wind_extract_clean.xls DONE MANUALLY WITH OFFICE
    # step_1_convert_csv()

    # step 2. fix encoding
    # step_2_fix_encoding()
    # step_3_name_fixing()

    # convert the final turbine excel file to a csv
    convert_weird_turbine_excel2csv()
