from . import utils
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

def check(driver) -> bool:
    try:
        driver.find_element(by=By.CSS_SELECTOR, value='iframe[src*="geo.captcha-delivery.com"]')
        return True
    except NoSuchElementException as e:
        utils.warn('This page is not a idealista captcha')
        return False

def solve(driver):
    sleep(5)
    driver.switch_to.default_content()
    parent_frame = driver.find_element(by=By.TAG_NAME, value='iframe')
    driver.switch_to.frame(parent_frame)
    driver.switch_to.frame(driver.find_element(by=By.CSS_SELECTOR, value='iframe[title="reCAPTCHA"]'))
    captcha = driver.find_element(by=By.ID, value='recaptcha-anchor-label')
    sleep(5)
    captcha.click()
    sleep(5)

    driver.switch_to.default_content()
    while check(driver):
        __click_solve(driver, parent_frame)
        sleep(1.5)
        if check(driver):
            __click_solve(driver, parent_frame)
            sleep(5)
            if check(driver):
                __click_reload(driver, parent_frame)
                sleep(2.5)

def __click_solve(driver, parent_frame):

        driver.switch_to.default_content()
        driver.switch_to.frame(parent_frame)
        driver.switch_to.frame(driver.find_element(by=By.CSS_SELECTOR, value='iframe[title^="recaptcha challenge"]'))
        solver_buttons = driver.find_element(by=By.CSS_SELECTOR, value='div.button-holder.help-button-holder')
        sleep(5)
        solver_buttons.click()
        sleep(5)
        driver.switch_to.default_content()

def __click_reload(driver, parent_frame):

        driver.switch_to.default_content()
        driver.switch_to.frame(parent_frame)
        driver.switch_to.frame(driver.find_element(by=By.CSS_SELECTOR, value='iframe[title^="recaptcha challenge"]'))
        reload_button = driver.find_element(by=By.CSS_SELECTOR, value='#recaptcha-reload-button')
        sleep(5)
        reload_button.click()
        sleep(5)
        driver.switch_to.default_content()