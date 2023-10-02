import argparse
import subprocess
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

PAGE_TIMEOUT = 10
DEBUG = True  # when set to true alarm will set off after 3 retries for testing
LOGIN_PAGE = "https://www.supersaas.co.uk/schedule/login/Greek_Embassy_London/Military"
APPOINTMENTS_URL = "https://www.supersaas.co.uk/schedule/Greek_Embassy_London/Military"


def get_driver():
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _is_logged_in(driver):
    if "Invalid login name or password" in driver.page_source:
        return "failure"
    elif "Successfully logged in" in driver.page_source:
        return "success"


def login(driver, email, password):
    driver.get(LOGIN_PAGE)

    # Locate and input email
    email_field = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "name"))
    )
    email_field.send_keys(email)

    # Locate and input password
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    # Locate and click login button
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()

    if not WebDriverWait(driver, PAGE_TIMEOUT).until(_is_logged_in) == "success":
        raise ValueError("Invalid login name or password")
    print("\033[32mSuccessfully logged in.\033[0m")


def has_available_appointment(driver):
    driver.get(APPOINTMENTS_URL)
    WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.title_contains("Greek Consulate in London-Appointments for Military")
    )
    if "No available space found" in driver.page_source:
        return False
    return True


def login_and_monitor(email, password):
    count = 0
    start_time = datetime.now()
    try:
        driver = get_driver()
        login(driver, email, password)
        while not has_available_appointment(driver) and (not DEBUG or count < 3):
            print(
                f"\r\033[38;5;202mCheck Count ({count}): No appointments available\033[0m",
                end="",
                flush=True,
            )
            count += 1
            time.sleep(5)  # Note: This will sleep for 5 seconds, not 5 minutes
        print(
            f"\n\033[32mFound an appointment, elapsed time: {(datetime.now() - start_time).total_seconds()} seconds\033[0m"
        )
        alarm()
    finally:
        driver.quit()


def alarm():
    while True:
        audio_file = "alarm.mp3"
        subprocess.call(["afplay", audio_file])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embassy Appointment Alarm Script")
    parser.add_argument("--email", required=True, help="Your email address")
    parser.add_argument("--password", required=True, help="Your password")
    args = parser.parse_args()

    try:
        login_and_monitor(args.email, args.password)
    except ValueError:
        sys.stderr.write(
            "\033[31mLogin error: Invalid login name or password, see README for more details on how to register.\033[0m\n"
        )
    except TimeoutError:
        sys.stderr.write(
            "\033[31mTimeout error: The page took too long to load or the title wasn't updated in time.\033[0m\n"
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.\n")
        sys.exit(0)
