import subprocess
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

PAGE_TIMEOUT = 10
DEBUG = True # when set to true alarm will set off after 2 retries for testing

def get_driver():
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def _check_login_status(driver):
        if "Successfully logged in" in driver.page_source:
            return "success"
        elif "Invalid login name or password" in driver.page_source:
            return "failure"
        return 'unexpected'

def login(driver):    
    url = 'https://www.supersaas.co.uk/schedule/login/Greek_Embassy_London/Military'
    driver.get(url)
    
    # Wait for the email field to be present
    WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, 'name'))
    )

    # Locate and input email
    email_field = driver.find_element(By.ID, 'name')
    email_field.send_keys(input('Email: '))

    # Locate and input password
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(input('Password: '))

    # Locate and click login button
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()

    # Wait for login result
    login_result = WebDriverWait(driver, PAGE_TIMEOUT).until(_check_login_status)
    
    if login_result == 'unexpected':
        raise IndexError('Unexpred result from login page')
    elif login_result == 'failure':
        print('Invalid login name or password, please try again.')
        login(driver)
        
def has_available_appointment(driver):
    url = 'https://www.supersaas.co.uk/schedule/Greek_Embassy_London/Military'
    driver.get(url)
    WebDriverWait(driver, PAGE_TIMEOUT).until(EC.title_contains("Greek Consulate in London-Appointments for Military"))
    if 'No available space found' in driver.page_source:
        return False
    return True


def login_and_monitor():
    count = 0
    try:
        driver = get_driver()
        login(driver)
        while not has_available_appointment(driver) and (not DEBUG or count < 2) :
            print(f"({count}): No appointments available")
            count += 1
            time.sleep(5)
        print(f"Found an appointment, elapsed time: {count*5} seconds")
        alarm()
    finally:
        driver.quit()

def alarm():
    while True:
        audio_file = "alarm.mp3"
        subprocess.call(["afplay", audio_file])

if __name__ == "__main__":
    try:
        login_and_monitor()
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.\n")
        sys.exit(0)

