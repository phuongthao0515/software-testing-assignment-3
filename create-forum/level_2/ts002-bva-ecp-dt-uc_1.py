# -*- coding: utf-8 -*-
"""
Feature: Create a New Forum
Data-driven testcases for:
- Boundary Value Analysis (BVA)
- Equivalence Class Partitioning (ECP)
- Decision Table Testing (DT)
- Use Case Testing (UC) (some) 
"""

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


class TestBVA_ECP_DT_UC(unittest.TestCase):
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
        expected = row["ExpectedResult"]
        

        if expected == "SUCCESS":
            self.assertEqual(
                row["ForumName"],
                page.get_CreatedForumName()
            )
            print("SUCCESS VERIFIED")
            
        elif expected == "FORUM_NAME_ERR":
            self.assertEqual(
                ERR_MESSAGES["FORUM_NAME_ERR"],
                page.get_ForumNameError()
            )
            
        elif expected == "MAX_AUTO_FORUM_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["MAX_AUTO_GRADE_TO_PASS_ERR"],
                page.get_WFG_GradeToPassError()
            )
        
        elif expected == "MAX_AUTO_RATINGS_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["MAX_AUTO_GRADE_TO_PASS_ERR"],
                page.get_R_GradeToPassError()
            )
            
        elif expected == "MAX_MANUAL_RATINGS_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["MAX_MANUAL_GRADE_TO_PASS_ERR"].format(row["R_MaxGrade"]),
                page.get_R_GradeToPassError()
            )
        
        elif expected == "MAX_MANUAL_FORUM_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["MAX_MANUAL_GRADE_TO_PASS_ERR"].format(row["WFG_MaxGrade"]),
                page.get_WFG_GradeToPassError()
            )
            
        elif expected == "FORUM_GRADE_VALUE_ERR":
            self.assertEqual(
                ERR_MESSAGES["GRADE_VALUE_ERR"],
                page.get_WFG_ForumGradeValueError()
            )
        
        elif expected == "RATINGS_GRADE_VALUE_ERR":
            self.assertEqual(
                ERR_MESSAGES["GRADE_VALUE_ERR"],
                page.get_R_GradeValueError()
            )

        elif expected == "AVAILABILITY_ERR":
            self.assertEqual(
                ERR_MESSAGES["AVAILABILITY_ERR"],
                page.get_AvailabilityError()
            )
        
        elif expected == "AGG_TYPE_ERR":
            self.assertEqual(
                ERR_MESSAGES["AGG_TYPE_ERR"],
                page.get_AggTypeError()
            )
        
        elif expected == "RATINGS_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["GRADE_TO_PASS_ERR"],
                page.get_R_GradeToPassError()
            )
        
        elif expected == "FORUM_GRADE_TO_PASS_ERR":
            self.assertEqual(
                ERR_MESSAGES["GRADE_TO_PASS_ERR"],
                page.get_WFG_GradeToPassError()
            )


    def execute_testcase(self, row):
        print("\n===================================")
        print("TC: ", row["TC_ID"])
        
        # OPEN CREATE FORUM PAGE
        page = NewForumPage(self.driver, self.wait, self.config, self.elements)
        page.open_create_forum_page()

        # FORUM NAME
        page.fill_TextField("forum_name_field", row["ForumName"])

        # AVAILABILITY 
        page.fill_Availability(row)

        # WHOLE FORUM GRADING
        page.fill_WholeForumGrading(row)
        
        # RATINGS
        page.fill_Ratings(row)

        page.submit_form()
        
        self.verify_result(page, row)
        
        time.sleep(1.5) # Small pause before next test case

    # MAIN TEST
    def test_forum_data_driven(self):
        # PREPARE ENVIRONMENT
        pre_conditions = PreConditions(self.driver, self.wait, self.config, self.elements)
        pre_conditions.set_up()

        # READ TEST DATA FROM CSV
        csv_file = PROJECT_DIR / "data" / "ts002-bva-ecp-dt-uc_1.csv"
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
                    

    # TEARDOWN
    def tearDown(self):
        print("\nTEST FINISHED")
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
