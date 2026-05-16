# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import time

from common.utils import APP_CONFIG, LOCATORS, BY_MAPPING

    
def run_precondition(driver, username="admin", password="sandbox24", is_custom_loginfo=False):
    print("\nRun precondition...")
    driver.get("https://sandbox51.moodledemo.net/")

    wait = WebDriverWait(driver, 30)

    isLoggedIn = False
    try:
        driver.find_element(By.LINK_TEXT, "Log in")
        isLoggedIn = False

    except NoSuchElementException:
        isLoggedIn = True
    print(f"\tIs logged in: {isLoggedIn}")

    if isLoggedIn == True :
        print("\tAlready logged in, Log out to log in with admin account")
        driver.find_element(By.CSS_SELECTOR, "div.usermenu").click()
        driver.find_element(By.LINK_TEXT, "Log out").click()
        driver.get("https://sandbox51.moodledemo.net/")
    
    driver.find_element(By.LINK_TEXT, "Log in").click()
    for attempt in range(3):
        try:

            username_input = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            username_input.clear()
            username_input.send_keys("admin")

            password_input = wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )

            password_input.clear()
            password_input.send_keys("sandbox24")

            login_btn = wait.until(
                EC.presence_of_element_located((By.ID, "loginbtn"))
            )

            driver.execute_script(
                "arguments[0].click();",
                login_btn
            )

            break

        except StaleElementReferenceException:

            print("\tRetry login because stale element")

            time.sleep(1)

        except TimeoutException:

            print("\tTimeout while locating login form")

            time.sleep(1)

    driver.find_element(By.LINK_TEXT, "Site administration").click()
    element = driver.find_element(By.LINK_TEXT, "Site security settings")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(1)
    element.click()
    isChecked = driver.find_element(By.ID, "id_s__passwordpolicy").is_selected()
    print(f"\tPassword policy is selected: {isChecked}")

    if isChecked == True :
        print("\tPassword policy is selected, Uncheck it to run test cases")
        checkbox = driver.find_element(By.ID, "id_s__passwordpolicy")
        driver.execute_script("arguments[0].scrollIntoView();", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox)

        assert not driver.find_element(By.ID, "id_s__passwordpolicy").is_selected()

        save_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Save changes']")
        driver.execute_script("arguments[0].scrollIntoView();", save_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_btn)

    if is_custom_loginfo:
        driver.find_element(By.CSS_SELECTOR, "div.usermenu").click()
        driver.find_element(By.LINK_TEXT, "Log out").click()
        driver.get("https://sandbox51.moodledemo.net/")

        for attempt in range(3):
            try:

                username_input = wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )

                username_input.clear()
                username_input.send_keys(username)

                password_input = wait.until(
                    EC.presence_of_element_located((By.ID, "password"))
                )

                password_input.clear()
                password_input.send_keys(password)

                login_btn = wait.until(
                    EC.presence_of_element_located((By.ID, "loginbtn"))
                )

                driver.execute_script(
                    "arguments[0].click();",
                    login_btn
                )

                break

            except StaleElementReferenceException:

                print("\tRetry login because stale element")

                time.sleep(1)

            except TimeoutException:

                print("\tTimeout while locating login form")

                time.sleep(1)


