import json
from csv import DictReader, DictWriter
from pathlib import Path
from typing import Any, TextIO, Union


def dict_reader(file_path: Path, delimiter: str = ",") -> DictReader:
    return DictReader(file_path.open(encoding="utf-8"), delimiter=delimiter)


def dict_writer(file_path: Path, fieldnames: list[str]) -> tuple[DictWriter, TextIO]:
    fout = file_path.open("w", encoding="utf-8")
    writer = DictWriter(fout, fieldnames=fieldnames, delimiter=",")
    return writer, fout


def load_json(file_path: Path) -> Union[dict, list]:
    return json.load(file_path.open(encoding="utf-8"))


def dump_json(file_path: Path, data: Union[dict, list]):
    file_path.open("w", encoding="utf-8").write(json.dumps(data, indent=2))


def transform_items_to_dict(items: list[tuple[Any, Any]]) -> dict[str, str]:
    return {tuple(k): v for k, v in items}
