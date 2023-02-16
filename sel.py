import random
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


def load_driver() -> WebDriver:
    """Returns a new Firefox Selenium driver."""
    options = Options()
    options.headless = True

    return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)


def load_page(
    driver: WebDriver, url: str, awaited_element: str, timeout: int = 10, retries: int = 5
) -> str:
    """Uses Selenium to load the page, wait until the awaited element shows up, and return the page
    source.

    Provides a simple backoff strategy using `timeout` and `retries`.
    """
    print("hitting:", url, file=sys.stderr)

    wait = WebDriverWait(driver, timeout=timeout)
    retried = 0

    while True:
        try:
            driver.get(url)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, awaited_element)))

            time.sleep(random.random() * 2 + 1)  # give the server a break
            break
        except TimeoutException:
            if retried >= retries:
                print(f"timed out! giving up")
                raise

            to_sleep = 15 * (retried + 1)
            print(f"timed out! retrying in {to_sleep}s", file=sys.stderr)
            time.sleep(to_sleep)
            retried += 1

    return driver.page_source
