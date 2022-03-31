"""
Deletes the web driver's user data if needed and starts a selenium web driver to
manually get to each to-be-scraped page. The user must fill in the CAPTCHA.
"""

import os
from time import sleep

from misc import captcha_solver, config, utils

if __name__ == '__main__':
    utils.delete_directory(os.path.join(
        config.ROOT_DIR, config.CHROME_SESSION))

    with utils.get_selenium() as driver:
        driver.get(config.IDEALISTA_URL)
        captcha_solver.solve(driver)
        sleep(30*5)
