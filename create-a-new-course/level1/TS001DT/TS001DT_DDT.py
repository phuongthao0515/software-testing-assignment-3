# -*- coding: utf-8 -*-
"""
Level 1 Data-Driven Test - Decision Table suite (TS001DT).

Consolidates TC001015-TC001019 from Project #2 into a single
parameterised test driven by TS001DT_data.csv.

The decision table exercised here covers four input conditions for the
Moodle Add-Course form and the action each combination should trigger:

  Condition                 Action / expected message
  ------------------------- ---------------------------------------------
  fullname provided?        if No  -> "Missing full name"
  shortname provided?       if No  -> "Missing short name"
  shortname unique?         if No  -> "Short name is already used ..."
  category provided?        if No  -> "You must supply a value here"
  all of the above hold     -> course created, redirect to course/view.php

CSV columns
-----------
test_id           Original test case identifier.
fullname          Value sent to id_fullname (blank to skip the field).
shortname         Value sent to id_shortname (blank to skip the field).
clear_category    Y to remove the pre-selected category, N to leave it.
expected_result   SUCCESS or ERROR.
expected_pattern  Regex matched against current_url when SUCCESS, or
                  against the page body text when ERROR.

Uniqueness strategy
-------------------
Unlike BVA / UC, the DT suite *requires* two rows to share the same
shortname so the duplicate-shortname rule can be tested (TC001015
creates "DT01", TC001018 retries "DT01" and expects the duplicate
error). We therefore append ONLY a per-run token to each shortname:
within one run, identical CSV shortnames produce identical actual
shortnames; across runs, the token changes so reruns do not collide
with courses left over from earlier runs.

Differences vs the original Project #2 scripts
----------------------------------------------
* Login precondition (manager / sandbox24) is baked into setUpClass.
* TC001017's catch-all "^[\\s\\S]*$" assertion is replaced with a real
  expectation: "Missing short name".
* The category-clear step in TC001019 used a session-dynamic XPath
  ("form_autocomplete_selection-1776786870765-0"); this script uses a
  stable starts-with XPath plus a Select fallback.
* Removed Selenium IDE noise (duplicate clicks, unused google base_url,
  empty executable_path, the spurious post-save driver.get to a hard-
  coded view.php?id=N which produced a false-positive URL match).

Run
---
    pip install --upgrade selenium
    python TS001DT_DDT.py
"""
import csv
import os
import re
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
                               "TS001DT_data.csv")

# Per-run token shared across every row, so within a single run the same
# CSV shortname maps to the same actual shortname (enables the duplicate
# test), while across runs the token changes (avoids collision with
# previously-created courses).
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
    """Remove the pre-selected category from Moodle's autocomplete widget.

    The selection chip has an id of the form 'form_autocomplete_selection-<n>-0';
    the inner span is the close icon. We click it, then force the hidden
    Select element back to its empty option as a fallback.
    """
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


class TS001DTDataDriven(unittest.TestCase):
    """Data-driven Decision Table suite for the Moodle Add-Course form."""

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

        # Wait for either redirect to course/view.php (SUCCESS) or
        # form re-render on the edit page (ERROR).
        try:
            WebDriverWait(d, 15).until(
                lambda dr: dr.current_url != COURSE_EDIT_URL
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
