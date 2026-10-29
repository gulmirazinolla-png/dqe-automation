import time
import os
from pathlib import Path

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "report.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
WAIT = 15


class SeleniumWebDriverContextManager:
    """Starts Chrome on enter and always closes it on exit."""

    def __init__(self):
        self.driver = None

    def __enter__(self) -> WebDriver:
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
        if exc_type:
            print(f"Error: {exc_type.__name__}: {exc_value}")
        return False  # don't swallow the exception


# ---------------- TABLE ----------------
def extract_table(driver: WebDriver):
    try:
        # Locator 1: CLASS_NAME
        WebDriverWait(driver, WAIT).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table"))
        )
        table = driver.find_element(By.CLASS_NAME, "table")

        # Locator 2: CSS_SELECTOR
        columns = table.find_elements(By.CSS_SELECTOR, ".y-column")
        if not columns:
            raise NoSuchElementException("No columns found in the table")

        data = {}
        for col in columns:
            # Locator 3: ID
            header = col.find_element(By.ID, "header").text.strip()
            # Locator 4: XPATH
            cells = col.find_elements(By.XPATH, ".//*[contains(@class,'cell-text')]")
            data[header] = [c.text.strip() for c in cells if c.text.strip() != header]

        df = pd.DataFrame(data)
        df = df.drop_duplicates().reset_index(drop=True)  # Plotly renders each row twice

        path = os.path.join(OUTPUT_DIR, "table.csv")
        df.to_csv(path, index=False)
        print(f"Saved {path}: {len(df)} rows")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Table extraction failed: {e}")
        raise


# ---------------- DOUGHNUT ----------------
def read_doughnut(driver: WebDriver):
    doughnut = driver.find_element(By.CLASS_NAME, "pielayer")
    labels = doughnut.find_elements(By.CSS_SELECTOR, "text.slicetext[data-notex='1']")
    rows = []
    for label in labels:
        tspans = label.find_elements(By.TAG_NAME, "tspan")
        if len(tspans) >= 2:
            rows.append((tspans[0].text.strip(), tspans[1].text.strip()))
    return rows


def save_state(driver: WebDriver, index: int):
    time.sleep(1)  # let the chart finish animating
    chart = driver.find_element(By.CLASS_NAME, "pielayer")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chart)
    time.sleep(0.5)

    driver.save_screenshot(os.path.join(OUTPUT_DIR, f"screenshot{index}.png"))

    rows = read_doughnut(driver)  # empty when every filter is off
    df = pd.DataFrame(rows, columns=["Facility Type", "Min Average Time Spent"])
    df.to_csv(os.path.join(OUTPUT_DIR, f"doughnut{index}.csv"), index=False)
    print(f"State {index}: {len(rows)} slices")


def legend_items(driver: WebDriver):
    legend = driver.find_element(By.CLASS_NAME, "scrollbox")
    return legend.find_elements(By.CLASS_NAME, "traces")


def hide_notifier(driver: WebDriver):
    """Plotly shows a toast popup over the legend after a click; hide it."""
    driver.execute_script(
        "document.querySelectorAll('.plotly-notifier').forEach(e => e.style.display = 'none');"
    )


def click_legend(driver: WebDriver, position: int):
    # Plotly redraws the legend after each click, so re-find the element every time
    for _ in range(3):
        try:
            hide_notifier(driver)
            legend_items(driver)[position].click()
            return
        except (StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(0.5)
    raise RuntimeError(f"Could not click legend item {position}")


def process_doughnut(driver: WebDriver):
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pielayer"))
        )
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scrollbox"))
        )
    except TimeoutException:
        print("Doughnut chart did not load")
        raise

    count = len(legend_items(driver))
    print(f"Legend items: {count}")

    index = 0
    save_state(driver, index)  # initial, unfiltered state

    for pos in range(count):  # each click hides one more slice
        try:
            click_legend(driver, pos)
            index += 1  # only count states that were really applied
            save_state(driver, index)  # last state = all filters off (edge case)
        except Exception as e:
            print(f"Filter {pos} failed: {e}")


if __name__ == "__main__":
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError(f"Report not found: {REPORT_PATH}")

    with SeleniumWebDriverContextManager() as driver:
        driver.get(Path(REPORT_PATH).as_uri())
        extract_table(driver)
        process_doughnut(driver)