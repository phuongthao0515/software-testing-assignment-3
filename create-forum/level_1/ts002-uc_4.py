import csv
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from utils.new_forum_page import NewForumPage
from utils.pre_conditions import PreConditions


class TestUsecase_Submit2(unittest.TestCase):
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
        self.base_url = "https://sandbox.moodledemo.net"
        self.wait = WebDriverWait(self.driver, 10)
        
        
    def verify_result(self, page: NewForumPage, row: dict):
        forum_name = self.wait.until(EC.presence_of_element_located((By.XPATH, "//li[@id='module-7']/div[2]/div[2]/div[2]/div/div/span/a"))).text
        self.assertEqual(row["ForumName"] + " Forum", forum_name)
        
        
    def execute_testcase(self, row: dict):
        print("\n===================================")
        print("TC: ", row["TC_ID"])
        
        # OPEN CREATE FORUM PAGE
        page = NewForumPage(self.driver, self.wait)
        page.open_create_forum_page()

        # FORUM NAME
        page.fill_TextField(By.ID, "id_name", row["ForumName"])

        page.click_return_to_course_btn()
        
        self.verify_result(page, row)
        
        time.sleep(1.5) # Small pause before next test case

    
    def test_submit_and_return(self):
        pre_conditions = PreConditions(self.driver, self.wait)
        pre_conditions.set_up(self.base_url)
        
        # READ TEST DATA FROM CSV
        csv_file = "../data/ts002-uc_4.csv"
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
