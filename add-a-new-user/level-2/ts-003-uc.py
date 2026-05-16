
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)
sys.path.append(PROJECT_ROOT)

import csv
import time
import unittest

from colorama import Fore, Style
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from common.precondition import run_precondition_lv2
from common.utils import APP_CONFIG, LOCATORS, BY_MAPPING, MESSAGES


class TS_003_UC(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(3)
        self.verificationErrors = []


    def set_input_value(self, by, locator, value):
        element = self.driver.find_element(by, locator)
        element.clear()
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input'));
            arguments[0].dispatchEvent(new Event('change'));
        """, element, value)
        return element


    def open_add_user_page(self):
        self.driver.get(APP_CONFIG['base_url']['value'])
        self.driver.find_element(BY_MAPPING[LOCATORS['site_admin']['by']], LOCATORS['site_admin']['value']).click()
        self.driver.find_element(BY_MAPPING[LOCATORS['users']['by']], LOCATORS['users']['value']).click()
        self.driver.find_element(BY_MAPPING[LOCATORS['add_user']['by']], LOCATORS['add_user']['value']).click()


    def open_add_user_page_indirect(self):
        self.driver.get(APP_CONFIG['base_url']['value'])
        self.driver.find_element(BY_MAPPING[LOCATORS['site_admin']['by']], LOCATORS['site_admin']['value']).click()
        self.driver.find_element(BY_MAPPING[LOCATORS['users']['by']], LOCATORS['users']['value']).click()
        self.driver.find_element(BY_MAPPING[LOCATORS['browse_list_users']['by']], LOCATORS['browse_list_users']['value']).click()
        self.driver.find_element(BY_MAPPING[LOCATORS['add_user']['by']], LOCATORS['add_user']['value']).click()


    def fill_required_fields(self, row):
        self.set_input_value(BY_MAPPING[LOCATORS['username']['by']], LOCATORS['username']['value'], row["username"])

        password_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-passwordunmask="edit"]')
        self.driver.execute_script("arguments[0].click();", password_btn)

        self.set_input_value(BY_MAPPING[LOCATORS['new_password']['by']], LOCATORS['new_password']['value'], row["new_password"])

        self.set_input_value(BY_MAPPING[LOCATORS['firstname']['by']], LOCATORS['firstname']['value'], row["first_name"])

        self.set_input_value(BY_MAPPING[LOCATORS['lastname']['by']], LOCATORS['lastname']['value'], row["last_name"])

        self.set_input_value(BY_MAPPING[LOCATORS['email']['by']], LOCATORS['email']['value'], row["email"])

    def fill_optional_fields(self, row):
        if row["city"]:
            self.set_input_value(BY_MAPPING[LOCATORS['city']['by']], LOCATORS['city']['value'], row["city"])

        if row["country"]:
            country = self.driver.find_element(BY_MAPPING[LOCATORS['country']['by']], LOCATORS['country']['value'])
            country.send_keys(row["country"])

    def click_create(self):
        submit_btn = self.driver.find_element(BY_MAPPING[LOCATORS['submit_btn']['by']], LOCATORS['submit_btn']['value'])
        self.driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", submit_btn)

    def click_cancel(self):
        cancel_btn = self.driver.find_element(BY_MAPPING[LOCATORS['cancel_btn']['by']], LOCATORS['cancel_btn']['value'])
        self.driver.execute_script("arguments[0].scrollIntoView();", cancel_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();",cancel_btn)

    # Verification
    def get_all_error_messages(self):
        error_selectors = [
            error_id['value'] for key, error_id in LOCATORS.items() if key.startswith("error_")
        ]
        actual_errors = []

        for element_id in error_selectors:
            try:
                text = self.driver.find_element(By.ID, element_id).text
                if text:
                    actual_errors.append(text)
            except NoSuchElementException:
                pass
        print("\tActual Errors:", actual_errors)
        return actual_errors

    def verify_success(self, row):
        expected_results = [
            item.strip()
            for item in row["expected_results"].split(";")
        ]
        print("\tExpected Results:", expected_results)
        try:
            alert_text = self.driver.find_element(BY_MAPPING[LOCATORS['alert']['by']], LOCATORS['alert']['value']).text
            assert "user.php" in self.driver.current_url
            for expected in expected_results:
                assert expected in alert_text
            
            print(Fore.GREEN + "PASS" + Style.RESET_ALL)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
            print(Fore.RED + "FAIL" + Style.RESET_ALL)

    def verify_errors(self, row, is_check_error_message_field=False):
        if is_check_error_message_field:
            expected_results = [
                item.strip()
                for item in row["error_message_1"].split(";")
            ]
        else:
            expected_results = [
                item.strip()
                for item in row["expected_results"].split(";")
            ]
        print("\tExpected Results:", expected_results)
        actual_errors = self.get_all_error_messages()

        for expected in expected_results:
            assert expected in actual_errors
        print(Fore.GREEN + "PASS" + Style.RESET_ALL)

    # Use Case Flows

    def flow_main(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.click_create()
        self.verify_success(row)

    def flow_invalid_login_retry(self, row):
        # wrong login
        self.driver.get(APP_CONFIG['login_url']['value'])
        self.set_input_value(BY_MAPPING[LOCATORS['log_in_username']['by']], LOCATORS['log_in_username']['value'], row["wrong_username"])
        self.set_input_value(BY_MAPPING[LOCATORS['log_in_password']['by']], LOCATORS['log_in_password']['value'], row["wrong_password"])
        self.driver.find_element(BY_MAPPING[LOCATORS['login_btn']['by']], LOCATORS['login_btn']['value']).click()

        # correct login
        run_precondition_lv2(self.driver)
        
        # continue use case
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.click_create()
        self.verify_success(row)

    def flow_indirect_navigation(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page_indirect()
        self.fill_required_fields(row)
        self.click_create()
        self.verify_success(row)

    def flow_invalid_data(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.click_create()
        self.verify_errors(row)

    def flow_cancel_creation(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.click_cancel()
        assert "user.php" in self.driver.current_url
        print(Fore.GREEN + "PASS" + Style.RESET_ALL)

    def flow_optional_fields(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.fill_optional_fields(row)
        self.click_create()
        self.verify_success(row)

    def flow_retry_after_invalid(self, row):
        run_precondition_lv2(self.driver)
        self.open_add_user_page()
        self.fill_required_fields(row)
        self.click_create()
        self.verify_errors(row, is_check_error_message_field=True)

        self.set_input_value(BY_MAPPING[LOCATORS['username']['by']], LOCATORS['username']['value'], row["correct_username"])
        self.set_input_value(By.ID, "id_email", row["correct_email"])

        self.click_create()
        self.verify_success(row)

    # Main Runner
    def run_test_case(self, row):
        print(f"Run {row['tc_id']}...")
        flow = row["flow"]

        if flow == "main_flow":
            self.flow_main(row)

        elif flow == "invalid_login_retry":
            self.flow_invalid_login_retry(row)

        elif flow == "indirect_navigation":
            self.flow_indirect_navigation(row)

        elif flow == "invalid_data":
            self.flow_invalid_data(row)

        elif flow == "cancel_creation":
            self.flow_cancel_creation(row)

        elif flow == "optional_fields":
            self.flow_optional_fields(row)

        elif flow == "retry_after_invalid":
            self.flow_retry_after_invalid(row)

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


def generate_test_case(row):
    def test(self):
        self.run_test_case(row)
    return test


if __name__ == "__main__":
    csv_file_path = os.path.abspath("../data/ts-003-uc-data.csv")

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            test_method = generate_test_case(row)
            test_name = "test_" + row["tc_id"]
            setattr(TS_003_UC, test_name, test_method)
    unittest.main()