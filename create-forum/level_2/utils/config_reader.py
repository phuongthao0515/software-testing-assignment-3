import csv
from pathlib import Path


LEVEL_2_DIR = Path(__file__).resolve().parents[1]


def read_key_value_csv(relative_path):
    file_path = LEVEL_2_DIR / relative_path
    data = {}

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data[row["key"]] = row["value"]

    return data
