"""
Checks if a page has a captcha and tries to solve the captcha with
the help of the Buster extension.
"""

from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from . import utils


def check(driver) -> bool:
    """
    Checks if the driver is currently on a captcha page

    Parameters
    ----------
    driver : WebElement
        Selenium driver, in the root content

    Returns
    -------
    True if the driver is on a captcha page, False otherwise
    """
    try:
        driver.find_element(by=By.CSS_SELECTOR,
                            value='iframe[src*="geo.captcha-delivery.com"]')
        return True
    except NoSuchElementException as e:
        utils.warn('This page is not a idealista captcha')
        return False
    except Exception as e:
        utils.error(f'There was an unexpected error: {e}')


def solve(driver):
    """
    Tries to solve the captcha in the driver's current page content

    Parameters
    ----------
    driver : WebElement
        Selenium driver, in the root content
    """
    try:
        sleep(5)
        driver.switch_to.default_content()
        parent_frame = driver.find_element(by=By.TAG_NAME, value='iframe')
        driver.switch_to.frame(parent_frame)
        driver.switch_to.frame(driver.find_element(
            by=By.CSS_SELECTOR, value='iframe[title="reCAPTCHA"]'))
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
    except Exception as e:
        utils.warn(f'There was an unexpected error: {e}')
        return


def __click_solve(driver, parent_frame):
    """
    Auxiliary function to the captcha solver. Tries to click the
    Buster extension solver button

    Parameters
    ----------
    driver : WebElement
        Selenium driver in the root content
    parent_frame : frame
        "I'm not a robot" frame
    """
    driver.switch_to.default_content()
    driver.switch_to.frame(parent_frame)
    driver.switch_to.frame(driver.find_element(
        by=By.CSS_SELECTOR, value='iframe[title^="recaptcha challenge"]'))
    solver_buttons = driver.find_element(
        by=By.CSS_SELECTOR, value='div.button-holder.help-button-holder')
    sleep(5)
    solver_buttons.click()
    sleep(5)
    driver.switch_to.default_content()


def __click_reload(driver, parent_frame):
    """
    Auxiliary function to the captcha solver. Tries to reload the
    Buster extension solver button

    Parameters
    ----------
    driver : WebElement
        Selenium driver in the root content
    parent_frame : frame
        "I'm not a robot" frame
    """
    driver.switch_to.default_content()
    driver.switch_to.frame(parent_frame)
    driver.switch_to.frame(driver.find_element(
        by=By.CSS_SELECTOR, value='iframe[title^="recaptcha challenge"]'))
    reload_button = driver.find_element(
        by=By.CSS_SELECTOR, value='#recaptcha-reload-button')
    sleep(5)
    reload_button.click()
    sleep(5)
    driver.switch_to.default_content()
