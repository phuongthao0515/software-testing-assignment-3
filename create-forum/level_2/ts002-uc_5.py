import csv
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.config_reader import read_key_value_csv
from utils.element_reader import ElementReader
from utils.new_forum_page import NewForumPage
from utils.pre_conditions import PreConditions
from utils.data import ERR_MESSAGES


PROJECT_DIR = Path(__file__).resolve().parents[1]


class TestUsecase_Reattempt(unittest.TestCase):
    """Test the use case that the user submits the form via the button "Save and return to course"."""
    
    def setUp(self):
        options = webdriver.ChromeOptions()

        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.password_manager_leak_detection": False,
                "autofill.profile_enabled": False                  
            }
        )
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")          
        options.add_argument("--password-store=basic")

        self.driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.config = read_key_value_csv("data/config.csv")
        self.elements = ElementReader("data/elements.csv")
        
        
    def verify_result(self, page: NewForumPage, result: str, forum_name=None):
        if result == "FORUM_NAME_ERR":
            self.assertEqual(ERR_MESSAGES[result], page.get_ForumNameError())
            print("ERROR MESSAGE VERIFIED")
        
        else:
            self.assertEqual(
                    forum_name,
                    page.get_CreatedForumName()
                )
            print("SUCCESS VERIFIED")
        
        
    def execute_testcase(self, row: dict):
        print("\n===================================")
        print("TC: ", row["TC_ID"])
        
        # OPEN CREATE FORUM PAGE
        page = NewForumPage(self.driver, self.wait, self.config, self.elements)
        page.open_create_forum_page()

        # Attempt 1: Empty forum name
        page.fill_TextField("forum_name_field", row["ForumName_Attempt1"])
        page.submit_form()
        self.verify_result(page, row["ExpectedResult_1"])
        
        # Attempt 2: Fill in a valid forum name and submit again
        page.fill_TextField("forum_name_field", row["ForumName_Attempt2"])
        page.submit_form()        
        self.verify_result(page, row["ExpectedResult_2"], row["ForumName_Attempt2"])
        
        time.sleep(1.5) # Small pause before next test case

    
    def test_reattempt(self):
        pre_conditions = PreConditions(self.driver, self.wait, self.config, self.elements)
        pre_conditions.set_up()
        
        # READ TEST DATA FROM CSV
        csv_file = PROJECT_DIR / "data" / "ts002-uc_5.csv"
        with open(
            csv_file,
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Start execution from a specific test case ID (for easier debugging)
                # if row["TC_ID"] <= "TC-002-001":  
                #     continue
                with self.subTest(data=row):    
                    self.execute_testcase(row)

                
    def tearDown(self):
        print("\nTEST FINISHED")
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
