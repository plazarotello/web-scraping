import logging
import os
import shutil
import uuid
from random import randint, uniform, random
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from . import config, network

# =========================================================
# FILE UTILITIES
# =========================================================

def delete_directory(dir_name : str):
    """
    Deletes the directory

    Parameters
    ----------
    dir_name : str
        Absolute path
    """
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
        log(f'{dir_name} has been deleted')

def create_directory(dir_name : str):
    """
    Deletes the directory and creates it again

    Parameters
    ----------
    dir_name : str
        Absolute path
    """
    delete_directory(dir_name)
    os.mkdir(dir_name)
    log(f'{dir_name} has been created')

def create_file(dir : str, file_name : str):
    """
    Creates a file in a directory and opens it for writing in UTF-8

    Parameters
    ----------
    dir : str
        Absolute path of the directory
    file_name : str
        Name of the file
    
    Returns
    -------
    File handler ready to be written into
    """
    log(f'{os.path.join(dir, file_name)} created')
    return open(os.path.join(dir, file_name), 'w+', encoding='UTF8')

def duplicate_folder(dir : str, dest : str):
    """
    Copy-pastes a folder

    Parameters
    ----------
    dir : str
        Absolute folder path to duplicate
    dest : str
        Absolute folder path in which to paste the folder
    """
    shutil.copytree(dir, dest)
    log(f'{dir} has been copy-pasted to {dest}')

def directory_exists(dir_name : str) -> bool:
    """
    Checks if the directory exists and if it is a directory

    Parameters
    ----------
    dir_name : str
        Absolute folder path to check
    
    Returns
    -------
    True if the path exists and is a folder
    """
    return os.path.exists(dir_name) and os.path.isdir(dir_name)

def file_exists(file_name : str) -> bool:
    return os.path.exists(file_name) and os.path.isfile(file_name)

def get_directories(src_dir : str) -> list:
    if directory_exists(src_dir):
        return [os.path.join(src_dir, file) for file in os.listdir(src_dir) 
            if os.path.isdir(os.path.join(src_dir, file))]
    else: return []

def get_files_in_directory(dir_name : str, extension : str = '') -> list:
    log(f'Getting files ending with "{extension}" in {dir_name}')
    if directory_exists(dir_name):
        return [os.path.join(dir_name, file) for file in os.listdir(dir_name) 
            if os.path.isfile(os.path.join(dir_name, file))
                and file.endswith(extension)]
    else: return []

# =========================================================
# INTERNET CAPABILITIES
# =========================================================

def get_http_code(url : str) -> int:
    try:
        r_headers = {'User-Agent': config.get_user_agent()}
        r = requests.get(url, headers=r_headers)
        return r.status_code
    except (requests.HTTPError, requests.ConnectionError) as e:
        error(f'Error trying to get status code for {url}: {e.msg}')

def download_image(url : str, img_file : str) -> bool:
    try:
        r_headers = {'User-Agent': network.get_user_agent()}
        r = requests.get(url, headers=r_headers)
        r.raise_for_status()
        with open(img_file, 'wb') as handler:
            handler.write(r.content)
    except Exception as e:
        warn(f'Error trying to download image from {url}')

# =========================================================
# SELENIUM UTILITIES
# =========================================================

def set_human_options() -> Options:
    """
    Create the options for the selenium web driver. Makes it look like a human
    """
    options = webdriver.ChromeOptions()
    options.add_extension(config.BUSTER)

    og_session = os.path.join(config.ROOT_DIR, config.CHROME_SESSION)
    session = og_session
    if directory_exists(og_session):
        dup_session = os.path.join(config.TMP_DIR, config.CHROME_SESSION, str(uuid.uuid4()))
        duplicate_folder(og_session, dup_session)
        session = dup_session
        # options.add_argument('--headless')
        log('The driver is not human')

    options.add_argument(f'user-data-dir={session}')
    options.add_argument('no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return options

# https://stackoverflow.com/a/40628176
def proxify():
    """
    Configures a proxy for a selenium web driver
    """
    available_proxies = network.get_proxies()
    selected = available_proxies[randint(0, len(available_proxies)-1)]
    
    capabilities = webdriver.DesiredCapabilities.CHROME
    capabilities['marionette'] = True
    capabilities['proxy'] = {
        'proxyType': 'MANUAL',
        'httpProxy': f'{selected["ip"]}:{selected["port"]}',
        'ftpProxy': f'{selected["ip"]}:{selected["port"]}',
        'sslProxy': f'{selected["ip"]}:{selected["port"]}'
    }
    log(f'Setting the driver`s proxy to {selected["ip"]}:{selected["port"]}')
    return capabilities

def get_selenium(use_proxy : bool = False):
    """
    Creates a new selenium web driver that looks like a human
    """
    log('Creating new driver')
    driver_path = os.path.join(config.ROOT_DIR, 'chromedriver.exe')
    driver = webdriver.Chrome(executable_path=driver_path, options=set_human_options(),
        desired_capabilities=proxify() if use_proxy else webdriver.DesiredCapabilities.CHROME)
    driver.implicitly_wait(15)
    return driver


# =========================================================
# WAITING UTILITIES
# =========================================================

"""
Utilities waiting a big chunk of time or only a small amount of it
Also includes a flipping coin to see if we have to wait a mega big
chunk of time
"""

def flip_coin() -> bool:
    return random() < config.CHANCE_MEGA_WAIT

def mega_wait():
    sleep(uniform(config.MEGA_MIN_WAIT, config.MEGA_MAX_WAIT))

def wait():
    sleep(uniform(config.RANDOM_MIN_WAIT, config.RANDOM_MAX_WAIT))

def mini_wait():
    sleep(uniform(config.RANDOM_SMALL_MIN_WAIT, config.RANDOM_SMALL_MAX_WAIT))


# =========================================================
# LOGGING UTILITIES
# =========================================================

"""
Starts a log file. The utilities log messages in the file with each correspondent
priority level
"""

# starts a log to file
logging.basicConfig(filename=os.path.join(config.ROOT_DIR, 'house-scraper.log'), 
    filemode='w', encoding='utf-8', level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def log(msg : str):
    logging.info(msg)

def warn(msg : str):
    logging.warn(msg)

def error(msg : str):
    logging.error(msg)
