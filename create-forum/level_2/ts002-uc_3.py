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


PROJECT_DIR = Path(__file__).resolve().parents[1]


class TestUsecase_Cancel(unittest.TestCase):
    """Test the use case that the user cancels creating a new forum after filling in some fields."""
    
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
        
        
    def verify_result(self, page: NewForumPage, row: dict):
        # Should turn back to the course page without creating a new forum
        course_name = page.get_CourseName()
        self.assertEqual("My first course", course_name)
        
        
    def execute_testcase(self, row: dict):
        print("\n===================================")
        print("TC: ", row["TC_ID"])
        
        # OPEN CREATE FORUM PAGE
        page = NewForumPage(self.driver, self.wait, self.config, self.elements)
        page.open_create_forum_page()

        # FORUM NAME
        page.fill_TextField("forum_name_field", row["ForumName"])

        page.click_cancel()
        
        self.verify_result(page, row)
        
        time.sleep(1.5) # Small pause before next test case
        
    
    def test_cancel_create_forum(self):
        pre_conditions = PreConditions(self.driver, self.wait, self.config, self.elements)
        pre_conditions.set_up()
        
        # READ TEST DATA FROM CSV
        csv_file = PROJECT_DIR / "data" / "ts002-uc_3.csv"
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
