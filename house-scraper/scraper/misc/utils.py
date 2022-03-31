"""
Miscellaneous utilities; including file utilities, 
selenium driver utilities, logging utilities and
internet utilities
"""
import logging
import os
import shutil
import uuid
from random import randint, random, uniform
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from . import config, network

# =========================================================
# FILE UTILITIES
# =========================================================


def delete_directory(dir_name: str):
    """
    Deletes the directory

    Parameters
    ----------
    dir_name : str
        Absolute path to the directory/folder
    """
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
        log(f'{dir_name} has been deleted')


def create_directory(dir_name: str):
    """
    Deletes the directory and creates it again

    Parameters
    ----------
    dir_name : str
        Absolute path to the directory/folder
    """
    delete_directory(dir_name)
    os.mkdir(dir_name)
    log(f'{dir_name} has been created')


def create_file(dir: str, file_name: str):
    """
    Creates a file in a directory and opens it for writing in UTF-8

    Parameters
    ----------
    dir : str
        Absolute path of the directory/folder
    file_name : str
        Name of the file

    Returns
    -------
    File handler ready to be written into
    """
    log(f'{os.path.join(dir, file_name)} created')
    return open(os.path.join(dir, file_name), 'w+', encoding='UTF8')


def duplicate_folder(dir: str, dest: str):
    """
    Copy-pastes a folder from dir to dest

    Parameters
    ----------
    dir : str
        Absolute folder path to duplicate
    dest : str
        Absolute folder path in which to paste the folder
    """
    shutil.copytree(dir, dest)
    log(f'{dir} has been copy-pasted to {dest}')


def directory_exists(dir_name: str) -> bool:
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


def file_exists(file_name: str) -> bool:
    """
    Checks if the file exists and if it is a file

    Parameters
    ----------
    file_name : str
        Absolute file path to check

    Returns
    -------
    True if the path exists and is a file
    """
    return os.path.exists(file_name) and os.path.isfile(file_name)


def get_directories(src_dir: str) -> list:
    """
    Gets all directories inside a given directory/folder

    Parameters
    ----------
    src_dir : str
        Absolute folder path to check

    Returns
    -------
    List of folders contained in src_dir
    """
    if directory_exists(src_dir):
        return [os.path.join(src_dir, file) for file in os.listdir(src_dir)
                if os.path.isdir(os.path.join(src_dir, file))]
    else:
        return []


def get_files_in_directory(dir_name: str, extension: str = '') -> list:
    """
    Gets all files ending in extension inside a given directory/folder

    Parameters
    ----------
    dir_name : str
        Absolute folder path to check
    extension : str, opt
        Extension of the file

    Returns
    -------
    List of files ending in extension contained in dir_name
    """
    log(f'Getting files ending with "{extension}" in {dir_name}')
    if directory_exists(dir_name):
        return [os.path.join(dir_name, file) for file in os.listdir(dir_name)
                if os.path.isfile(os.path.join(dir_name, file))
                and file.endswith(extension)]
    else:
        return []


# =========================================================
# INTERNET CAPABILITIES
# =========================================================

def get_http_code(url: str) -> int:
    """
    Gets the HTTP status code returned by querying a url

    Parameters
    ----------
    url : str
        URL to check

    Returns
    -------
    Status code of the response
    """
    try:
        r_headers = {'User-Agent': config.get_user_agent()}
        r = requests.get(url, headers=r_headers)
        return r.status_code
    except (requests.HTTPError, requests.ConnectionError) as e:
        error(f'Error trying to get status code for {url}: {e.msg}')


def download_image(url: str, img_file: str):
    """
    Downloads the image given in a url and saves it to img_file

    Parameters
    ----------
    url : str
        URL to check
    img_file : str
        Absolute path to the file the image is going to be saved at 
    """
    try:
        r_headers = {'User-Agent': network.get_user_agent()}
        r = requests.get(url, headers=r_headers)
        r.raise_for_status()
        with open(img_file, 'wb') as handler:
            handler.write(r.content)
    except Exception as e:
        warn(f'Error {r.status_code} trying to download image from {url}')


# =========================================================
# SELENIUM UTILITIES
# =========================================================

def set_human_options() -> Options:
    """
    Create the options for the selenium web driver. Makes it look like a human

    Returns
    -------
    An Options object for the driver
    """
    options = webdriver.ChromeOptions()
    options.add_extension(config.BUSTER)

    og_session = os.path.join(config.ROOT_DIR, config.CHROME_SESSION)
    session = og_session
    if directory_exists(og_session):
        dup_session = os.path.join(
            config.TMP_DIR, config.CHROME_SESSION, str(uuid.uuid4()))
        duplicate_folder(og_session, dup_session)
        session = dup_session
        # options.add_argument('--headless')
        log('The driver is not human')

    options.add_argument(f'user-data-dir={session}')
    options.add_argument('no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return options


def proxify():
    """
    Configures a proxy for a selenium web driver

    Returns
    -------
    The desired capabilities of the selenium driver
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


def get_selenium(use_proxy: bool = False):
    """
    Creates a new selenium web driver that looks like a human

    Parameters
    ----------
    use_proxy : bool, opt
        Flag to use a proxy or not. False by default

    Returns
    -------
    A selenium driver
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

def flip_coin() -> bool:
    """
    Throws a probability check to make stuff a bit more random

    Returns
    -------
    If the check was passed
    """
    return random() < config.CHANCE_MEGA_WAIT


def mega_wait():
    """
    Waits a lot of time
    """
    sleep(uniform(config.MEGA_MIN_WAIT, config.MEGA_MAX_WAIT))


def wait():
    """
    Waits a moderate ammount of time
    """
    sleep(uniform(config.RANDOM_MIN_WAIT, config.RANDOM_MAX_WAIT))


def mini_wait():
    """
    Waits a little bit of time
    """
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


def log(msg: str):
    """
    Logs an INFO message to the log
    """
    logging.info(msg)


def warn(msg: str):
    """
    Logs a WARN message to the log
    """
    logging.warn(msg)


def error(msg: str):
    """
    Logs an ERROR message to the log
    """
    logging.error(msg)
