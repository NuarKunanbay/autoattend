from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


USERNAME = "a_zhetpisbaev@kbtu.kz"
PASSWORD = "ta(hiQW&"

def try_to_attend(driver):
    wait = WebDriverWait(driver, 10)
    page_source = driver.page_source
    if 'Нет доступных дисциплин' in page_source:
        return

    try:
        button_divs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[span/span[@class='v-button-caption' and text()='Отметиться']]")
            )
        )

        for button_div in button_divs:
            if button_div is not None:
                button_div.click()
                time.sleep(1)
    except Exception as e:
        print(e)
        try_to_attend(driver)


def main(driver):
    driver.get("https://wsp.kbtu.kz/RegistrationOnline")

    while True:
        time.sleep(1)
        page_source = driver.page_source
        # table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        if 'Вход в систему' in page_source:
            login(driver)

        try_to_attend(driver)
        time.sleep(60)
        driver.refresh()


def login(driver):
    wait = WebDriverWait(driver, 10)

    username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
    if username_input is not None:
        username_input.clear()
        username_input.send_keys(USERNAME)

    time.sleep(1)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
    if password_input is not None:
        password_input.send_keys(PASSWORD)

    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="checkbox"]')))
    parent_element = driver.execute_script("return arguments[0].parentElement;", checkbox)
    if parent_element is not None:
        parent_element.click()

    submit_button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="button" and contains(@class, "v-button-primary")]')))
    if submit_button is not None:
        submit_button.click()


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        main(driver)
    except Exception as e:
        print(e)
    finally:
        driver.quit()