import os
import time
from datetime import datetime
from threading import Thread

from flask import Flask
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Credentials: set in main.py or via env vars USERNAME and PASSWORD (env preferred on server)
USERNAME = os.environ.get("USERNAME", "")
PASSWORD = os.environ.get("PASSWORD", "")
UPDATE_INTERVAL = 60  # time in seconds on how often to update the page
WAIT_TIME = 10  # time in seconds to wait for target element to appear
SHOW_UI = os.environ.get("SHOW_UI", "false").lower() == "true"  # headless on server by default

# Status for the status page (updated by the attendance loop)
status = {
    "running": False,
    "last_check": None,
    "last_result": "Not run yet",
    "error": None,
    "total_checks": 0,
    "total_attended": 0,
}


def try_to_attend(selenium_driver):
    """Returns number of attendance buttons clicked (0 if none or error)."""
    wait = WebDriverWait(selenium_driver, WAIT_TIME)
    page_source = selenium_driver.page_source
    if "Нет доступных дисциплин" in page_source:
        return 0

    try:
        button_divs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[span/span[@class='v-button-caption' and text()='Отметиться']]")
            )
        )
        count = 0
        for button_div in button_divs:
            if button_div is not None:
                button_div.click()
                count += 1
                time.sleep(1)
        return count
    except TimeoutException:
        return 0
    except Exception as e:
        print(e)
        return try_to_attend(selenium_driver)


def run_attendance_loop(driver):
    """Runs in a background thread; updates global status."""
    global status
    status["running"] = True
    status["error"] = None
    try:
        driver.get("https://wsp.kbtu.kz/RegistrationOnline")
        while True:
            time.sleep(1)
            page_source = driver.page_source
            if "Вход в систему" in page_source:
                login(driver)
                time.sleep(2)

            count = try_to_attend(driver)
            status["last_check"] = datetime.utcnow().isoformat() + "Z"
            status["total_checks"] += 1
            if count > 0:
                status["total_attended"] += count
                status["last_result"] = f"Attended {count} class(es)"
            else:
                status["last_result"] = "No attendance available (or no button found)"
            print(f"[{status['last_check']}] {status['last_result']} (total attended so far: {status['total_attended']})")

            time.sleep(UPDATE_INTERVAL)
            driver.refresh()
    except Exception as e:
        status["running"] = False
        status["error"] = str(e)
        status["last_result"] = f"Error: {str(e)}"
        print(f"Error: {e}")
    finally:
        status["running"] = False
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def login(selenium_driver):
    wait = WebDriverWait(selenium_driver, WAIT_TIME)

    username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
    if username_input is not None:
        username_input.clear()
        username_input.send_keys(USERNAME)

    time.sleep(1)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
    if password_input is not None:
        password_input.send_keys(PASSWORD)

    checkbox = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//input[@type="checkbox"]')
        )
    )
    parent_element = selenium_driver.execute_script("return arguments[0].parentElement;", checkbox)
    if parent_element is not None:
        parent_element.click()

    submit_button = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@role="button" and contains(@class, "v-button-primary")]')
        )
    )
    if submit_button is not None:
        submit_button.click()


app = Flask(__name__)


@app.route("/")
def index():
    """Status page: is it running, last result, total attended."""
    s = status
    running_text = "Yes" if s["running"] else "No"
    return (
        f"<h1>Auto-attend status</h1>"
        f"<p><b>Running:</b> {running_text}</p>"
        f"<p><b>Last check:</b> {s['last_check'] or '—'}</p>"
        f"<p><b>Last result:</b> {s['last_result']}</p>"
        f"<p><b>Total checks:</b> {s['total_checks']}</p>"
        f"<p><b>Total attended (all time):</b> {s['total_attended']}</p>"
        f"<p><b>Error:</b> {s['error'] or '—'}</p>"
    )


@app.route("/health")
def health():
    """For Render health checks."""
    return {"ok": True}, 200


@app.route("/status")
def status_json():
    """JSON status for scripts."""
    return status


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        print("Set USERNAME and PASSWORD in main.py or environment (e.g. export USERNAME=... PASSWORD=...)")
        exit(1)

    options = webdriver.ChromeOptions()
    if not SHOW_UI:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    thread = Thread(target=run_attendance_loop, args=(driver,), daemon=True)
    thread.start()

    port = int(os.environ.get("PORT", 5000))
    print(f"Status server on http://0.0.0.0:{port} — attendance loop running in background")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
