import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)
sys.path.append(PROJECT_ROOT)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from colorama import Fore, Style, init
import argparse, unittest, csv, time

from common.precondition import run_precondition
from common.utils import MESSAGES

class TS_003(unittest.TestCase):
    def setUp(self):
        driver_path = os.path.abspath("../webdriver/chromedriver.exe")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(3)
        self.verificationErrors = []
        run_precondition(self.driver)

    
    def set_input_value(self, by, locator, value):
        element = self.driver.find_element(by, locator)
        element.clear()
        self.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input'));
            arguments[0].dispatchEvent(new Event('change'));
        """, element, value)
        return element


    def run_test_case(self, row):
        print(f"Run {row['tc_id']}...")
        
        # ---------- Extract test data ----------
        username = row["username"]
        new_password = row["new_password"]
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]
        expected_results = [item.strip() for item in row["expected_results"].split(";")]

        print("\tUsername:", username)
        print("\tNew Password:", new_password)
        print("\tFirst Name:", first_name)
        print("\tLast Name:", last_name)
        print("\tEmail:", email)
        print("\tExpected Results:", expected_results)

        is_success = True
        if len(expected_results) == 1 and expected_results[0] == MESSAGES["SUCCESS"]:
            is_success = True
        else:
            is_success = False

        # ---------- Fill input ----------
        self.driver.get("https://sandbox51.moodledemo.net/")
        self.driver.find_element(By.LINK_TEXT, "Site administration").click()
        self.driver.find_element(By.LINK_TEXT, "Users").click()
        self.driver.find_element(By.LINK_TEXT, "Add a new user").click()

        self.driver.find_element(By.ID, "id_username").clear()
        self.set_input_value(By.ID, "id_username", username)
        password_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-passwordunmask="edit"]')
        self.driver.execute_script("arguments[0].click();", password_btn)
        self.set_input_value(By.ID, "id_newpassword", new_password)
        self.set_input_value(By.ID, "id_firstname", first_name)
        self.set_input_value(By.ID, "id_lastname", last_name)
        self.set_input_value(By.ID, "id_email", email)

        submit_btn = self.driver.find_element(By.ID, "id_submitbutton")
        self.driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # ---------- Verify results ----------
        if is_success:
            try:
                alert_text = self.driver.find_element(By.CSS_SELECTOR, "div.alert").text
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                assert "user.php" in self.driver.current_url
                for expected in expected_results:
                    assert expected in alert_text
                assert email in page_text
                print(Fore.GREEN + "PASS" + Style.RESET_ALL)
            except AssertionError as e:
                self.verificationErrors.append(str(e))
                print(Fore.RED + "FAIL" + Style.RESET_ALL)
        else:
            actual_errors = self.get_all_error_messages()
            try:
                for expected in expected_results:
                    assert expected in actual_errors
                print(Fore.GREEN + "PASS" + Style.RESET_ALL)
            except AssertionError as e:
                self.verificationErrors.append(str(e))
                print(Fore.RED + "FAIL" + Style.RESET_ALL)
    

    def get_all_error_messages(self):
        error_selectors = [
            "id_error_username",
            "id_error_firstname",
            "id_error_lastname",
            "id_error_email",
            "id_error_newpassword"
        ]
        actual_errors = []

        for element_id in error_selectors:
            try:
                text = self.driver.find_element(By.ID, element_id).text
                if text:
                    actual_errors.append(text)
            except NoSuchElementException:
                pass
        
        try:
            errors = self.driver.find_elements(By.XPATH, "//p[@class='errormessage']")
            for err in errors:
                text = err.text
                if text:
                    actual_errors.append(text)
        except NoSuchElementException:
            pass
        print("\tActual Errors:", actual_errors)
        return actual_errors


    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

def generate_test_case(row):
    def test(self):
        self.run_test_case(row)
    return test

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--bva", action="store_true", help="Run BVA test cases")
    parser.add_argument("--ecp", action="store_true", help="Run ECP test cases")
    parser.add_argument("--dt", action="store_true", help="Run Decision Table test cases")
    parser.add_argument("--all", action="store_true", help="Run all test cases")

    args = parser.parse_args()

    csv_files = []

    if args.bva:
        csv_files.append("../data/ts-003-bva-data.csv")
    if args.ecp:
        csv_files.append("../data/ts-003-ecp-data.csv")
    if args.dt:
        csv_files.append("../data/ts-003-dt-data.csv")
    if args.all:
        csv_files.extend([
            "../data/ts-003-bva-data.csv",
            "../data/ts-003-ecp-data.csv",
            "../data/ts-003-dt-data.csv"
        ])

    # default
    if not csv_files:
        print("No option selected. Running all test cases.")
        csv_files.extend([
            "../data/ts-003-bva-data.csv",
            "../data/ts-003-ecp-data.csv",
            "../data/ts-003-dt-data.csv"
        ])

    # remove duplicates
    csv_files = list(set(csv_files))

    # load test cases from CSV files and dynamically create test methods
    for csv_path in csv_files:
        csv_file_path = os.path.abspath(csv_path)
        print(f"\nLoading: {csv_file_path}")
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader, start=1):
                test_method = generate_test_case(row)
                test_name = "test_" + row["tc_id"]
                setattr(TS_003, test_name, test_method)

    unittest.main(argv=['first-arg-is-ignored'])