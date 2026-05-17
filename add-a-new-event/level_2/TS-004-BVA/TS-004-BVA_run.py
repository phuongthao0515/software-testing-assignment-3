import pandas as pd
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By



with open("../../config/app.json", "r") as f:
    config = json.load(f)

# ---------------------------
# Helper function to get locator
# ---------------------------
def get_locator(locator_key):
    locator = config["locators"][locator_key]
    by_type = getattr(By, locator["by"])
    return by_type, locator["value"]

# ---------------------------
# Login function (configurable - Level 2)
# ---------------------------
def login(driver):

    driver.get(config["urls"]["login"])

    by, value = get_locator("username_input")
    driver.find_element(by, value).send_keys(
        config["credentials"]["username"]
    )

    by, value = get_locator("password_input")
    driver.find_element(by, value).send_keys(
        config["credentials"]["password"]
    )

    by, value = get_locator("login_button")
    driver.find_element(by, value).click()

    time.sleep(2)

# ---------------------------
# Load test data
# ---------------------------
data = pd.read_csv("TS-004-BVA_data.csv")


# ---------------------------
# Execute test cases
# ---------------------------
for index, row in data.iterrows():

    driver = webdriver.Chrome()

    try:

        tc_id = row["tc_id"]
        title = str(row["title"])
        duration = row["duration"]
        repeat = row["repeat"]
        expected_type = row["expected_type"]
        expected_value = str(row["expected_value"])

        print("\nRunning:", tc_id)



        # ---------------------------
        # Step 1: Login
        # ---------------------------
        login(driver)

        # ---------------------------
        # Step 2: Open Calendar
        # ---------------------------
        driver.get(config["urls"]["calendar"])

        # time.sleep(10)

        # ---------------------------
        # Step 3: Click "New event"
        # ---------------------------
        by, value = get_locator("new_event_button")
        driver.find_element(by, value).click()

        time.sleep(5)

        # ---------------------------
        # Step 4: Fill Title
        # ---------------------------
        if title != "nan":

            by, value = get_locator("title_input")
            driver.find_element(by, value).send_keys(title)

        time.sleep(10)
        # ---------------------------
        # Step 5: Fill Duration (if any)
        # ---------------------------
        if pd.notna(duration):

            # Select "Duration in minutes"
            by, value = get_locator("duration_radio")
            driver.find_element(by, value).click()

            time.sleep(5)

            by, value = get_locator("duration_minutes_input")
            driver.find_element(by, value).clear()

            driver.find_element(by, value).send_keys(str(duration))

        # ---------------------------
        # Step 6: Fill Repeat (if any)
        # ---------------------------
        if pd.notna(repeat):

            # show more
            by, value = get_locator("show_more_link")
            driver.find_element(by, value).click()

            time.sleep(5)

            # enable repeat
            by, value = get_locator("repeat_checkbox")
            driver.find_element(by, value).click()

            time.sleep(5)

            by, value = get_locator("repeat_input")
            repeat_input = driver.find_element(by, value)

            repeat_input.clear()

            repeat_input.send_keys(str(repeat))
            time.sleep(5)

        # ---------------------------
        # Step 7: Click Save
        # ---------------------------
        by, value = get_locator("save_button")
        driver.find_element(by, value).click()
        

        time.sleep(10)

        page_source = driver.page_source

        # ---------------------------
        # Step 8: Verification
        # ---------------------------
        if expected_type == "error_text":

            assert expected_value in page_source

        elif expected_type == "event_created":

            assert expected_value in page_source

        else:
            raise Exception("Unknown expected_type")

        print(tc_id, "PASS")

    except Exception as e:

        print(tc_id, "FAIL")
        print("Reason:", e)

    finally:

        driver.quit()


print("\nAll Level 2 testcases completed.")