"""Reliability (repeatability) test for the Moodle Add-Course flow.

Runs the same create-course operation N times and asserts that the
observed success rate meets the configured threshold.
"""

import csv
import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL        = "https://sandbox.moodledemo.net"
LOGIN_URL       = BASE_URL + "/login/index.php"
COURSE_EDIT_URL = BASE_URL + "/course/edit.php?category=0"
USERNAME        = "manager"
PASSWORD        = "sandbox24"

HERE       = os.path.dirname(os.path.abspath(__file__))
DATA_FILE  = os.path.join(HERE, "reliability_data.csv")
REPORT_FILE = os.path.join(HERE, "reliability_report.csv")

RUN_TOKEN = str(int(time.time()))[-5:]


def load_config(path):
    with open(path, newline="", encoding="utf-8") as f:
        return next(csv.DictReader(f))


class ReliabilityTest(unittest.TestCase):

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
        d.find_element(By.ID, "username").send_keys(USERNAME)
        d.find_element(By.ID, "password").send_keys(PASSWORD)
        d.find_element(By.ID, "loginbtn").click()
        WebDriverWait(d, 30).until(lambda dr: "login/index.php" not in dr.current_url)

    def _create_course(self, fullname, shortname):
        d = self.driver
        d.get(COURSE_EDIT_URL)
        fn = d.find_element(By.ID, "id_fullname")
        fn.clear(); fn.send_keys(fullname)
        sn = d.find_element(By.ID, "id_shortname")
        sn.clear(); sn.send_keys(shortname)
        d.find_element(By.ID, "id_saveanddisplay").click()
        WebDriverWait(d, 15).until(lambda dr: "course/edit.php" not in dr.current_url)
        return "course/view.php" in d.current_url

    def test_reliability(self):
        cfg        = load_config(DATA_FILE)
        n          = int(cfg["iterations"])
        threshold  = float(cfg["success_threshold"])
        fullname   = cfg["fullname"]
        prefix     = cfg["shortname_prefix"]

        passed = 0
        results = []
        for i in range(1, n + 1):
            shortname = "%s_%s_%03d" % (prefix, RUN_TOKEN, i)
            start = time.time()
            ok = False
            err = ""
            try:
                ok = self._create_course(fullname, shortname)
            except (TimeoutException, WebDriverException) as e:
                err = type(e).__name__
            elapsed = round(time.time() - start, 2)
            if ok:
                passed += 1
            results.append((i, shortname, "PASS" if ok else "FAIL", elapsed, err))
            print("iter %02d  %s  %.2fs  %s" %
                  (i, "PASS" if ok else "FAIL", elapsed, err))

        rate = passed / n
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["iteration", "shortname", "result", "seconds", "error"])
            w.writerows(results)
            w.writerow([])
            w.writerow(["total", n, "passed", passed, "success_rate", "%.2f" % rate])

        print("\nReliability: %d/%d passed (%.2f%%), threshold %.2f%%"
              % (passed, n, rate * 100, threshold * 100))
        self.assertGreaterEqual(
            rate, threshold,
            "success rate %.2f below threshold %.2f" % (rate, threshold))


if __name__ == "__main__":
    unittest.main(verbosity=2)
