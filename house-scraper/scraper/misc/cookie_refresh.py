import pickle
from . import utils
from . import config
from time import sleep
import os

def refresh_idealista():
    with utils.get_selenium() as driver:

        # idealista cookies
        driver.get(config.IDEALISTA_URL)
        sleep(10*3) # enough to get to the real page
        cookies = driver.get_cookies()
        cookie = [_cookie for _cookie in cookies if _cookie['domain'] == '.idealista.com']
        pickle.dump(cookie, open(os.path.join(config.ROOT_DIR, config.IDEALISTA_COOKIE), 'wb'))
