import csv
import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL        = "https://sandbox.moodledemo.net"
LOGIN_URL       = BASE_URL + "/login/index.php"
COURSE_EDIT_URL = BASE_URL + "/course/edit.php?category=0"
USERNAME        = "manager"
PASSWORD        = "sandbox24"
DATA_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "TS001ECP_data.csv")

RUN_TOKEN = str(int(time.time()))[-5:]


def _load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _unique_shortname(base):
    if not base:
        return ""
    return base + "_" + RUN_TOKEN


def _fill(driver, field_id, value):
    if not value:
        return
    el = driver.find_element(By.ID, field_id)
    el.clear()
    el.send_keys(value)


def _clear_category(driver):
    chips = driver.find_elements(
        By.XPATH,
        "//span[starts-with(@id,'form_autocomplete_selection-')]/span",
    )
    for chip in chips:
        try:
            chip.click()
        except WebDriverException:
            continue

    try:
        Select(driver.find_element(By.ID, "id_category")).select_by_value("")
    except (NoSuchElementException, WebDriverException):
        pass


class TS001ECPDataDriven(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(30)
        cls._login()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def _login(cls):
        d = cls.driver
        d.get(LOGIN_URL)
        d.find_element(By.ID, "username").clear()
        d.find_element(By.ID, "username").send_keys(USERNAME)
        d.find_element(By.ID, "password").clear()
        d.find_element(By.ID, "password").send_keys(PASSWORD)
        d.find_element(By.ID, "loginbtn").click()
        WebDriverWait(d, 30).until(
            lambda dr: "login/index.php" not in dr.current_url
        )

    def test_all_rows(self):
        rows = _load_rows(DATA_FILE)
        self.assertTrue(rows, "no rows loaded from %s" % DATA_FILE)
        for row in rows:
            with self.subTest(test_id=row["test_id"]):
                self._run_row(row)

    def _run_row(self, row):
        d = self.driver
        d.get(COURSE_EDIT_URL)

        _fill(d, "id_fullname",  row["fullname"])
        _fill(d, "id_shortname", _unique_shortname(row["shortname"]))

        if row["clear_category"].strip().upper() == "Y":
            _clear_category(d)

        d.find_element(By.ID, "id_saveanddisplay").click()

        try:
            WebDriverWait(d, 15).until(
                lambda dr: "course/view.php" in dr.current_url
                or any(kw in dr.find_element(By.TAG_NAME, "body").text
                       for kw in ("Missing", "already used", "must supply"))
            )
        except TimeoutException:
            pass

        expected = row["expected_result"].strip().upper()
        pattern  = row["expected_pattern"]

        if expected == "SUCCESS":
            self.assertRegex(
                d.current_url, pattern,
                "row %s: expected URL ~%r, got %r"
                % (row["test_id"], pattern, d.current_url),
            )
        elif expected == "ERROR":
            body = d.find_element(By.TAG_NAME, "body").text
            self.assertRegex(
                body, pattern,
                "row %s: expected body text matching %r"
                % (row["test_id"], pattern),
            )
        else:
            self.fail("row %s: unknown expected_result %r"
                      % (row["test_id"], expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
