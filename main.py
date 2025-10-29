import time
import logging
import threading
import os
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Get credentials strictly from environment variables (no hardcoded defaults)
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
UPDATE_INTERVAL = 60  # time in seconds on how often to update the page
WAIT_TIME = 30  # time in seconds to wait for target element to appear, if it doesn't appear, the function will return
SHOW_UI = False  # if True, the browser instance will be open. If False, it will be headless, which requires less cpu

# Global variables for server
app = Flask(__name__)
scheduler = BackgroundScheduler()
driver = None
driver_lock = threading.Lock()
last_run_time = None
last_run_status = "Not started"
run_count = 0

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance_server.log'),
        logging.StreamHandler()
    ]
)


def try_to_attend(selenium_driver):
    global last_run_status
    try:
        wait = WebDriverWait(selenium_driver, WAIT_TIME)
        page_source = selenium_driver.page_source
        if 'Нет доступных дисциплин' in page_source:
            last_run_status = "No available subjects"
            logging.info("No available subjects found")
            return

        button_divs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[span/span[@class='v-button-caption' and text()='Отметиться']]")
            )
        )

        attendance_count = 0
        for button_div in button_divs:
            if button_div is not None:
                button_div.click()
                attendance_count += 1
                time.sleep(1)
        
        last_run_status = f"Successfully attended {attendance_count} classes"
        logging.info(f"Successfully attended {attendance_count} classes")
        
    except TimeoutException:
        last_run_status = "Timeout waiting for attendance buttons"
        logging.warning("Timeout waiting for attendance buttons")
        return
    except Exception as e:
        last_run_status = f"Error: {str(e)}"
        logging.error(f"Error in try_to_attend: {str(e)}")
        return


def run_attendance_check():
    """Scheduled function to run attendance check every minute"""
    global driver, last_run_time, last_run_status, run_count
    
    with driver_lock:
        if driver is None:
            logging.error("Driver not initialized")
            last_run_status = "Driver not initialized"
            return
        
        try:
            run_count += 1
            last_run_time = datetime.now()
            logging.info(f"Starting attendance check #{run_count}")
            
            # Check if we need to login
            page_source = driver.page_source
            if 'Вход в систему' in page_source:
                logging.info("Login required, attempting to login")
                login(driver)
            
            # Run attendance check
            try_to_attend(driver)
            
            # Refresh page for next check
            driver.refresh()
            logging.info(f"Attendance check #{run_count} completed")
            
        except Exception as e:
            last_run_status = f"Critical error: {str(e)}"
            logging.error(f"Critical error in run_attendance_check: {str(e)}")
            # Try to reinitialize driver
            try:
                driver.quit()
            except:
                pass
            initialize_driver()


def login(selenium_driver):
    try:
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
        
        logging.info("Login attempt completed")
        
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        raise


def initialize_driver():
    """Initialize the Selenium WebDriver"""
    global driver
    try:
        options = webdriver.ChromeOptions()
        
        if not SHOW_UI:
            options.add_argument('--headless')
        
        # Additional options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://wsp.kbtu.kz/RegistrationOnline")
        logging.info("WebDriver initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {str(e)}")
        raise


# Flask routes
@app.route('/')
def home():
    """Home page with server status"""
    return jsonify({
        "status": "Attendance Server Running",
        "last_run_time": last_run_time.isoformat() if last_run_time else None,
        "last_run_status": last_run_status,
        "total_runs": run_count,
        "next_run": "Every minute"
    })

@app.route('/status')
def status():
    """Detailed status endpoint"""
    return jsonify({
        "server_status": "running",
        "scheduler_running": scheduler.running,
        "driver_initialized": driver is not None,
        "last_run_time": last_run_time.isoformat() if last_run_time else None,
        "last_run_status": last_run_status,
        "total_runs": run_count,
        "username_configured": bool(USERNAME),
        "password_configured": bool(PASSWORD)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/ping')
def ping():
    """Ping endpoint to keep server awake"""
    return jsonify({"status": "awake", "timestamp": datetime.now().isoformat()})

def start_server():
    """Start the Flask server and scheduler"""
    global driver
    
    try:
        # Validate credentials are provided via environment
        if not USERNAME or not PASSWORD:
            logging.error("Missing USERNAME or PASSWORD environment variables")
            raise RuntimeError("Set USERNAME and PASSWORD environment variables")
        # Initialize WebDriver
        logging.info("Initializing WebDriver...")
        initialize_driver()
        
        # Start scheduler
        logging.info("Starting scheduler...")
        scheduler.add_job(
            func=run_attendance_check,
            trigger=IntervalTrigger(seconds=60),  # Run every minute
            id='attendance_check',
            name='Attendance Check',
            replace_existing=True
        )
        scheduler.start()
        
        # Start Flask server
        logging.info("Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise
    finally:
        if scheduler.running:
            scheduler.shutdown()
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    start_server()
