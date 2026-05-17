import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PreConditions:
    """Set up pre-conditions for test cases"""
    
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def login(self, base_url):
        self.driver.get(base_url)
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        
        time.sleep(1.5)  # Small pause to allow login page to load
        self.wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys("teacher")
        
        self.wait.until(EC.element_to_be_clickable((By.ID, "password"))).send_keys("sandbox24")
        
        self.wait.until(EC.element_to_be_clickable((By.ID, "login"))).submit()
        print("LOGIN SUCCESS")


    def navigate_to_edited_course(self):
        # driver.save_screenshot("debug_before_click.png")
        element = self.driver.find_element(By.LINK_TEXT, "My first course")
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
        self.wait.until(EC.element_to_be_clickable((By.NAME, "setmode"))).click()
        print("EDIT MODE ALREADY ENABLED")
        
    def set_up(self, base_url):
        self.login(base_url)
        self.navigate_to_edited_course()
        