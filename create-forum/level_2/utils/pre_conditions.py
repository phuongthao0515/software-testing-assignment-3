import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PreConditions:
    """Set up pre-conditions for test cases"""
    
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait, config, elements):
        self.driver = driver
        self.wait = wait
        self.config = config
        self.elements = elements

    def login(self, base_url=None):
        if base_url is None:
            base_url = self.config["base_url"]

        self.driver.get(base_url)
        self.wait.until(
            EC.element_to_be_clickable(self.elements.get("login_link"))
        ).click()
        
        time.sleep(1.5)  # Small pause to allow login page to load

        self.wait.until(
            EC.element_to_be_clickable(self.elements.get("username_field"))
        ).send_keys(self.config["username"])

        self.wait.until(
            EC.element_to_be_clickable(self.elements.get("password_field"))
        ).send_keys(self.config["password"])

        self.wait.until(
            EC.element_to_be_clickable(self.elements.get("login_button"))
        ).submit()
        print("LOGIN SUCCESS")


    def navigate_to_edited_course(self):
        element = self.wait.until(
            EC.element_to_be_clickable(self.elements.get("course_link"))
        )

        # Scroll element into view before clicking
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", 
            element
        )
        
        # Small pause to allow any scroll animations to finish
        time.sleep(1) 
        element.click()
        print("COURSE OPENED")
        
        time.sleep(1)  # Small pause to allow course page to load
        self.wait.until(
            EC.element_to_be_clickable(self.elements.get("edit_mode_button"))
        ).click()
        print("EDIT MODE ALREADY ENABLED")
        
    def set_up(self, base_url=None):
        self.login(base_url)
        self.navigate_to_edited_course()
        
