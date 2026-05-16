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
CONFIG_FILE = os.path.join(HERE, "TS001UC_config.ini")
DATA_FILE   = os.path.join(HERE, "TS001UC_data.csv")

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

URLS = cfg["urls"]
CREDS = cfg["credentials"]
FRAG = cfg["url_fragments"]
WAIT = cfg["wait"]

RUN_TOKEN = str(int(time.time()))[-5:]


def L(key):
    raw = cfg["locators"][key]
    by_str, _, value = raw.partition(":")
    return (BY_MAP[by_str.strip()], value)


def _save_btn_locator(value):
    key = "save_button_" + (value.strip() or "display")
    return L(key)


def _load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _unique(base, suffix):
    if not base:
        return ""
    return base + "_" + RUN_TOKEN + suffix


def _ensure_menu(driver):
    if driver.find_elements(*L("nav_site_admin")):
        return
    if driver.find_elements(*L("nav_my_courses")):
        return
    triggers = driver.find_elements(*L("nav_more_trigger"))
    if triggers:
        triggers[0].click()


def _navigate(driver, nav_route):
    if nav_route == "site_admin":
        driver.get(URLS["course_edit_url"])
        return
    if nav_route == "my_courses":
        driver.get(URLS["base_url"] + "/my/courses.php")
        WebDriverWait(driver, int(WAIT["submit_seconds"])).until(
            lambda d: d.find_elements(*L("create_new_course"))
        )
        driver.find_element(*L("create_new_course")).click()
        WebDriverWait(driver, int(WAIT["submit_seconds"])).until(
            lambda d: FRAG["edit_page"] in d.current_url
        )
        return
    raise ValueError("Unknown nav_route: " + nav_route)


def _fill(driver, locator, value):
    if not value:
        return
    el = driver.find_element(*locator)
    el.clear()
    el.send_keys(value)


def _wait_off_edit(driver, timeout=None):
    if timeout is None:
        timeout = int(WAIT["submit_seconds"])
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: FRAG["edit_page"] not in d.current_url
        )
    except TimeoutException:
        pass


def _flow_happy(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, L("fullname_field"),  row["fullname"])
    _fill(driver, L("shortname_field"), _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(*_save_btn_locator(row["save_btn"] or "display")).click()
    _wait_off_edit(driver)


def _flow_cancel(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, L("fullname_field"),  row["fullname"])
    _fill(driver, L("shortname_field"), _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(*L("save_button_cancel")).click()
    _wait_off_edit(driver)


def _flow_save_partial_then_edit(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, L("shortname_field"), _unique(row["shortname"], row["test_id"][-3:]))
    driver.find_element(*L("save_button_display")).click()
    time.sleep(int(WAIT["partial_save_seconds"]))
    _fill(driver, L("fullname_field"), row["fullname2"])
    driver.find_element(*L("save_button_display")).click()
    _wait_off_edit(driver)


def _flow_edit_after_save(driver, row):
    _navigate(driver, row["nav_route"])
    _fill(driver, L("fullname_field"),  row["fullname"])
    _fill(driver, L("shortname_field"),
          _unique(row["shortname"], row["test_id"][-3:] + "A"))
    driver.find_element(*L("save_button_display")).click()
    WebDriverWait(driver, int(WAIT["submit_seconds"])).until(
        lambda d: FRAG["view_page"] in d.current_url
    )
    m = re.search(r"[?&]id=(\d+)", driver.current_url)
    if not m:
        raise RuntimeError("Cannot extract course id from URL: "
                           + driver.current_url)
    driver.get(URLS["base_url"] + FRAG["edit_by_id_template"] + m.group(1))
    _fill(driver, L("shortname_field"),
          _unique(row["shortname2"], row["test_id"][-3:] + "B"))
    driver.find_element(*L("save_button_display")).click()
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
            self.assertNotIn(
                FRAG["edit_page"], self.driver.current_url,
                "row %s: expected to leave the edit page; URL is %s"
                % (row["test_id"], self.driver.current_url),
            )
            return

        body = self.driver.find_element(*L("body")).text
        self.assertRegex(
            body, row["expected_pattern"],
            "row %s: expected body text matching %r"
            % (row["test_id"], row["expected_pattern"]),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
