import csv
import time
import unittest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.new_forum_page import NewForumPage
from utils.pre_conditions import PreConditions


PROJECT_DIR = Path(__file__).resolve().parents[1]


class TestUsecase_HappyPath(unittest.TestCase):
    """Test the use case that the user fills in all fields and submits the form."""

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
        self.assertEqual(
                row["ForumName"],
                page.get_CreatedForumName()
            )
        print("SUCCESS VERIFIED")
        
        
    def execute_testcase(self, row: dict):
        print("\n===================================")
        print("TC: ", row["TC_ID"])
        
        # OPEN CREATE FORUM PAGE
        page = NewForumPage(self.driver, self.wait)
        page.open_create_forum_page()
        
        # FORUM
        page.fill_TextField(By.ID, "id_name", row["ForumName"])
        should_show_description = row["DisplayDesc"] == "YES"
        page.fill_ForumDescription(row["ForumDesc"], should_show_description)
        page.fill_ForumType(row["ForumType"])
        
        page.fill_Availability(row)

        page.fill_Attachments_WordCount(row["MaxBytes"], row["MaxAttcm"], row["DisplayWrdCnt"])
        
        page.fill_Subscription_Tracking(row["ForceSub"], row["ReadTracking"])
        
        page.fill_DiscussionLocking(row["LockDscEnbl"], row["LockDscNum"], row["LockDscTime"])
        
        page.fill_PostThresholdBlocking(row["BlockPeriod"], row["BlockAfter"], row["WarnAfter"])
        
        page.fill_WholeForumGrading(row)
        
        page.fill_Ratings(row)
        
        page.fill_CommonModuleSettings(row["Visible"], row["CmtNum"], row["Lang"], row["GroupMode"])
        
        page.fill_RestrictAccess(row["AvailCond"], row["MinGradePercent"])
        
        page.fill_CompleteConditions(row["CompleteCond"])
        
        page.fill_Tags(row["Tag"])
        
        page.fill_Competency(row["Competency"])
        
        page.fill_SendNoti(row["SendNoti"])
        
        page.submit_form()
        
        self.verify_result(page, row)
        
        time.sleep(1.5) # Small pause before next test case
        
    
    def test_happy_path(self):
        pre_conditions = PreConditions(self.driver, self.wait)
        pre_conditions.set_up(self.base_url)
        
        # READ TEST DATA FROM CSV
        csv_file = PROJECT_DIR / "data" / "ts002-uc_2.csv"
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
