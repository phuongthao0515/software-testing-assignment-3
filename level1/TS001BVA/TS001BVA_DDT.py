import csv
import os
import re
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL        = "https://sandbox.moodledemo.net"
LOGIN_URL       = BASE_URL + "/login/index.php"
COURSE_EDIT_URL = BASE_URL + "/course/edit.php?category=0"
USERNAME        = "manager"
PASSWORD        = "sandbox24"
DATA_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "TS001BVA_data.csv")

# Short run-time token appended to every shortname so reruns do not collide
# with courses created in earlier runs.
RUN_TOKEN = str(int(time.time()))[-5:]


def expand(value):
    """Expand "<char>x<count>" shorthand into a literal string.

    "Ax5" -> "AAAAA". Any value that does not match the shorthand is
    returned unchanged.
    """
    m = re.fullmatch(r"(.)x(\d+)", value or "")
    if m:
        return m.group(1) * int(m.group(2))
    return value or ""


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class TS001BVADataDriven(unittest.TestCase):
    """Data-driven BVA suite for the Moodle Add-Course form."""

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
        WebDriverWait(d, 30).until(lambda dr: "login/index.php" not in dr.current_url)

    def test_all_rows(self):
        rows = load_rows(DATA_FILE)
        self.assertTrue(rows, "no rows loaded from %s" % DATA_FILE)
        for row in rows:
            with self.subTest(test_id=row["test_id"]):
                self._run_row(row)

    def _run_row(self, row):
        d = self.driver
        d.get(COURSE_EDIT_URL)

        fullname  = expand(row["fullname"])
        # Make shortname unique per row + per run.
        shortname = expand(row["shortname"]) + "_" + row["test_id"][-3:] + RUN_TOKEN

        fn = d.find_element(By.ID, "id_fullname")
        fn.clear()
        fn.send_keys(fullname)

        sn = d.find_element(By.ID, "id_shortname")
        sn.clear()
        sn.send_keys(shortname)

        d.find_element(By.ID, "id_saveanddisplay").click()

        # Wait for the edit URL to change (success redirect or validation
        # re-render). If nothing changes within 15s, fall through to the
        # assertion below which will produce a meaningful failure.
        try:
            WebDriverWait(d, 15).until(lambda dr: dr.current_url != COURSE_EDIT_URL)
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
            body = d.find_element(By.TAG_NAME, "body").text
            self.assertRegex(
                body, pattern,
                "row %s: expected body text ~%r" % (row["test_id"], pattern),
            )
        else:
            self.fail("row %s: unknown expected_result %r"
                      % (row["test_id"], expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
