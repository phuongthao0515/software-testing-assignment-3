import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


# ---------------------------
# Login function (hardcoded - Level 1)
# ---------------------------
def login(driver):

    driver.get(
        "https://sandbox.moodledemo.net/login/index.php"
    )

    driver.find_element(
        By.ID,
        "username"
    ).send_keys("admin")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("sandbox24")

    driver.find_element(
        By.ID,
        "loginbtn"
    ).click()

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
        driver.get(
            "https://sandbox.moodledemo.net/calendar/view.php?view=month"
        )

        # time.sleep(10)

        # ---------------------------
        # Step 3: Click "New event"
        # ---------------------------
        driver.find_element(
            By.XPATH,
            "//button[contains(., 'New event')]"
        ).click()

        time.sleep(5)

        # ---------------------------
        # Step 4: Fill Title
        # ---------------------------
        if title != "nan":

            driver.find_element(
                By.ID,
                "id_name"
            ).send_keys(title)

        time.sleep(10)
        # ---------------------------
        # Step 5: Fill Duration (if any)
        # ---------------------------
        if pd.notna(duration):

            # Select "Duration in minutes"
            driver.find_element(
                By.ID,
                "id_duration_2"
            ).click()

            time.sleep(5)

            driver.find_element(
                By.ID,
                "id_timedurationminutes"
            ).clear()

            driver.find_element(
                By.ID,
                "id_timedurationminutes"
            ).send_keys(str(duration))

        # ---------------------------
        # Step 6: Fill Repeat (if any)
        # ---------------------------
        if pd.notna(repeat):

            # show more
            driver.find_element(
                By.XPATH,
                "//a[contains(.,'Show more')]"
            ).click()

            time.sleep(5)

            # enable repeat
            driver.find_element(
                By.ID,
                "id_repeat"
            ).click()

            time.sleep(5)

            repeat_input = driver.find_element(
                By.ID,
                "id_repeats"
            )

            repeat_input.clear()

            repeat_input.send_keys(
                str(repeat)
            )
            time.sleep(5)

        # ---------------------------
        # Step 7: Click Save
        # ---------------------------
        driver.find_element(
            By.XPATH,
            "//button[contains(., 'Save')]"
        ).click()
        

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


print("\nAll Level 1 testcases completed.")