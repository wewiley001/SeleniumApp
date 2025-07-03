# functions.py
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def open_url(driver, url):
    """driver.get(url)"""
    driver.get(url)

def get_current_url(driver):
    """Retrieve the current browser URL"""
    return driver.current_url

def get_title(driver):
    """Retrieve the current page title"""
    return driver.title

def back(driver):
    driver.back()

def forward(driver):
    driver.forward()

def refresh(driver):
    driver.refresh()

def maximize_window(driver):
    driver.maximize_window()

def minimize_window(driver):
    driver.minimize_window()

def implicit_wait(driver, seconds):
    driver.implicitly_wait(float(seconds))

def explicit_wait(driver, css_selector, timeout):
    WebDriverWait(driver, float(timeout)).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )

def click_by_id(driver, element_id):
    driver.find_element(By.ID, element_id).click()

def click_by_name(driver, name):
    driver.find_element(By.NAME, name).click()

def click_by_xpath(driver, xpath):
    driver.find_element(By.XPATH, xpath).click()

def click_by_css(driver, css):
    driver.find_element(By.CSS_SELECTOR, css).click()

def click_by_link_text(driver, text):
    driver.find_element(By.LINK_TEXT, text).click()

def fill_by_id(driver, element_id, text):
    el = driver.find_element(By.ID, element_id)
    el.clear()
    el.send_keys(text)

def fill_by_name(driver, name, text):
    el = driver.find_element(By.NAME, name)
    el.clear()
    el.send_keys(text)

def fill_by_xpath(driver, xpath, text):
    el = driver.find_element(By.XPATH, xpath)
    el.clear()
    el.send_keys(text)

def fill_by_css(driver, css, text):
    el = driver.find_element(By.CSS_SELECTOR, css)
    el.clear()
    el.send_keys(text)

def submit_by_id(driver, element_id):
    driver.find_element(By.ID, element_id).submit()

def submit_by_xpath(driver, xpath):
    driver.find_element(By.XPATH, xpath).submit()

def select_by_name(driver, name, value):
    Select(driver.find_element(By.NAME, name)).select_by_value(value)

def send_keys_action(driver, keys_sequence):
    driver.switch_to.active_element.send_keys(keys_sequence)

def switch_to_frame_by_name(driver, frame_name):
    driver.switch_to.frame(frame_name)

def switch_to_default_content(driver):
    driver.switch_to.default_content()

def switch_to_parent_frame(driver):
    driver.switch_to.parent_frame()

def switch_to_window(driver, handle_or_name):
    driver.switch_to.window(handle_or_name)

def accept_alert(driver):
    driver.switch_to.alert.accept()

def dismiss_alert(driver):
    driver.switch_to.alert.dismiss()

def get_alert_text(driver):
    return driver.switch_to.alert.text

def wait_seconds(driver, seconds):
    time.sleep(float(seconds))

def close_browser(driver):
    driver.quit()
