import csv
from pathlib import Path
from selenium.webdriver.common.by import By

LEVEL_2_DIR = Path(__file__).resolve().parents[1]


BY_MAP = {
    "ID": By.ID,
    "NAME": By.NAME,
    "XPATH": By.XPATH,
    "CSS_SELECTOR": By.CSS_SELECTOR,
    "LINK_TEXT": By.LINK_TEXT,
    "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
    "TAG_NAME": By.TAG_NAME,
    "CLASS_NAME": By.CLASS_NAME,
}


class ElementReader:
    def __init__(self, relative_path):
        file_path = LEVEL_2_DIR / relative_path
        self.elements = {}

        with open(file_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # return a dictionary of element name and its locator tuple (By, value)
                self.elements[row["name"]] = (
                    BY_MAP[row["by"]],
                    row["value"]
                )

    def get(self, name):
        return self.elements[name] # (By, value)
