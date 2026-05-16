import csv
import os
import re
import time
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL        = "https://sandbox.moodledemo.net"
LOGIN_URL       = BASE_URL + "/login/index.php"
COURSE_EDIT_URL = BASE_URL + "/course/edit.php?category=0"
HOME_URL        = BASE_URL + "/"
USERNAME        = "manager"
PASSWORD        = "sandbox24"
DATA_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "TS001UC_data.csv")

RUN_TOKEN = str(int(time.time()))[-5:]


def _load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _unique(base, suffix):
    if not base:
        return ""
    return base + "_" + RUN_TOKEN + suffix


def _ensure_menu(driver):
    if driver.find_elements(By.LINK_TEXT, "Site administration"):
        return
    if driver.find_elements(By.LINK_TEXT, "My courses"):
        return
    triggers = driver.find_elements(By.CSS_SELECTOR, "[id^='moremenu-dropdown-']")
    if triggers:
        triggers[0].click()


def _navigate(driver, nav_route):
    if nav_route == "site_admin":
        driver.get(COURSE_EDIT_URL)
        return
    if nav_route == "my_courses":
        driver.get(BASE_URL + "/my/courses.php")
        create_xpath = (
            "//a[normalize-space()='Create course']"
            " | //button[normalize-space()='Create course']"
        )
        WebDriverWait(driver, 30).until(
            lambda d: d.find_elements(By.XPATH, create_xpath)
        )
        driver.find_element(By.XPATH, create_xpath).click()
        WebDriverWait(driver, 30).until(
            lambda d: "course/edit.php" in d.current_url
        )
        return
    raise ValueError("Unknown nav_route: " + nav_route)


def _fill(driver, field_id, value):
    if not value:
        return
    el = driver.find_element(By.ID, field_id)
    el.clear()
    el.send_keys(value)


def _wait_off_edit(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "course/edit.php" not in d.current_url
        )
    except TimeoutException:
        pass


def _flow_happy(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, "id_fullname", row["fullname"])
    _fill(driver, "id_shortname", _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(By.ID, row["save_btn"] or "id_saveanddisplay").click()
    _wait_off_edit(driver)


def _flow_cancel(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, "id_fullname", row["fullname"])
    _fill(driver, "id_shortname", _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(By.ID, "id_cancel").click()
    _wait_off_edit(driver)


def _flow_save_partial_then_edit(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, "id_shortname", _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(By.ID, "id_saveanddisplay").click()
    time.sleep(3)
    _fill(driver, "id_fullname", row["fullname2"])
    driver.find_element(By.ID, "id_saveanddisplay").click()
    _wait_off_edit(driver)


def _flow_edit_after_save(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, "id_fullname", row["fullname"])
    _fill(driver, "id_shortname",
          _unique(row["shortname"], row["test_id"][-3:] + "A"))
    driver.find_element(By.ID, "id_saveanddisplay").click()
    WebDriverWait(driver, 30).until(
        lambda d: "course/view.php" in d.current_url
    )
    m = re.search(r"[?&]id=(\d+)", driver.current_url)
    if not m:
        raise RuntimeError("Cannot extract course id from URL: "
                           + driver.current_url)
    driver.get(BASE_URL + "/course/edit.php?id=" + m.group(1))
    _fill(driver, "id_shortname",
          _unique(row["shortname2"], row["test_id"][-3:] + "B"))
    driver.find_element(By.ID, "id_saveanddisplay").click()
    _wait_off_edit(driver)


FLOW_HANDLERS = {
    "HAPPY":                  _flow_happy,
    "CANCEL":                 _flow_cancel,
    "SAVE_PARTIAL_THEN_EDIT": _flow_save_partial_then_edit,
    "EDIT_AFTER_SAVE":        _flow_edit_after_save,
}


class TS001UCDataDriven(unittest.TestCase):

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
            label = dict(test_id=row["test_id"], flow=row["flow_type"])
            with self.subTest(**label):
                self._run_row(row)

    def _run_row(self, row):
        flow = row["flow_type"].strip().upper()
        handler = FLOW_HANDLERS.get(flow)
        if handler is None:
            self.fail("row %s: unknown flow_type %r"
                      % (row["test_id"], flow))

        handler(self.driver, row)

        if flow == "CANCEL":
            self.assertNotRegex(
                self.driver.current_url, r"course/edit\.php",
                "row %s: expected to leave the edit page; URL is %s"
                % (row["test_id"], self.driver.current_url),
            )
            return

        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertRegex(
            body, row["expected_pattern"],
            "row %s: expected body text matching %r"
            % (row["test_id"], row["expected_pattern"]),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