def run_precondition_lv2(driver, username="admin", password="sandbox24", is_custom_loginfo=False):
    print("\nRun precondition...")
    driver.get(APP_CONFIG['base_url']['value'])

    wait = WebDriverWait(driver, 30)

    isLoggedIn = False
    try:
        driver.find_element(BY_MAPPING[LOCATORS['log_in']['by']], LOCATORS["log_in"]['value'])
        isLoggedIn = False

    except NoSuchElementException:
        isLoggedIn = True
    print(f"\tIs logged in: {isLoggedIn}")

    if isLoggedIn == True :
        print("\tAlready logged in, Log out to log in with admin account")
        driver.find_element(BY_MAPPING[LOCATORS['user_menu']['by']], LOCATORS["user_menu"]['value']).click()
        driver.find_element(BY_MAPPING[LOCATORS['log_out']['by']], LOCATORS["log_out"]['value']).click()
        driver.get(APP_CONFIG["base_url"]["value"])

    driver.find_element(BY_MAPPING[LOCATORS['log_in']['by']], LOCATORS["log_in"]['value']).click()
    for attempt in range(3):
        try:

            username_input = wait.until(
                EC.presence_of_element_located((BY_MAPPING[LOCATORS['log_in_username']['by']], LOCATORS["log_in_username"]['value']))
            )

            username_input.clear()
            username_input.send_keys("admin")

            password_input = wait.until(
                EC.presence_of_element_located((BY_MAPPING[LOCATORS['log_in_password']['by']], LOCATORS["log_in_password"]['value']))
            )

            password_input.clear()
            password_input.send_keys("sandbox24")

            login_btn = wait.until(
                EC.presence_of_element_located((BY_MAPPING[LOCATORS['login_btn']['by']], LOCATORS["login_btn"]['value']))
            )

            driver.execute_script(
                "arguments[0].click();",
                login_btn
            )

            break

        except StaleElementReferenceException:

            print("\tRetry login because stale element")

            time.sleep(1)

        except TimeoutException:

            print("\tTimeout while locating login form")

            time.sleep(1)

    driver.find_element(BY_MAPPING[LOCATORS['site_admin']['by']], LOCATORS["site_admin"]['value']).click()
    element = driver.find_element(BY_MAPPING[LOCATORS['site_security']['by']], LOCATORS["site_security"]['value'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(1)
    element.click()
    isChecked = driver.find_element(BY_MAPPING[LOCATORS['password_policy']['by']], LOCATORS["password_policy"]['value']).is_selected()
    print(f"\tPassword policy is selected: {isChecked}")

    if isChecked == True :
        print("\tPassword policy is selected, Uncheck it to run test cases")
        checkbox = driver.find_element(BY_MAPPING[LOCATORS['password_policy']['by']], LOCATORS["password_policy"]['value'])
        driver.execute_script("arguments[0].scrollIntoView();", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox)

        assert not driver.find_element(BY_MAPPING[LOCATORS['password_policy']['by']], LOCATORS["password_policy"]['value']).is_selected()

        save_btn = driver.find_element(BY_MAPPING[LOCATORS['save_site_security']['by']], LOCATORS["save_site_security"]['value'])
        driver.execute_script("arguments[0].scrollIntoView();", save_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_btn)

    if is_custom_loginfo:
        driver.find_element(BY_MAPPING[LOCATORS['user_menu']['by']], LOCATORS["user_menu"]['value']).click()
        driver.find_element(BY_MAPPING[LOCATORS['log_out']['by']], LOCATORS["log_out"]['value']).click()
        driver.get("https://sandbox51.moodledemo.net/")

        for attempt in range(3):
            try:

                username_input = wait.until(
                    EC.presence_of_element_located((BY_MAPPING[LOCATORS['log_in_username']['by']], LOCATORS["log_in_username"]['value']))
                )

                username_input.clear()
                username_input.send_keys(username)

                password_input = wait.until(
                    EC.presence_of_element_located((BY_MAPPING[LOCATORS['log_in_password']['by']], LOCATORS["log_in_password"]['value']))
                )

                password_input.clear()
                password_input.send_keys(password)

                login_btn = wait.until(
                    EC.presence_of_element_located((BY_MAPPING[LOCATORS['login_btn']['by']], LOCATORS["login_btn"]['value']))
                )

                driver.execute_script(
                    "arguments[0].click();",
                    login_btn
                )

                break

            except StaleElementReferenceException:

                print("\tRetry login because stale element")

                time.sleep(1)

            except TimeoutException:

                print("\tTimeout while locating login form")

                time.sleep(1)