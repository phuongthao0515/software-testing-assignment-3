import time

from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()

try:

    print("Opening browser...")

    # Login
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

    print("Opening calendar...")

    driver.get(
        "https://sandbox.moodledemo.net/calendar/view.php?view=month"
    )

    time.sleep(2)

    print("Opening new event modal...")

    driver.find_element(
        By.XPATH,
        "//button[contains(., 'New event')]"
    ).click()

    time.sleep(2)

    print("Fill title...")

    driver.find_element(
        By.ID,
        "id_name"
    ).send_keys("TEST_JS")

    time.sleep(1)

    print("Trigger form submit using JS...")

    # IMPORTANT:
    # Submit the actual form, not the button
    driver.execute_script("""
        document.querySelector('form').requestSubmit();
    """)

    print("Waiting redirect...")

    time.sleep(5)

    print("Checking result...")

    page = driver.page_source

    if "TEST_JS" in page:

        print("SUCCESS!")
        print("JS submit works.")

    else:

        print("FAILED!")
        print("Event not found.")

        with open(
            "debug_js_submit.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(page)

        print("Saved debug_js_submit.html")


finally:

    input("\nPress Enter to close browser...")

    driver.quit()