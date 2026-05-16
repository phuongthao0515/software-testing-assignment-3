import configparser
import csv
import os
import re
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HERE        = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "TS001BVA_config.ini")
DATA_FILE   = os.path.join(HERE, "TS001BVA_data.csv")

BY_MAP = {
    "id":                By.ID,
    "name":              By.NAME,
    "xpath":             By.XPATH,
    "css":               By.CSS_SELECTOR,
    "link_text":         By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "tag_name":          By.TAG_NAME,
    "class_name":        By.CLASS_NAME,
}

cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE, encoding="utf-8")

URLS             = cfg["urls"]
CREDS            = cfg["credentials"]
WAIT             = cfg["wait"]
SUCCESS_URL_FRAG = cfg["expected"]["success_url"]

RUN_TOKEN = str(int(time.time()))[-5:]


def L(key):
    raw = cfg["locators"][key]
    by_str, _, value = raw.partition(":")
    return (BY_MAP[by_str.strip()], value)


def expand(value):
    m = re.fullmatch(r"(.)x(\d+)", value or "")
    if m:
        return m.group(1) * int(m.group(2))
    return value or ""


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TS001BVADataDriven(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(int(WAIT["implicit_seconds"]))
        cls._login()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def _login(cls):
        d = cls.driver
        d.get(URLS["login_url"])
        d.find_element(*L("login_username")).clear()
        d.find_element(*L("login_username")).send_keys(CREDS["username"])
        d.find_element(*L("login_password")).clear()
        d.find_element(*L("login_password")).send_keys(CREDS["password"])
        d.find_element(*L("login_submit")).click()
        WebDriverWait(d, int(WAIT["login_seconds"])).until(
            lambda dr: "login/index.php" not in dr.current_url
        )

    def test_all_rows(self):
        rows = load_rows(DATA_FILE)
        self.assertTrue(rows, "no rows loaded from %s" % DATA_FILE)
        for row in rows:
            with self.subTest(test_id=row["test_id"]):
                self._run_row(row)

    def _run_row(self, row):
        d = self.driver
        d.get(URLS["course_edit_url"])

        fullname  = expand(row["fullname"])
        shortname = expand(row["shortname"]) + "_" + row["test_id"][-3:] + RUN_TOKEN

        fn = d.find_element(*L("fullname_field"))
        fn.clear()
        fn.send_keys(fullname)

        sn = d.find_element(*L("shortname_field"))
        sn.clear()
        sn.send_keys(shortname)

        d.find_element(*L("save_button")).click()

        try:
            WebDriverWait(d, int(WAIT["submit_seconds"])).until(
                lambda dr: SUCCESS_URL_FRAG in dr.current_url
            )
        except TimeoutException:
            pass

        expected = row["expected_result"].strip().upper()
        pattern  = row["expected_pattern"]

        if expected == "SUCCESS":
            self.assertRegex(
                d.current_url, pattern,
                "row %s: expected URL ~%r, got %r" % (row["test_id"], pattern, d.current_url),
            )
        elif expected == "ERROR":
            body = d.find_element(*L("body")).text
            self.assertRegex(
                body, pattern,
                "row %s: expected body text ~%r" % (row["test_id"], pattern),
            )
        else:
            self.fail("row %s: unknown expected_result %r"
                      % (row["test_id"], expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
