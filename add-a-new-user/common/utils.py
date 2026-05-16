import csv
import os

from selenium.webdriver.common.by import By


def load_csv_config(path):
    data = {}
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data[row["key"]] = row
    return data


APP_CONFIG = load_csv_config("../config/app.csv")

LOCATORS = load_csv_config("../config/locator.csv")

BY_MAPPING = {
    "ID": By.ID,
    "LINK_TEXT": By.LINK_TEXT,
    "CSS_SELECTOR": By.CSS_SELECTOR,
    "XPATH": By.XPATH,
    "NAME": By.NAME,
    "TAG_NAME": By.TAG_NAME
}

MESSAGES = {
    "SUCCESS": "Changes saved"
}